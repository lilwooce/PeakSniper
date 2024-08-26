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

from classes import Servers, User, database, Jobs, ShopItem

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
                    embed.add_field(name=item.name, value=f"Price: {item.price}\nUses: {item.uses}", inline=False)
                return embed

            # Send the first embed
            message = await ctx.send(embed=create_embed(current_page))

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

        finally:
            session.close()

            
    @commands.hybrid_command()
    async def buy(self, ctx, amount: int, *, name: str):
        Session = sessionmaker(bind=database.engine)
        session = Session()
        
        try:
            item = session.query(ShopItem.ShopItem).filter_by(name=name).first()
            if not item:
                await ctx.send(f"{name} was not found in shop.")
            u = session.query(User.User).filter_by(user_id=ctx.author.id).first()

            if u.balance < item.price * amount:
                await ctx.send("You cannot afford this item")
                return

            u.balance -= item.price * amount
            inven = json.loads(u.inventory) if u.inventory else {}
            inven[item.name] = amount

            await ctx.send(f"You have bought {amount} {name}(s) for {item.price * amount} discoins.")
        finally:
            session.close()


        

async def setup(bot):
    await bot.add_cog(Shop(bot))