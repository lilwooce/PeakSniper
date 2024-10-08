from discord.ext import commands
import os
import discord 
import random
from dotenv import load_dotenv
from sqlalchemy.orm import sessionmaker
from classes import User, database
from classes import Servers, User, database, Jobs, Global, ShopItem, Utils
import json
from datetime import datetime

class Gamba(commands.Cog, name="Gamba"):
    def __init__(self, client: commands.Bot):
        self.minCoinBid = 5
        self.cfMulti = 2
        self.client = client

    @commands.command(aliases=['cf'], description="This is a simple game where the user selects between heads or tails. You double your wager each time you win. It's simple yet addictive, side bets are always welcome!")
    @commands.cooldown(1, .5, commands.BucketType.user)
    async def coinflip(self, ctx, bet, amount):
        heads = ["heads", "head", "h"]
        tails = ["tails", "tail", "t"]
        author = ctx.author
        Session = sessionmaker(bind=database.engine)
        session = Session()
        try:
            u = session.query(User.User).filter_by(user_id=author.id).first()

            # Check for injury
            injured = self.check_injured(u)
            if injured:
                m, s = injured
                await ctx.send(f"You are injured! Please wait {int(m)} minutes and {int(s)} seconds before attempting to work again.")
                return  # Return early if the user is injured

            bal = u.balance
            if type(amount) == str and amount.lower() in "all":
                amount = u.balance
            elif type(amount) == str and amount.lower() in "half":
                amount = u.balance / 2
            else:
                amount = int(amount)
            if amount > int(bal):
                await ctx.send("You are too poor to afford this bet. Check your balance before betting next time.")
                return
            if amount < self.minCoinBid:
                await ctx.send("Bet more money you poor fuck. The minimum bet is 5 discoins.")
                return
            if bet.lower() not in heads and bet.lower() not in tails:
                await ctx.send("Please type heads or tails")
                return

            result = random.randint(0, 1)
            if result == 0 and bet.lower() in heads or result == 1 and bet.lower() in tails:
                total = amount * self.cfMulti
                won = total - amount
                used_items = json.loads(u.used_items) if u.used_items else {}
                used_items_objects = []
                for item in used_items:
                    shop_item = session.query(ShopItem.ShopItem).filter_by(name=item).first()
                    
                    if shop_item:
                        # Add the queried ShopItem object to the used_items_objects array
                        used_items_objects.append(shop_item)


                item_boost = u.get_multiplier(used_items_objects, "gamba")
                free_boost = Utils.Utils.get_boost(u.user_id, session, "gamba", "assistant")
                multi = free_boost + item_boost

                won = int(won * multi)
                u.total_earned += won
                u.balance += won
                await ctx.send(f"Congrats!!! You won {int(won)} discoins")
            else:
                u.balance -= amount
                u.total_lost += amount
                await ctx.send(f"You lost. lol. -{amount} discoins")

            u.total_bets += 1
        finally:
            session.commit()
            session.close()

    @commands.command(description="Lottery style betting functionality, allowing players that have earned coins to pick a number and bet a certain amount to win even more coins.")
    @commands.cooldown(1, .5, commands.BucketType.user)
    async def bet(self, ctx, bet: int, amount):
        author = ctx.author
        Session = sessionmaker(bind=database.engine)
        session = Session()
        try:
            u = session.query(User.User).filter_by(user_id=author.id).first()
            
            # Check for injury
            injured = self.check_injured(u)
            if injured:
                m, s = injured
                await ctx.send(f"You are injured! Please wait {int(m)} minutes and {int(s)} seconds before attempting to work again.")
                return  # Return early if the user is injured

            bal = u.balance
            if type(amount) == str and amount.lower() in "all":
                amount = u.balance
            elif type(amount) == str and amount.lower() in "half":
                amount = u.balance / 2
            else:
                amount = int(amount)
            if amount > bal:
                await ctx.send("You are too poor to afford this bet. Check your balance before betting next time.")
                return
            if amount <= 0:
                await ctx.send("Idiot.")
            if bet < 1 or bet > 100:
                await ctx.send("Please choose a number between 1 and 100 for your bet. Including 1 and 100.")
                return

            result = random.randint(1, 100)
            if result == bet:
                won = amount * 100
                used_items = json.loads(u.used_items) if u.used_items else {}
                used_items_objects = []
                for item in used_items:
                    shop_item = session.query(ShopItem.ShopItem).filter_by(name=item).first()
                    
                    if shop_item:
                        # Add the queried ShopItem object to the used_items_objects array
                        used_items_objects.append(shop_item)


                item_boost = u.get_multiplier(used_items_objects, "gamba")
                free_boost = Utils.Utils.get_boost(u.user_id, session, "gamba", "assistant")
                multi = free_boost + item_boost

                won = int(won * multi)
                u.balance += won
                u.total_earned += won
                await ctx.send(f"Congrats!!! You won {int(won)} discoins")
            else:
                u.balance -= amount
                u.total_lost += amount
                await ctx.send(f"You lost. You chose **{bet}** but the bot chose **{result}**. Better luck next time.")
            
            u.total_bets += 1
        finally:
            session.commit()
            session.close()

    @commands.hybrid_command()
    async def setpollgamba(self, ctx, amount):
        author = ctx.author
        Session = sessionmaker(bind=database.engine)
        session = Session()
        try:
            u = session.query(User.User).filter_by(user_id=author.id).first()

            if type(amount) == str and amount.lower() in "all":
                amount = u.balance
            elif type(amount) == str and amount.lower() in "half":
                amount = u.balance / 2
            else:
                amount = int(amount)
            if amount == 0:
                u.balance += u.poll_gamba
                await ctx.send(f"You withdrew your gamble of {u.poll_gamba} discoins")
                u.poll_gamba = 0
                return
            if amount > u.balance:
                await ctx.send("You are too poor")
                return
            if amount <= 0:
                await ctx.send("Please bet more than 0")
                return
            if u.poll_gamba > 0:
                u.balance += u.poll_gamba
                u.poll_gamba = 0
            
            u.poll_gamba = amount
            u.balance -= amount
            await ctx.send(f"You have set the amount for your next poll gamble to **{amount}**")
        finally:
            session.commit()
            session.close()

    @commands.hybrid_command()
    async def payout(self, ctx, poll: discord.Message, correct_answer: str):
        poll_creator = poll.author.id
        if ctx.author.id != poll_creator:
            await ctx.send("You do not have the right")
            return
        
        Session = sessionmaker(bind=database.engine)
        session = Session()
        try:
            embed = discord.Embed(title="Payout Results")
            total_bet = 0
            total_winners = 0
            total_losers = 0
            winners = []
            losers = []

            user_ids = set()
            for answer in poll.poll.answers:
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
                        if user.poll_gamba <= 0:
                            continue
                        won_amount = total_bet * (user.poll_gamba / total_winners)
                        user.balance += won_amount
                        user.total_earned += won_amount
                        user.total_bets += 1
                        user.poll_gamba = 0
                        embed.add_field(name=user.name, value=f"Won: {won_amount}", inline=False)
                
                for loser in losers:
                    if loser in user_map:
                        user = user_map[loser]
                        if user.poll_gamba <= 0:
                            continue
                        embed.add_field(name=user.name, value=f"Lost: {user.poll_gamba}", inline=False)
                        user.total_lost += user.poll_gamba
                        user.total_bets += 1
                        user.poll_gamba = 0

                embed.description = "Payouts processed successfully!"
            else:
                embed.description = "No winners to process payouts."

            await ctx.send(embed=embed)
        finally:
            session.commit()
            session.close()

    def check_injured(self, u):
        current_time = datetime.now()
        if u.injury and current_time < u.injury:
            remaining_time = (u.injury - current_time).total_seconds()
            minutes, seconds = divmod(remaining_time, 60)
            return minutes, seconds
        return None  # Return None if there's no injury or the injury has expired

    @commands.hybrid_command()
    @commands.cooldown(1, 5, commands.BucketType.user)
    async def work(self, ctx):
        Session = sessionmaker(bind=database.engine)
        session = Session()
        try:
            u = session.query(User.User).filter_by(user_id=ctx.author.id).first()
            job_name = u.job

            # Check for injury
            injured = self.check_injured(u)
            if injured:
                m, s = injured
                await ctx.send(f"You are injured! Please wait {int(m)} minutes and {int(s)} seconds before attempting to work again.")
                return  # Return early if the user is injured
            
            if job_name is None:
                await ctx.send("Job not found. Please apply first before working.")
                return
            
            j = session.query(Jobs.Jobs).filter_by(name=job_name).first()
            am = j.salary + random.randint(1, j.salary)

            used_items = json.loads(u.used_items) if u.used_items else {}
            used_items_objects = []
            for item in used_items:
                shop_item = session.query(ShopItem.ShopItem).filter_by(name=item).first()
                
                if shop_item:
                    # Add the queried ShopItem object to the used_items_objects array
                    used_items_objects.append(shop_item)


            item_boost = u.get_multiplier(used_items_objects, "work")
            free_boost = Utils.Utils.get_boost(u.user_id, session, "work", "assistant")
            multi = free_boost + item_boost

            am = int(am * multi)
            u.balance += am
            u.total_earned += am
            await ctx.send(f"You have made {am} from working!")
        finally:
            session.commit()
            session.close()

        
    #See Rstudio for better code

async def setup(bot):
    await bot.add_cog(Gamba(bot))
