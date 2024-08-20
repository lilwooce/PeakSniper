from discord.ext import commands
import os
import requests
import discord 
import random
from dotenv import load_dotenv
from asyncio import gather
import asyncio
from .Config import hasAccount
from classes import User, Servers, database
import io
import asyncio
from discord import app_commands, File
from sqlalchemy import update
from sqlalchemy.orm import sessionmaker
from classes.database import engine
import random

load_dotenv()
updateUser = os.getenv('UPDATE_USER')
addUser = os.getenv('ADD_USER')
getUser = os.getenv('GET_USER')

class Gamba(commands.Cog, name="Gamba"):
    def __init__(self, client: commands.Bot):
        self.minCoinBid = 5
        self.cfMulti = 2
        self.client = client
        

    @commands.command(aliases=['cf'], description="This is a simple game where the user selects between heads or tails. You double your wager each time you win. It's simple yet addictive, side bets are always welcome!")
    async def coinflip(self, ctx, bet, amount: int):
        heads = ["heads", "head", "h"]
        tails = ["tails", "tail", "t"]
        author = ctx.author
        Session = sessionmaker(bind=database.engine)
        session = Session()
        u = session.query(User.User).filter_by(user_id=author.id).first()
        bal = u.balance
        c = self.client.get_channel(773916648317911140)

        if(amount > int(bal)):
            await ctx.send("You are too poor to afford this bet. Check your balance before betting next time.")
            return
        if (amount < self.minCoinBid):
            await ctx.send("Bet more money you poor fuck. The minimum bet is 5 discoins.")
            return
        if((bet.lower() not in heads) and (bet.lower() not in tails)):
            await ctx.send("Please type heads or tails")
            return

        result = random.randint(0,1)
        if (result == 0 and bet.lower() in heads):
            total = amount * self.cfMulti
            won = total - amount
            u.total_earned += won
            u.balance += won
            await ctx.send(f"Congrats!!! You won {int(won)} discoins")
        elif (result == 1 and bet.lower() in tails):
            total = amount * self.cfMulti
            won = total - amount
            u.total_earned += won
            u.balance += won
            await ctx.send(f"Congrats!!! You won {int(won)} discoins")
        else:
            u.balance -= amount
            u.total_lost += amount
            await ctx.send(f"You lost. lol. -{amount} discoins")

        u.total_bets += 1
        session.commit()
        session.close()
                    
            

    @commands.command(description="Lottery style betting functionality, allowing players that have earned coins to pick a number and bet a certain amount to win even more coins. This function is part of our gaming pivot, allowing for more currency based functions.")
    async def bet(self, ctx, bet: int, amount: int):
        author = ctx.author
        Session = sessionmaker(bind=database.engine)
        session = Session()
        u = session.query(User.User).filter_by(user_id=author.id).first()
        bal = u.balance

        if (amount > bal):
            await ctx.send("You are too poor to afford this bet. Check your balance before betting next time.")
            return
        if(bet < 1 and bet > 100):
            await ctx.send("Please choose a number between 1 and 100 for your bet. Including 1 and 100.")
            return

        result = random.randint(1,100)
        if (result == bet):
            won = amount * 100
            u.balance += won
            u.total_earned += won
            u.total_bets += 1
            await ctx.send(f"Congrats!!! You won {int(won)} discoins")
        else:
            u.balance -= amount
            u.total_lost += amount
            u.total_bets += 1
            await ctx.send(f"You lost. You chose **{bet}** but the bot chose **{result}**. Better luck next time.")
            
        session.commit()
        session.close()

    @commands.hybrid_command()
    async def setpollgamba(self, ctx, amount: int):
        amount = int(amount)
        author = ctx.author
        Session = sessionmaker(bind=database.engine)
        session = Session()
        u = session.query(User.User).filter_by(user_id=author.id).first()

        if u.poll_gamba > 0:
            u.balance += u.poll_gamba
            u.poll_gamba = 0
        if not amount:
            await ctx.send("Please set an amount for your next poll gamble")
            return
        if amount > u.balance:
            await ctx.send("You are too poor")
            return
        if amount <= 0:
            await ctx.send("Please bet more than 0")
            return
        
        #set the amount in the database
        u.poll_gamba = amount
        u.balance -= amount
        await ctx.send(f"You have set the amount for your next poll gamble to **{amount}**")
        session.commit()
        session.close()

    @commands.hybrid_command()
    async def payout(self, ctx, poll: discord.Message, correct_answer: str):
        # Check if the poll is finalized
        p = poll.poll
        poll_creator = poll.author.id
        if ctx.author.id !=poll_creator:
            await ctx.send("You do not have the right")
            return
        
        # Prepare to query the database
        Session = sessionmaker(bind=database.engine)
        session = Session()
        embed = discord.Embed(title="Payout Results")
        
        # Initialize totals
        total_bet = 0
        total_winners = 0
        total_losers = 0
        winners = []
        losers = []
        
        # Fetch all users in one go to reduce database queries
        user_ids = set()
        for answer in p.answers:
            async for voter in answer.voters():
                user_ids.add(voter.id)
                if answer.text.lower() == correct_answer.lower():
                    winners.append(voter.id)
                else:
                    losers.append(voter.id)
        
        users = session.query(User.User).filter(User.User.user_id.in_(user_ids)).all()
        user_map = {user.user_id: user for user in users}
        
        for winner in winners:
            if winner in user_map:
                user = user_map[winner]
                total_bet += user.poll_gamba
                total_winners += user.poll_gamba
        
        for loser in losers:
            if loser in user_map:
                user = user_map[loser]
                total_bet += user.poll_gamba
                total_losers += user.poll_gamba

        if total_winners > 0 or total_losers > 0:
            for winner in winners:
                if winner in user_map:
                    if winner == poll_creator:
                        continue
                    user = user_map[winner]
                    won_amount = total_bet * (user.poll_gamba / total_winners)
                    user.balance += won_amount
                    user.total_earned += won_amount
                    user.total_bets += 1
                    user.poll_gamba = 0
                    embed.add_field(name=user.name, value=f"Won: {won_amount}", inline=False)
            
            for loser in losers:
                if loser in user_map:
                    user = user_map[loser]
                    embed.add_field(name=user.name, value=f"Lost: {user.poll_gamba}", inline=False)
                    user.total_lost += user.poll_gamba
                    user.total_bets += 1
                    user.poll_gamba = 0


            # Commit transactions
            session.commit()
            embed.description = "Payouts processed successfully!"
        else:
            embed.description = "No winners to process payouts."
        
        await ctx.send(embed=embed)
        
        

async def setup(bot):
    await bot.add_cog(Gamba(bot)) 