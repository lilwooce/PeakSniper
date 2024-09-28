from ast import alias
from discord.ext import commands, tasks
import discord
from discord import app_commands
import math
from datetime import datetime, timedelta, time
from dotenv import load_dotenv
import requests
import os 
from sqlalchemy.orm import sessionmaker
from sqlalchemy.sql.expression import func
from sqlalchemy import or_
import random
import logging
import json
from zoneinfo import ZoneInfo
from classes import Servers, User, database, Jobs, ShopItem, Stock, Businesses, Freelancers
import asyncio
import matplotlib.pyplot as plt

eastern = ZoneInfo("America/New_York")

load_dotenv()
getUser = os.getenv('GET_USER')
updateUser = os.getenv('UPDATE_USER')
addUser = os.getenv('ADD_USER')

allowed_ids = [347162620996091904]
admins = [347162620996091904, 187323145273868288]
def allowed():
    def predicate(interaction: discord.Interaction) -> bool:
        return interaction.user.id in allowed_ids
    return app_commands.check(predicate)

def admins_only():
    def predicate(interaction: discord.Interaction) -> bool:
        return interaction.user.id in allowed_ids
    return app_commands.check(predicate)

class Business(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.stock_tax = .02

    @commands.Cog.listener()
    async def on_ready(self):
        print(f"{self.__class__.__name__} Cog has been loaded\n----")

    @commands.hybrid_command()
    async def acquire(self, ctx, *, name: str):
        Session = sessionmaker(bind=database.engine)
        session = Session()

        try:
            # Fetch the user and business from the database
            user = session.query(User.User).filter_by(user_id=ctx.author.id).first()
            business = session.query(Businesses.Business).filter(Businesses.Business.name.ilike(f"%{name}%")).first()
            amount = business.current_value

            if not user:
                await ctx.send("User not found in the database.")
                return

            if user.in_jail:
                await ctx.send("You cannot buy businesses while in jail.")
                return

            if not business:
                await ctx.send(f"business '{name}' not found.")
                return

            if not business.in_market:
                await ctx.send(f"The business '{name}' is not currently available for purchase.")
                return
            
            if len(user.freelancers) > 0:
                for freelancer in user.freelancers:
                    f = session.query(Freelancers.Freelancer).filter_by(name == freelancer).first()
                    if f and f.type_of.lower() in "agent" and f.job_title.lower() in "business":
                        logging.warning("found Business Agent")
                    else:
                        await ctx.send("You cannot buy a business unless you have a *Business Agent*.")
                        return

            # # Determine the amount to bid
            # if amount.lower() == "all":
            #     amount = user.balance
            # elif amount.lower() == "half":
            #     amount = user.balance // 2
            # else:
            #     try:
            #         amount = int(amount)
            #     except ValueError:
            #         await ctx.send("Invalid amount. Please specify a valid number or use 'all' or 'half'.")
            #         return

            if user.balance < amount:
                await ctx.send("You cannot afford to buy this business.")
                return

            # if amount <= 0:
            #     await ctx.send("Bid more than one discoinn, please!")
            #     return
            
            if business.owner != 0:
                owner = session.query(User.User).filter_by(user_id=business.owner).first()

                # Deduct the bid amount from user's balance
                user.balance -= amount
                owner.balance += amount

                business.in_market = False
                business.owner = ctx.author.id
                business.last_expense_paid = datetime.now()
                business.expenses = 0
            else:
                user.balance -= amount

                business.in_market = False
                business.owner = ctx.author.id
                business.last_expense_paid = datetime.now()
                business.expenses = 0

            # # Update bid history for the business
            # bid_history = json.loads(business.bid_history) if business.bid_history else {}
            # bid_history[str(ctx.author.id)] = bid_history.get(str(ctx.author.id), 0) + amount
            # business.bid_history = json.dumps(bid_history)

            # Commit the transaction
            session.commit()

            await ctx.send(f"You have purchased {business.name} for {amount} discoins.")

        except Exception as e:
            await ctx.send("An error occurred while processing your purchase.")
            logging.warning(f"Error: {e}")

        finally:
            session.close()

    @commands.hybrid_command()
    async def auction(self, ctx, *, name: str = None):
        Session = sessionmaker(bind=database.engine)
        session = Session()

        try:
            user = session.query(User.User).filter_by(user_id=ctx.author.id).first()

            if not user:
                await ctx.send("User not found in the database.")
                return
            
            freelancers = json.loads(user.freelancers)
            if len(freelancers) > 0:
                for freelancer in freelancers:
                    logging.warning(freelancer)
                    f = session.query(Freelancers.Freelancer).filter_by(name == freelancer).first()
                    if f and f.type_of.lower() in "agent" and f.job_title.lower() in "business":
                        logging.warning("found Business Agent")
                    else:
                        await ctx.send("You cannot list your business unless you have a *Business Agent*.")
                        return

            # Find the business by name and ensure the user owns it
            business = session.query(Businesses.Business).filter(Businesses.Business.owner == user.user_id,Businesses.Business.name.ilike(f"%{name}%")).first()

            if not business:
                await ctx.send(f"Business '{name}' not found or you do not own it.")
                return

            # Set the business to be on the market
            business.in_market = True
            #business.bid_history = {}

            # Commit the changes
            session.commit()

            await ctx.send(f"The business '{business.name}' has been listed on the market.")

        except Exception as e:
            await ctx.send("An error occurred while processing your listing.")
            logging.warning(f"Error: {e}")

        finally:
            session.close()

    @commands.hybrid_command(aliases=['bs'])
    async def businesses(self, ctx):
        Session = sessionmaker(bind=database.engine)
        session = Session()

        try:
            # Query all businesses that are in the market
            businesses = session.query(Businesses.Business).filter_by(in_market=True).all()
            if not businesses:
                await ctx.send("No businesses are currently available in the market.")
                return

            # Prepare to paginate
            embeds = []
            businesses_per_page = 3
            total_pages = (len(businesses) + businesses_per_page - 1) // businesses_per_page

            for page in range(total_pages):
                embed = discord.Embed(title=f"Business Market (Page {page + 1}/{total_pages})", color=discord.Color.blue())
                start = page * businesses_per_page
                end = start + businesses_per_page

                for business in businesses[start:end]:
                    # Check if there are bids and format the price information accordingly
                    if business.current_value:
                        cv = business.current_value
                        price_info = f"Current Value: {cv} discoins"
                    else:
                        business.current_value = 100000
                        price_info = "Current Value: 100000 discoins"

                    embed.add_field(
                        name=business.name,
                        value=f"Type: {business.type_of}\n{price_info}\nDaily Expenses: {business.daily_expense}\nDaily Revenue: {business.daily_revenue}",
                        inline=False
                    )

                embeds.append(embed)

            # Send the embeds with pagination
            if embeds:
                message = await ctx.send(embed=embeds[0])
                page = 0

                if len(embeds) > 1:
                    await message.add_reaction("◀️")
                    await message.add_reaction("▶️")

                def check(reaction, user):
                    return user == ctx.author and str(reaction.emoji) in ["◀️", "▶️"] and reaction.message.id == message.id

                session.close()
                while True:
                    try:
                        reaction, user = await self.bot.wait_for("reaction_add", timeout=60.0, check=check)

                        if str(reaction.emoji) == "▶️" and page < len(embeds) - 1:
                            page += 1
                            await message.edit(embed=embeds[page])
                        elif str(reaction.emoji) == "◀️" and page > 0:
                            page -= 1
                            await message.edit(embed=embeds[page])

                        await message.remove_reaction(reaction, user)
                    except asyncio.TimeoutError:
                        await message.clear_reactions()
                        break
            else:
                session.close()

        except Exception as e:
            await ctx.send("An error occurred while retrieving the housing market.")
            logging.warning(f"Error: {e}")

    @commands.hybrid_command()
    async def details(self, ctx, *, name: str):
        Session = sessionmaker(bind=database.engine)
        session = Session()

        try:
            # Query business details
            business = session.query(Businesses.Business).filter(Businesses.Business.name == name).first()

            if not business:
                await ctx.send(f"Business '{name}' not found.")
                return

            # Prepare the embed with the business details
            embed = discord.Embed(title=f"Details for {business.name}", color=discord.Color.green())
            embed.add_field(name="Owner", value=self.bot.get_user(business.owner).name if business.owner != 0 else "None", inline=False)
            embed.add_field(name="Type", value=business.type_of, inline=False)
            embed.add_field(name="Daily Expenses", value=business.daily_expense, inline=False)
            embed.add_field(name="Daily Revenue", value=business.daily_revenue, inline=False)

            if business.in_market:
                embed.add_field(name="Current Price", value=f"{business.current_value} discoins", inline=False)
                # # Load bid_history as a dictionary
                # bid_history = json.loads(business.bid_history) if business.bid_history else {}

                # if bid_history:
                #     highest_bid = max(bid_history.values())
                #     embed.add_field(name="Highest Bid", value=f"{highest_bid} discoins", inline=False)
                # else:
                #     embed.add_field(name="Highest Bid", value="No bids yet", inline=False)

            else:
                embed.add_field(name="Purchase Price", value=f"{business.purchase_value} discoins", inline=False)

            # Attempt to generate and attach an image (if applicable)
            try:
                buf = business.graph()  # Replace with your method to generate a graph or image for the business
                file = discord.File(fp=buf, filename=f"{business.name}_graph.png")
                embed.set_image(url=f"attachment://{business.name}_graph.png")
                image_sent = True
            except Exception as e:
                logging.warning(f"Cannot retrieve graph: {e}")
                image_sent = False

            # Send the embed with the image if available
            if image_sent:
                await ctx.send(embed=embed, file=file)
            else:
                await ctx.send(embed=embed)

        except Exception as e:
            await ctx.send("An error occurred while retrieving the business details.")
            logging.warning(f"Error: {e}")

        finally:
            session.close()

    @commands.hybrid_command()
    async def mybiz(self, ctx, user: discord.Member = None):
        Session = sessionmaker(bind=database.engine)
        session = Session()

        try:
            user = user or ctx.author
            u = session.query(User.User).filter_by(user_id=user.id).first()

            if not u:
                await ctx.send("User not found in the database.")
                return

            # Retrieve the user's portfolio (businesses)
            businesses = session.query(Businesses.Business).filter_by(owner=u.user_id).all()
            if not businesses:
                await ctx.send(f"{user.name} does not own any businesses.")
                return

            # Prepare to paginate
            embeds = []
            businesses_per_page = 3
            total_pages = (len(businesses) + businesses_per_page - 1) // businesses_per_page

            for page in range(total_pages):
                embed = discord.Embed(title=f"{user.name}'s businesses (Page {page + 1}/{total_pages})", color=discord.Color.gold())
                start = page * businesses_per_page
                end = start + businesses_per_page

                for business in businesses[start:end]:
                    if business.in_market:
                        #price_info = f"Highest Bid: {max(json.loads(business.bid_history).values(), default='No bids yet')} discoins" if business.bid_history else "No bids yet"
                        price_info = f"Current Value: {business.current_value} discoins."
                    else:
                        price_info = f"Purchase Price: {business.purchase_value} discoins"

                    embed.add_field(
                        name=business.name,
                        value=f"Type: {business.type_of}\n{price_info}\nDaily Expenses: {business.daily_expense}\nDaily Revenue: {business.daily_revenue}",
                        inline=False
                    )

                embeds.append(embed)

            # Send the embeds with pagination
            if embeds:
                message = await ctx.send(embed=embeds[0])
                page = 0

                if len(embeds) > 1:
                    await message.add_reaction("◀️")
                    await message.add_reaction("▶️")

                def check(reaction, user):
                    return user == ctx.author and str(reaction.emoji) in ["◀️", "▶️"] and reaction.message.id == message.id

                session.close()
                while True:
                    try:
                        reaction, user = await self.bot.wait_for("reaction_add", timeout=60.0, check=check)

                        if str(reaction.emoji) == "▶️" and page < len(embeds) - 1:
                            page += 1
                            await message.edit(embed=embeds[page])
                        elif str(reaction.emoji) == "◀️" and page > 0:
                            page -= 1
                            await message.edit(embed=embeds[page])

                        await message.remove_reaction(reaction, user)
                    except asyncio.TimeoutError:
                        await message.clear_reactions()
                        break
            else:
                session.close()

        except Exception as e:
            await ctx.send("An error occurred while retrieving the businesses.")
            logging.warning(f"Error: {e}")
    
async def setup(bot):
    await bot.add_cog(Business(bot))