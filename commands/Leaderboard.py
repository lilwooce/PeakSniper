from discord.ext import commands
import os
import requests
import discord 
import random
from dotenv import load_dotenv
from asyncio import gather
import asyncio
from .Config import hasAccount
from classes import User, Servers, database
import io
import asyncio
from discord import app_commands, File
from sqlalchemy import update, desc
from sqlalchemy.orm import sessionmaker
from classes.database import engine
import random

load_dotenv()

class Leaderboard(commands.Cog, name="Leaderboard"):
    def __init__(self, client: commands.Bot):
        self.client = client
    
    @app_commands.command(name="leaderboard")
    async def leaderboard(self, interaction: discord.Interaction):
        Session = sessionmaker(bind=database.engine)
        session = Session()
        guild = interaction.guild
        users = [member.id for member in guild.members if not member.bot]
        embed = discord.Embed(title=f"Richest Users in {guild.name}")
        database_users = session.query(User.User).order_by(desc(User.User.balance)).all()
        for u in database_users:
            print(f"{u.name}: {u.balance}")
            if u.user_id in users:
                embed.add_field(name=u.name, value=f"{u.balance}", inline=False)
        await interaction.response.send_message(embed=embed)

        

async def setup(bot):
    await bot.add_cog(Leaderboard(bot)) 