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
        return interaction.user.id in allowed_ids
    return app_commands.check(predicate)

class Admin(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

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
    @allowed()
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
    async def randomize_jobs(self, interaction: discord.Interaction):
        Session = sessionmaker(bind=database.engine)
        session = Session()
        try:
            servers = session.query(Servers.Servers).all()
            for server in servers:
                # Get a random list of jobs
                jobs_query = session.query(Jobs.Jobs).order_by(func.rand()).limit(random.randint(3, 6)).all()
                job_names = [job.name for job in jobs_query]
                
                # Update the server's jobs with the new list of job names
                server.jobs = job_names

            # Commit the changes to the database
            session.commit()
            
            await interaction.response.send_message("Success")
        except Exception as e:
            await interaction.response.send_message(f"Failed because {e}")
        finally:
            session.close()

async def setup(bot):
    await bot.add_cog(Admin(bot))