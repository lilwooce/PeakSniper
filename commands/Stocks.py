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
from classes import Servers, User, database, Jobs, ShopItem, Stock, Utils
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
        self.stock_tax = .02
        self.stock_multi = 0.00000000001
        self.min_stock_amount = 37000000

    @commands.Cog.listener()
    async def on_ready(self):
        print(f"{self.__class__.__name__} Cog has been loaded\n----")

    @commands.hybrid_command()
    async def purchase(self, ctx, amount: str, *, name: str):
        Session = sessionmaker(bind=database.engine)
        session = Session()

        try:
            user = session.query(User.User).filter_by(user_id=ctx.author.id).first()
            stock = session.query(Stock.Stock).filter(or_(Stock.Stock.name == name, Stock.Stock.full_name == name)).first()

            if not user:
                await ctx.send("User not found in the database.")
                return

            if user.in_jail == True:
                await ctx.send("You cannot purchase stocks while in jail.")
                return

            if not stock:
                await ctx.send(f"Stock '{name}' not found.")
                return

            if stock.type_of != "stock":
                await ctx.send("You cannot purchase this.")
                return
            
            if stock.amount <= 0:
                await ctx.send("There is none of this stock up for purchase.")
                return
            # Get the original price of the stock
            original_price = stock.current_value

            # Get the actual price using the get_price function
            price = Utils.Utils.get_price(user.user_id, session, stock.current_value, "stock")

            price_message = ""
            if price < original_price:
                price_message = f"Your stock broker has decreased the price of {stock.name} from {original_price} to {price}.\n"
            
            stock_amount = stock.amount
            
            # Handle "all" or "half" amount purchases
            if amount.lower() == "all":
                amount = min(user.balance // int(price), stock_amount)
            elif amount.lower() == "half":
                amount = min((user.balance // 2) // int(price), stock_amount // 2)
            else:
                amount = min(int(amount), stock_amount)

            total_cost = int(price) * amount

            if user.balance < total_cost:
                await ctx.send("You cannot afford this purchase.")
                return

            if amount <= 0:
                await ctx.send("Buy more than one stock please!")
                return

            # Update user's balance and portfolio
            user.balance -= total_cost
            user.total_lost += total_cost
            portfolio = json.loads(user.portfolio) if user.portfolio else {}
            portfolio[stock.name] = portfolio.get(stock.name, 0) + amount
            user.portfolio = json.dumps(portfolio)

            # Reduce the amount of stock left
            stock.amount -= amount

            # Adjust stock based on growth direction
            if stock.growth_direction == 1:
                stock.growth_rate += self.stock_multi * total_cost
                stock.swap_chance -= self.stock_multi * total_cost
                if total_cost > self.min_stock_amount:
                    stock.ruination *= 1.35
            elif stock.growth_direction == -1:
                stock.growth_rate -= self.stock_multi * total_cost
                stock.swap_chance += self.stock_multi * total_cost
                if total_cost > self.min_stock_amount:
                    stock.ruination *= 0.65

            # Commit the transaction
            session.commit()

            await ctx.send(f"{price_message}You have purchased {amount} shares of {stock.name} for {total_cost} discoins. There are {stock.amount} shares remaining.")

        except Exception as e:
            await ctx.send("An error occurred while processing your purchase.")
            logging.warning(f"Error: {e}")

        finally:
            session.close()



    @commands.hybrid_command(aliases=['ld'])
    async def liquidate(self, ctx, amount: str, *, name: str = None):
        Session = sessionmaker(bind=database.engine)
        session = Session()

        try:
            user = session.query(User.User).filter_by(user_id=ctx.author.id).first()

            if not user:
                await ctx.send("User not found in the database.")
                return

            portfolio = json.loads(user.portfolio) if user.portfolio else {}

            def get_liquidation_amount(available_amount):
                if amount.lower() == "all":
                    return int(available_amount)
                elif amount.lower() == "half":
                    return available_amount // 2
                else:
                    return int(amount) if amount <= available_amount else available_amount

            if name:
                stock = session.query(Stock.Stock).filter(or_(Stock.Stock.name == name, Stock.Stock.full_name == name)).first()

                if not stock:
                    await ctx.send(f"Stock '{name}' not found.")
                    return

                if stock.name not in portfolio:
                    await ctx.send(f"You do not own any shares of {stock.name}.")
                    return

                available_amount = portfolio[stock.name]
                liquidation_amount = get_liquidation_amount(available_amount)

                if liquidation_amount <= 0 or liquidation_amount > available_amount:
                    await ctx.send(f"You do not own enough shares of {stock.name} to sell {liquidation_amount}.")
                    return

                total_value = int(stock.current_value) * liquidation_amount
                tax = total_value * self.stock_tax
                user.bank += total_value - tax
                user.total_earned += total_value - tax
                portfolio[stock.name] -= liquidation_amount

                if portfolio[stock.name] == 0:
                    del portfolio[stock.name]
                
                stock.amount += liquidation_amount

                # Adjust stock properties based on growth direction
                if stock.growth_direction == 1:
                    stock.growth_rate -= self.stock_multi * total_value
                    stock.swap_chance += self.stock_multi * total_value
                    if total_value > self.min_stock_amount:
                        stock.ruination *= 1.1
                elif stock.growth_direction == -1:
                    stock.growth_rate -= self.stock_multi * total_value
                    stock.swap_chance += self.stock_multi * total_value
                    if total_value > self.min_stock_amount:
                        stock.ruination *= 1.35

                user.portfolio = json.dumps(portfolio)
                session.commit()

                await ctx.send(f"You have liquidated {liquidation_amount} shares of {stock.name} for {total_value - tax} discoins. You were taxed {tax} discoins for this transaction.")

            else:
                total_value = 0
                for stock_name, shares in list(portfolio.items()):
                    stock = session.query(Stock.Stock).filter_by(name=stock_name).first()
                    if stock:
                        liquidation_amount = get_liquidation_amount(shares)
                        value = int(stock.current_value) * liquidation_amount
                        total_value += value
                        portfolio[stock_name] -= liquidation_amount

                        if portfolio[stock_name] == 0:
                            del portfolio[stock_name]

                        stock.amount += liquidation_amount

                        # Adjust stock properties based on growth direction
                        if stock.growth_direction == 1:
                            stock.growth_rate -= self.stock_multi * value
                            stock.swap_chance += self.stock_multi * value
                            if value > self.min_stock_amount:
                                stock.ruination *= 1.01
                        elif stock.growth_direction == -1:
                            stock.growth_rate -= self.stock_multi * value
                            stock.swap_chance += self.stock_multi * value
                            if value > self.min_stock_amount:
                                stock.ruination *= 1.035

                tax = total_value * self.stock_tax
                user.bank += total_value - tax
                user.total_earned += total_value - tax
                user.portfolio = json.dumps(portfolio)
                session.commit()

                await ctx.send(f"You have liquidated shares for {total_value - tax} discoins. You were taxed {tax} discoins for this transaction.")

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

            for i, stock in enumerate(stocks, start=1):
                if not stock.type_of == "stock":
                    continue
                # Find the majority shareholder for the stock
                majority_shareholder = None
                max_shares = 0
                users = session.query(User.User).all()

                for user in users:
                    portfolio = json.loads(user.portfolio) if user.portfolio else {}
                    shares = portfolio.get(stock.name, 0)
                    if shares > max_shares:
                        max_shares = shares
                        majority_shareholder = user

                shareholder_info = f"{majority_shareholder.name}: {max_shares} shares" if majority_shareholder else "None"

                # Create an embed with the majority shareholder in the title
                if i % 4 == 1:  # Start a new embed every 4 stocks
                    embed = discord.Embed(
                        title=f"Available Stocks",
                        color=discord.Color.blue()
                    )

                percent_change = stock.get_percentage_change()
                embed.add_field(
                    name=f"{stock.name} | {shareholder_info}",
                    value=f"Value: {stock.current_value} discoins\nPercent Change: {percent_change:.2f}%\nTotal Left: {stock.amount}",
                    inline=False
                )

                if i % 4 == 0 or i == len(stocks):
                    embeds.append(embed)

            if not embeds:
                await ctx.send("No stocks available at the moment.")
                return

            message = await ctx.send(embed=embeds[0])
            page = 0

            await message.add_reaction("◀️")
            await message.add_reaction("▶️")
            session.close

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


    @commands.hybrid_command()
    async def stock(self, ctx, *, name: str):
        Session = sessionmaker(bind=database.engine)
        session = Session()

        try:
            # Query stock details
            stock = session.query(Stock.Stock).filter(
                or_(Stock.Stock.name == name, Stock.Stock.full_name == name)
            ).first()

            if not stock:
                await ctx.send(f"Stock '{name}' not found.")
                return

            # Create embed with all information
            embed = discord.Embed(title=f"Details for {stock.name}", color=discord.Color.green())
            embed.add_field(name="Full Name", value=stock.full_name, inline=False)
            embed.add_field(name="Amount in Circulation", value=stock.amount, inline=False)
            embed.add_field(name="Current Value", value=f"{stock.current_value:.2f} discoins", inline=False)
            embed.add_field(name="Record Low", value=f"{stock.record_low:.2f} discoins", inline=False)
            embed.add_field(name="Record High", value=f"{stock.record_high:.2f} discoins", inline=False)
            embed.add_field(name="Status", value="Crashed" if stock.crashed else stock.is_stable().title(), inline=False)

            try:
                # Generate the graph and save it as a BytesIO object
                buf = stock.graph()
                file = discord.File(fp=buf, filename=f"{stock.name}_graph.png")
                embed.set_image(url=f"attachment://{stock.name}_graph.png")
                image_sent = True
            except Exception as e:
                logging.warning(f"Cannot retrieve graph: {e}")
                image_sent = False

            # Send the embed with image if available
            if image_sent:
                await ctx.send(embed=embed, file=file)
            else:
                await ctx.send(embed=embed)

        except Exception as e:
            await ctx.send("An error occurred while retrieving the stock details.")
            logging.warning(f"Error: {e}")

        finally:
            session.close()


    @commands.hybrid_command(aliases=['pf'])
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
            prev_total = 0
            for stock_name, shares in portfolio.items():
                stock = session.query(Stock.Stock).filter_by(name=stock_name).first()
                if stock:
                    value = int(stock.current_value) * shares
                    prev_value = int(stock.previous_value) * shares
                    total_value += value
                    prev_total += prev_value
                    embed.add_field(
                        name=stock_name,
                        value=f"Shares: {shares}\nCurrent Value: {value} discoins\nPrevious Value: {prev_value} discoins",
                        inline=False
                    )

            embed.set_footer(text=f"Total Portfolio Value: {total_value} discoins\nPrevious Value: {prev_total} discoins\nPercent Change: {(((total_value - prev_total) / prev_total) * 100): .2f}")
            await ctx.send(embed=embed)

        except Exception as e:
            await ctx.send("An error occurred while retrieving the portfolio.")
            logging.warning(f"Error: {e}")

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
    
    @commands.hybrid_command()
    async def history(self, ctx, stock_name: str):
        """Returns the historical graph of the given stock."""
        Session = sessionmaker(bind=database.engine)
        session = Session()

        try:
            # Query the stock by name
            stock = session.query(Stock.Stock).filter_by(name=stock_name).first()

            if not stock:
                await ctx.send(f"Stock with name {stock_name} not found.")
                return

            embed = discord.Embed(title=f"{stock_name} Stock History")

            # Attempt to generate the graph
            try:
                # Generate the graph and save it as a BytesIO object
                buf = stock.graph()
                file = discord.File(fp=buf, filename=f"{stock.name}_graph.png")
                embed.set_image(url=f"attachment://{stock.name}_graph.png")
                image_sent = True
            except Exception as e:
                logging.warning(f"Cannot retrieve graph: {e}")
                image_sent = False

            # Send the embed along with the graph file if available
            if image_sent:
                await ctx.send(embed=embed, file=file)
            else:
                await ctx.send(embed=embed)
        finally:
            session.close()
        

    
async def setup(bot):
    await bot.add_cog(Stocks(bot))