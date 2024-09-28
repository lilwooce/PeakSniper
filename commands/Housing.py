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
from classes import Servers, User, database, Jobs, ShopItem, Stock, Houses, Freelancers
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

class Housing(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.stock_tax = .02

    @commands.Cog.listener()
    async def on_ready(self):
        print(f"{self.__class__.__name__} Cog has been loaded\n----")

    @commands.hybrid_command()
    async def buyout(self, ctx, *, name: str):
        Session = sessionmaker(bind=database.engine)
        session = Session()

        try:
            # Fetch the user and house from the database
            user = session.query(User.User).filter_by(user_id=ctx.author.id).first()
            house = session.query(Houses.House).filter_by(name=name).first()
            amount = house.current_value

            if not user:
                await ctx.send("User not found in the database.")
                return

            if user.in_jail:
                await ctx.send("You cannot buy houses while in jail.")
                return

            if not house:
                await ctx.send(f"House '{name}' not found.")
                return

            if not house.in_market:
                await ctx.send(f"The house '{name}' is not currently available for purchase.")
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
                await ctx.send("You cannot afford to buy this house.")
                return

            # if amount <= 0:
            #     await ctx.send("Bid more than one discoinn, please!")
            #     return
            
            if owner != 0:
                owner = session.query(User.User).filter_by(user_id=house.owner).first()

                # Deduct the bid amount from user's balance
                user.balance -= amount
                owner.balance += amount

                house.in_market = False
                house.owner = ctx.author.id
                house.last_expense_paid = datetime.now()
                house.expenses = 0
            else:
                user.balance -= amount

                house.in_market = False
                house.owner = ctx.author.id
                house.last_expense_paid = datetime.now()
                house.expenses = 0

            # # Update bid history for the house
            # bid_history = json.loads(house.bid_history) if house.bid_history else {}
            # bid_history[str(ctx.author.id)] = bid_history.get(str(ctx.author.id), 0) + amount
            # house.bid_history = json.dumps(bid_history)

            # Commit the transaction
            session.commit()

            await ctx.send(f"You have purchased {house.name} for {amount} discoins.")

        except Exception as e:
            await ctx.send("An error occurred while processing your purchase.")
            logging.warning(f"Error: {e}")

        finally:
            session.close()

    @commands.hybrid_command()
    async def list(self, ctx, *, name: str = None):
        Session = sessionmaker(bind=database.engine)
        session = Session()

        try:
            user = session.query(User.User).filter_by(user_id=ctx.author.id).first()

            if not user:
                await ctx.send("User not found in the database.")
                return

            for freelancer in user.freelancers:
                if freelancer["type_of"].lower() == "agent" and "estate" in freelancer["job_title"].lower():
                    logging.warning("found real estate agent")
                else:
                    await ctx.send("You cannot list your house unless you have a *Real Esate Agent*.")
                    return

            # Find the house by name and ensure the user owns it
            house = session.query(Houses.House).filter_by(owner=user.user_id, name=name).first()

            if not house:
                await ctx.send(f"House '{name}' not found or you do not own it.")
                return

            # Set the house to be on the market
            house.in_market = True
            house.bid_history = {}

            # Commit the changes
            session.commit()

            await ctx.send(f"The house '{house.name}' has been listed on the market.")

        except Exception as e:
            await ctx.send("An error occurred while processing your listing.")
            logging.warning(f"Error: {e}")

        finally:
            session.close()

    @commands.hybrid_command(aliases=['hm'])
    async def housing_market(self, ctx):
        Session = sessionmaker(bind=database.engine)
        session = Session()

        try:
            # Query all houses that are in the market
            houses = session.query(Houses.House).filter_by(in_market=True).all()
            if not houses:
                await ctx.send("No houses are currently available in the market.")
                return

            # Prepare to paginate
            embeds = []
            houses_per_page = 3
            total_pages = (len(houses) + houses_per_page - 1) // houses_per_page

            for page in range(total_pages):
                embed = discord.Embed(title=f"Housing Market (Page {page + 1}/{total_pages})", color=discord.Color.blue())
                start = page * houses_per_page
                end = start + houses_per_page

                for house in houses[start:end]:
                    # Check if there are bids and format the price information accordingly
                    if house.current_value:
                        cv = house.current_value
                        price_info = f"Current Value: {cv} discoins"
                    else:
                        house.current_value = 100000
                        price_info = "Current Value: 100000 discoins"

                    embed.add_field(
                        name=house.name,
                        value=f"Type: {house.type_of}\n{price_info}",
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
    async def house(self, ctx, *, name: str):
        Session = sessionmaker(bind=database.engine)
        session = Session()

        try:
            # Query house details
            house = session.query(Houses.House).filter(Houses.House.name == name).first()

            if not house:
                await ctx.send(f"House '{name}' not found.")
                return

            # Prepare the embed with the house details
            embed = discord.Embed(title=f"Details for {house.name}", color=discord.Color.green())
            embed.add_field(name="Type", value=house.type_of, inline=False)

            if house.in_market:
                embed.add_field(name="Current Price", value=f"{house.current_value} discoins", inline=False)
                # # Load bid_history as a dictionary
                # bid_history = json.loads(house.bid_history) if house.bid_history else {}

                # if bid_history:
                #     highest_bid = max(bid_history.values())
                #     embed.add_field(name="Highest Bid", value=f"{highest_bid} discoins", inline=False)
                # else:
                #     embed.add_field(name="Highest Bid", value="No bids yet", inline=False)

            else:
                embed.add_field(name="Purchase Price", value=f"{house.purchase_value} discoins", inline=False)

            # Attempt to generate and attach an image (if applicable)
            try:
                buf = house.graph()  # Replace with your method to generate a graph or image for the house
                file = discord.File(fp=buf, filename=f"{house.name}_graph.png")
                embed.set_image(url=f"attachment://{house.name}_graph.png")
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
            await ctx.send("An error occurred while retrieving the house details.")
            logging.warning(f"Error: {e}")

        finally:
            session.close()



    @commands.hybrid_command()
    async def houses(self, ctx, user: discord.Member = None):
        Session = sessionmaker(bind=database.engine)
        session = Session()

        try:
            user = user or ctx.author
            u = session.query(User.User).filter_by(user_id=user.id).first()

            if not u:
                await ctx.send("User not found in the database.")
                return

            # Retrieve the user's portfolio (houses)
            houses = session.query(Houses.House).filter_by(owner=u.user_id).all()
            if not houses:
                await ctx.send(f"{user.name} does not own any houses.")
                return

            # Prepare to paginate
            embeds = []
            houses_per_page = 3
            total_pages = (len(houses) + houses_per_page - 1) // houses_per_page

            for page in range(total_pages):
                embed = discord.Embed(title=f"{user.name}'s Houses (Page {page + 1}/{total_pages})", color=discord.Color.gold())
                start = page * houses_per_page
                end = start + houses_per_page

                for house in houses[start:end]:
                    if house.in_market:
                        #price_info = f"Highest Bid: {max(json.loads(house.bid_history).values(), default='No bids yet')} discoins" if house.bid_history else "No bids yet"
                        price_info = f"Current Value: {house.current_value} discoins."
                    else:
                        price_info = f"Purchase Price: {house.purchase_value} discoins"

                    embed.add_field(
                        name=house.name,
                        value=f"Type: {house.type_of}\n{price_info}",
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
            await ctx.send("An error occurred while retrieving the houses.")
            logging.warning(f"Error: {e}")
    
async def setup(bot):
    await bot.add_cog(Housing(bot))