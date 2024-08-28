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
from classes import Servers, User, database, Jobs, ShopItem, Stock
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

class Stocks(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.update_stocks.start()

    @commands.Cog.listener()
    async def on_ready(self):
        print(f"{self.__class__.__name__} Cog has been loaded\n----")
    
    def cog_unload(self):
        self.update_stocks()

    @commands.hybrid_command()
    async def purchase(self, ctx, amount: int, *, name: str):
        Session = sessionmaker(bind=database.engine)
        session = Session()

        try:
            user = session.query(User.User).filter_by(user_id=ctx.author.id).first()
            stock = session.query(Stock.Stock).filter(or_(Stock.Stock.name == name, Stock.Stock.full_name == name)).first()

            if not user:
                await ctx.send("User not found in the database.")
                return

            if not stock:
                await ctx.send(f"Stock '{name}' not found.")
                return

            total_cost = int(stock.current_value) * amount
            if user.balance < total_cost:
                await ctx.send("You cannot afford this purchase.")
                return
            
            if amount <= 0:
                await ctx.send("Dumbass!")
                return

            user.balance -= total_cost
            user.total_lost += total_cost
            portfolio = json.loads(user.portfolio) if user.portfolio else {}
            portfolio[stock.name] = portfolio.get(stock.name, 0) + amount

            user.portfolio = json.dumps(portfolio)
            session.commit()

            await ctx.send(f"You have purchased {amount} shares of {stock.name} for {total_cost} discoins.")

        except Exception as e:
            await ctx.send("An error occurred while processing your purchase.")
            logging.warning(f"Error: {e}")

        finally:
            session.close()

    @commands.hybrid_command()
    async def liquidate(self, ctx, amount: int, *, name: str):
        Session = sessionmaker(bind=database.engine)
        session = Session()

        try:
            user = session.query(User.User).filter_by(user_id=ctx.author.id).first()
            stock = session.query(Stock.Stock).filter(or_(Stock.Stock.name == name, Stock.Stock.full_name == name)).first()

            if not user:
                await ctx.send("User not found in the database.")
                return

            if not stock:
                await ctx.send(f"Stock '{name}' not found.")
                return

            portfolio = json.loads(user.portfolio) if user.portfolio else {}

            if stock.name not in portfolio or portfolio[stock.name] < amount:
                await ctx.send(f"You do not own enough shares of {stock.name} to sell.")
                return

            total_value = int(stock.current_value) * amount
            user.balance += total_value
            user.total_earned += total_value
            portfolio[stock.name] -= amount
            if portfolio[stock.name] == 0:
                del portfolio[stock.name]

            user.portfolio = json.dumps(portfolio)
            session.commit()

            await ctx.send(f"You have liquidated {amount} shares of {stock.name} for {total_value} discoins.")

        except Exception as e:
            await ctx.send("An error occurred while processing your liquidation.")
            logging.warning(f"Error: {e}")

        finally:
            session.close()

    @commands.hybrid_command()
    async def stocks(self, ctx):
        Session = sessionmaker(bind=database.engine)
        session = Session()

        try:
            stocks = session.query(Stock.Stock).all()
            if not stocks:
                await ctx.send("No stocks available at the moment.")
                return

            embeds = []
            embed = discord.Embed(title="Available Stocks", color=discord.Color.blue())
            for i, stock in enumerate(stocks, start=1):
                percent_change = stock.get_percentage_change()
                embed.add_field(
                    name=stock.name,
                    value=f"Value: {stock.current_value:.2f} discoins\nPercent Change: {percent_change:.2f}%",
                    inline=False
                )
                if i % 4 == 0 or i == len(stocks):
                    embeds.append(embed)
                    embed = discord.Embed(title="Available Stocks", color=discord.Color.blue())

            if not embeds:
                await ctx.send("No stocks available at the moment.")
                return

            message = await ctx.send(embed=embeds[0])
            page = 0

            await message.add_reaction("◀️")
            await message.add_reaction("▶️")

            def check(reaction, user):
                return user == ctx.author and str(reaction.emoji) in ["◀️", "▶️"] and reaction.message.id == message.id

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

        except Exception as e:
            await ctx.send("An error occurred while retrieving stocks.")
            logging.warning(f"Error: {e}")

        finally:
            session.close()

    @commands.hybrid_command()
    async def stock(self, ctx, *, name: str):
        Session = sessionmaker(bind=database.engine)
        session = Session()

        try:
            stock = session.query(Stock.Stock).filter(
                or_(Stock.Stock.name == name, Stock.Stock.full_name == name)
            ).first()

            if not stock:
                await ctx.send(f"Stock '{name}' not found.")
                return

            # First page embed
            embed1 = discord.Embed(title=f"Details for {stock.name}", color=discord.Color.green())
            embed1.add_field(name="Full Name", value=stock.full_name, inline=False)
            embed1.add_field(name="Current Value", value=f"{stock.current_value:.2f} discoins", inline=False)
            embed1.add_field(name="Record Low", value=f"{stock.record_low:.2f} discoins", inline=False)
            embed1.add_field(name="Record High", value=f"{stock.record_high:.2f} discoins", inline=False)
            embed1.add_field(name="Status", value="Crashed" if stock.crashed else stock.is_stable().title(), inline=False)

            # Second page embed
            embed2 = discord.Embed(title=f"Graph for {stock.name}", color=discord.Color.green())
            image_data = f"data:image/png;base64,{self.graph()}"
            embed2.set_image(url=image_data)

            # Pagination logic
            pages = [embed1, embed2]
            current_page = 0

            message = await ctx.send(embed=pages[current_page])

            await message.add_reaction("◀️")
            await message.add_reaction("▶️")

            def check(reaction, user):
                return user == ctx.author and str(reaction.emoji) in ["◀️", "▶️"]

            while True:
                try:
                    reaction, user = await self.bot.wait_for("reaction_add", timeout=60.0, check=check)

                    if str(reaction.emoji) == "▶️" and current_page < len(pages) - 1:
                        current_page += 1
                        await message.edit(embed=pages[current_page])
                    elif str(reaction.emoji) == "◀️" and current_page > 0:
                        current_page -= 1
                        await message.edit(embed=pages[current_page])

                    await message.remove_reaction(reaction, user)
                except Exception as e:
                    logging.warning(f"Error: {e}")
                    break

        except Exception as e:
            await ctx.send("An error occurred while retrieving the stock details.")
            logging.warning(f"Error: {e}")

        finally:
            session.close()

    @commands.hybrid_command()
    async def portfolio(self, ctx, user: discord.Member = None):
        Session = sessionmaker(bind=database.engine)
        session = Session()

        try:
            user = user or ctx.author
            u = session.query(User.User).filter_by(user_id=user.id).first()

            if not u:
                await ctx.send("User not found in the database.")
                return

            portfolio = json.loads(u.portfolio) if u.portfolio else {}
            if not portfolio or len(portfolio) <= 0:
                await ctx.send(f"{user.name} does not own any stocks.")
                return

            embed = discord.Embed(title=f"{user.name}'s Portfolio", color=discord.Color.gold())
            total_value = 0
            for stock_name, shares in portfolio.items():
                stock = session.query(Stock.Stock).filter_by(name=stock_name).first()
                if stock:
                    value = int(stock.current_value) * shares
                    total_value += value
                    embed.add_field(
                        name=stock_name,
                        value=f"Shares: {shares}\nCurrent Value: {value:.2f} discoins",
                        inline=False
                    )

            embed.set_footer(text=f"Total Portfolio Value: {total_value:.2f} discoins")
            await ctx.send(embed=embed)

        except Exception as e:
            await ctx.send("An error occurred while retrieving the portfolio.")
            logging.warning(f"Error: {e}")

        finally:
            session.close()

    times = [time(hour=h, tzinfo=eastern) for h in range(0, 24, 3)]
    @tasks.loop(time=times)
    async def update_stocks(self):
        Session = sessionmaker(bind=database.engine)
        session = Session()
        try:
            stocks = session.query(Stock.Stock).all()
            for stock in stocks:
                stock.update()

            # Commit the changes to the database
            session.commit()
        finally:
            session.close()
    
    @commands.hybrid_command()
    async def man_update_stocks(self, ctx):
        Session = sessionmaker(bind=database.engine)
        session = Session()
        try:
            stocks = session.query(Stock.Stock).all()
            for stock in stocks:
                stock.update()

            # Commit the changes to the database
            session.commit()
            await ctx.send("Successfully updated the stock market!!!")
        finally:
            session.close()

async def setup(bot):
    await bot.add_cog(Stocks(bot))