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
import random
import json
import logging

from classes import Servers, User, database, Jobs, ShopItem, Stock

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
        return interaction.user.id in admins
    return app_commands.check(predicate)

class Admin(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.min_num_jobs = 3

    @commands.Cog.listener()
    async def on_ready(self):
        print(f"{self.__class__.__name__} Cog has been loaded\n----")

    

    @commands.hybrid_command(name="addmoney", aliases=["am"], hidden=True, with_app_command=True)
    @commands.is_owner()
    async def addmoney(self, ctx: commands.Context, user: discord.User, amount: int):
        Session = sessionmaker(bind=database.engine)
        session = Session()
        u = session.query(User.User).filter_by(user_id=user.id).first()
        u.balance += amount
        session.commit()
        
        if (amount < 0) :
            await ctx.send(f"Removed {amount * -1} discoin(s) from {user}")
        else:
            await ctx.send(f"Added {amount} discoin(s) to {user}")

    @commands.hybrid_command(name="message", aliases=["msg"], hidden=True, with_app_command=True)
    @commands.is_owner()
    async def message(self, ctx: commands.Context, channel: discord.TextChannel, message: str):
        await channel.send(message)
        await ctx.send(f"message: [{message}] sent to {channel.name}")
    
    @app_commands.command()
    @admins_only()
    async def add_job(self, interaction: discord.Interaction, name: str, salary: int, chance: float):
        Session = sessionmaker(bind=database.engine)
        session = Session()

        try: 
            j = Jobs.Jobs(name, salary, chance)
            session.add(j)
            session.commit()
            await interaction.response.send_message(f"Successfully added a job: name {name}, salary {salary}, chance {chance}")
        finally:
            session.close()
        
    @app_commands.command()
    @allowed()
    async def add_shop_item(self, interaction: discord.Interaction, name: str, price: int, uses: int, command: str, item_type: str, duration: int):
        Session = sessionmaker(bind=database.engine)
        session = Session()

        try: 
            i = ShopItem.ShopItem(name, price, uses, command, item_type, duration)
            session.add(i)
            session.commit()
            await interaction.response.send_message(f"Successfully added a shop item: name {name}, price {price}, uses {uses}, command {command}, type {item_type}, duration {duration} minutes")

        finally:
            session.close()

    @app_commands.command()
    @admins_only()
    async def add_stock(self, interaction: discord.Interaction, name: str, full_name: str, growth_rate: float, start_value:float, volatility: float, swap_chance: float, ruination:float):
        Session = sessionmaker(bind=database.engine)
        session = Session()

        try: 
            s = Stock.Stock(name, full_name, growth_rate, start_value, volatility, swap_chance, ruination)
            session.add(s)
            session.commit()
            await interaction.response.send_message(f"Successfully added a stock item: name {name}, full_name {full_name}, growth_rate {growth_rate}, start_value {start_value}, volatility {volatility}, swap_chance {swap_chance} ruination {ruination}")
        finally:
            session.close()
    
    @app_commands.command()
    @allowed()
    async def add_current_stock(self, interaction: discord.Interaction):
        Session = sessionmaker(bind=database.engine)
        session = Session()

        try: 
            stocks = session.query(Stock.Stock).all()
            if not stocks:
                await interaction.response.send_message("No stocks available at the moment.")
                return

            for i, stock in enumerate(stocks, start=1):
                logging.warning(stock.history)
                stock.history.append(stock.previous_value)
                stock.history.append(stock.current_value)
                logging.warning(stock.history)
                session.add(stock)
            session.commit()
            await interaction.response.send_message("Success")
        finally:
            session.close()

    def weigh_jobs(self, jobs):
        if len(jobs) <= 0:
            return {}

        # Invert the salary values: higher salary becomes a lower weight
        inverted_weights = []
        for job in jobs:
            if job.chance > 0:
                logging.warning(f"{job.name} | {job.chance}")
                inverted_weights.append(job.chance)
            else:
                logging.warning(f"{job.name} | {job.salary}")
                inverted_weights.append(1 / job.salary)

        logging.warning(inverted_weights)
        # Sum the inverted weights
        total_inverted_weight = sum(inverted_weights)

        # Normalize the inverted weights
        normalized_weights = [(weight / total_inverted_weight) * 100 for weight in inverted_weights]

        ret = {}
        for job, weight in zip(jobs, normalized_weights):  # Zip through jobs and normalized weights
            ret[job.name] = weight  # Assign the normalized weight to the corresponding job name
            logging.warning(f"{job.name} | {ret[job.name]} % chance")

        return ret


    @app_commands.command()
    @allowed()
    async def randomize_jobs(self, interaction: discord.Interaction):
        guild = interaction.guild
        Session = sessionmaker(bind=database.engine)
        session = Session()
        try:
            server = session.query(Servers.Servers).filter_by(server_id=guild.id)
            # Get a random list of jobs
            jobs_query = session.query(Jobs.Jobs).order_by(func.rand()).limit(random.randint(self.min_num_jobs, self.min_num_jobs*2)).all()
            jobs = self.weigh_jobs(jobs_query)

            server.jobs = json.dumps(jobs)
            logging.warning(jobs)
            logging.warning(server.jobs)
            # Commit the changes to the database
            session.commit()
            logging.warning(server.jobs)
            
            await interaction.response.send_message("Success")
        except Exception as e:
            await interaction.response.send_message(f"Failed because {e}")
        finally:
            session.close()
    
    @commands.hybrid_command()
    @allowed()
    async def give_item(self, ctx, user: discord.User, amount: int, name: str):
        Session = sessionmaker(bind=database.engine)
        
        with Session() as session:
            try:
                item = session.query(ShopItem.ShopItem).filter_by(name=name).first()
                if not item:
                    await ctx.send(f"{name} was not found in shop.")
                    return

                u = session.query(User.User).filter_by(user_id=user.id).first()

                if not u:
                    await ctx.send("User not found.")
                    return
                
                inven = json.loads(u.inventory) if u.inventory else {}
                inven[item.name] = inven.get(item.name, 0) + amount
                u.inventory = json.dumps(inven)

                session.commit()
                await ctx.send(f"You have given {amount} {name}(s).")
            except Exception as e:
                print(f"Error in give items command: {e}")
                await ctx.send("An error occurred while giving the items.")

async def setup(bot):
    await bot.add_cog(Admin(bot))