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

        if(amount > int(bal)):
            await ctx.send("You are too poor to afford this bet. Check your balance before betting next time.")
        if (amount < self.minCoinBid):
            await ctx.send("Bet more money you poor fuck. The minimum bet is 5 discoins.")
        if((bet.lower() not in heads) or (bet.lower() not in tails)):
            await ctx.send("Please type heads or tails")

        result = random.randint(0,1)
        if (result == 0 and bet.lower() in heads):
            total = amount * (1+self.cfMulti)
            won = total - amount
            u.total_earned += won
            u.balance += won
            await ctx.send(f"Congrats!!! You won {int(won)} discoins")
        elif (result == 1 and bet.lower() in tails):
            total = amount * (1+self.cfMulti)
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
        if(bet < 1 and bet > 100):
            await ctx.send("Please choose a number between 1 and 100 for your bet. Including 1 and 100.")

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
    async def setpollgamba(self, ctx, amount):
        author = ctx.author
        Session = sessionmaker(bind=database.engine)
        session = Session()
        u = session.query(User.User).filter_by(user_id=author.id).first()

        if not amount:
            await ctx.send("Please set an amount for your next poll gamble")
        if amount > u.balance:
            await ctx.send("You are too poor")
        if amount <= 0:
            await ctx.send("Please bet more than 0")
        
        #set the amount in the database
        u.poll_gamba = amount
        session.commit()
        session.close()

    @commands.hybrid_command()
    async def payout(self, ctx, poll):
        return

async def setup(bot):
    await bot.add_cog(Gamba(bot)) 