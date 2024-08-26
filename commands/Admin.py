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

from classes import Servers, User, database, Jobs

load_dotenv()
getUser = os.getenv('GET_USER')
updateUser = os.getenv('UPDATE_USER')
addUser = os.getenv('ADD_USER')

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
    @commands.is_owner()
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

    async def randomize_jobs(self, interaction: discord.Interaction):
        Session = sessionmaker(bind=database.engine)
        session = Session()
        try:
            servers = session.query(Servers).all()
            for server in servers:
                # Get a random list of jobs
                jobs_query = session.query(Jobs).order_by(func.rand()).limit(random.randint(3, 6)).all()
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