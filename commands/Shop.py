from ast import alias
from discord.ext import commands
import discord
from discord import app_commands
import math
from datetime import datetime, timedelta
from dotenv import load_dotenv
import requests
import os 
from sqlalchemy.orm import sessionmaker
from sqlalchemy.sql.expression import func
import asyncio
import random
import json

from classes import Servers, User, database, Jobs, ShopItem, PremiumShopItem

class Shop(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.Cog.listener()
    async def on_ready(self):
        print(f"{self.__class__.__name__} Cog has been loaded\n----")

    @commands.hybrid_command()
    async def shop(self, ctx):
        Session = sessionmaker(bind=database.engine)
        session = Session()

        try:
            items = session.query(ShopItem.ShopItem).all()

            # Divide items into pages with a max of 3 items per page
            pages = [items[i:i + 3] for i in range(0, len(items), 3)]
            current_page = 0

            # Function to create an embed for a given page
            def create_embed(page):
                embed = discord.Embed(title="Shop", description=f"Page {page + 1}/{len(pages)}")
                for item in pages[page]:
                    embed.add_field(name=item.name.title(), value=f"Price: {item.price}\nDescription: {item.description}\nCommand: {item.command}", inline=False)
                return embed

            # Send the first embed
            message = await ctx.send(embed=create_embed(current_page))
            session.close()

            # Add reactions if there are multiple pages
            if len(pages) > 1:
                await message.add_reaction("⬅️")
                await message.add_reaction("➡️")

                # Check for reaction events
                def check(reaction, user):
                    return user == ctx.author and reaction.message.id == message.id and str(reaction.emoji) in ["⬅️", "➡️"]

                while True:
                    try:
                        reaction, user = await self.bot.wait_for("reaction_add", timeout=60.0, check=check)

                        if str(reaction.emoji) == "➡️":
                            if current_page < len(pages) - 1:
                                current_page += 1
                                await message.edit(embed=create_embed(current_page))
                        elif str(reaction.emoji) == "⬅️":
                            if current_page > 0:
                                current_page -= 1
                                await message.edit(embed=create_embed(current_page))

                        await message.remove_reaction(reaction, user)

                    except asyncio.TimeoutError:
                        break

                # Clear reactions after the timeout
                await message.clear_reactions()

        except:
            return
    
    @commands.hybrid_command(aliases=['ps'])
    async def premiumshop(self, ctx):
        Session = sessionmaker(bind=database.engine)
        session = Session()

        try:
            items = session.query(PremiumShopItem.PremiumShopItem).all()

            # Divide items into pages with a max of 3 items per page
            pages = [items[i:i + 3] for i in range(0, len(items), 3)]
            current_page = 0

            # Function to create an embed for a given page
            def create_embed(page):
                embed = discord.Embed(title="Premium Shop", description=f"Page {page + 1}/{len(pages)}")
                for item in pages[page]:
                    embed.add_field(name=item.name.title(), value=f"Price: {item.price}\nDescription: {item.description}\nCommand: {item.command}", inline=False)
                return embed

            # Send the first embed
            message = await ctx.send(embed=create_embed(current_page))
            session.close()

            # Add reactions if there are multiple pages
            if len(pages) > 1:
                await message.add_reaction("⬅️")
                await message.add_reaction("➡️")

                # Check for reaction events
                def check(reaction, user):
                    return user == ctx.author and reaction.message.id == message.id and str(reaction.emoji) in ["⬅️", "➡️"]

                while True:
                    try:
                        reaction, user = await self.bot.wait_for("reaction_add", timeout=60.0, check=check)

                        if str(reaction.emoji) == "➡️":
                            if current_page < len(pages) - 1:
                                current_page += 1
                                await message.edit(embed=create_embed(current_page))
                        elif str(reaction.emoji) == "⬅️":
                            if current_page > 0:
                                current_page -= 1
                                await message.edit(embed=create_embed(current_page))

                        await message.remove_reaction(reaction, user)

                    except asyncio.TimeoutError:
                        break

                # Clear reactions after the timeout
                await message.clear_reactions()

        except:
            return
            
    @app_commands.command()
    async def premiumbuy(self, interaction: discord.Interaction, amount: int, name: str):
        Session = sessionmaker(bind=database.engine)
        session = Session()
        
        with session as session:
            try:
                item = session.query(PremiumShopItem.PremiumShopItem).filter_by(name=name).first()
                if not item:
                    await interaction.response.send_message(f"{name} was not found in the Premium Shop.")
                    return

                u = session.query(User.User).filter_by(user_id=interaction.user.id).first()

                if not u:
                    await interaction.response.send_message("User not found.")
                    return

                if u.premium_balance < item.price * amount:
                    await interaction.response.send_message("You cannot afford this item")
                    return

                u.premium_balance -= item.price * amount
                inven = json.loads(u.inventory) if u.inventory else {}
                inven[item.name] = inven.get(item.name, 0) + amount
                u.inventory = json.dumps(inven)

                session.commit()
                await interaction.response.send_message(f"You have bought {amount} {name}(s) for {item.price * amount} discoins.")
            except Exception as e:
                print(f"Error in buy command: {e}")
                await interaction.response.send_message("An error occurred while processing your purchase.")

    @app_commands.command()
    async def sell(self, interaction: discord.Interaction, amount: int, name: str):
        Session = sessionmaker(bind=database.engine)
        
        with Session() as session:
            try:
                item = session.query(ShopItem.ShopItem).filter_by(name=name).first()
                if not item:
                    await interaction.response.send_message(f"{name} was not found in shop.")
                    return

                u = session.query(User.User).filter_by(user_id=interaction.user.id).first()

                if not u:
                    await interaction.response.send_message("User not found.")
                    return

                # Check if the user has the item in their inventory
                inven = json.loads(u.inventory) if u.inventory else {}
                if name not in inven or inven[name] < amount:
                    await interaction.response.send_message(f"You do not have enough {name}(s) to sell.")
                    return

                # Calculate the sell price (70% of the original price)
                sell_price = int(item.price * 0.7 * amount)

                # Remove the sold items from inventory
                inven[name] -= amount
                if inven[name] == 0:
                    del inven[name]  # Remove the item completely if the amount is 0
                u.inventory = json.dumps(inven)

                # Add the sell price to the user's balance
                u.balance += sell_price

                session.commit()
                await interaction.response.send_message(f"You have sold {amount} {name}(s) for {sell_price} discoins.")
            except Exception as e:
                print(f"Error in sell command: {e}")
                await interaction.response.send_message("An error occurred while processing your sale.")


async def setup(bot):
    await bot.add_cog(Shop(bot))