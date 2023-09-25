from ast import alias
from discord.ext import commands
import discord
import math
from datetime import datetime, timedelta
from dotenv import load_dotenv
import requests
import os 

load_dotenv()
getUser = os.getenv('GET_USER')
updateUser = os.getenv('UPDATE_USER')
addUser = os.getenv('ADD_USER')

class Moderation(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.Cog.listener()
    async def on_ready(self):
        print(f"{self.__class__.__name__} Cog has been loaded\n----")
    
    @commands.command()
    async def purge(self, ctx, num):
        return
    
    @commands.hybrid_command(name="ban", aliases=['blacklist, bl'], hidden=True, with_app_command=True)
    @commands.is_owner()
    async def ban(self, ctx: commands.Context, user: discord.User, reason: str):
        requests.post(updateUser, data={"f1": "blacklisted", "f2": 1, "f3": user}, headers={"User-Agent": "XY"})
        requests.post(updateUser, data={"f1": "reason", "f2": reason, "f3": user}, headers={"User-Agent": "XY"})

        await ctx.reply(f"User {user.name} has been banned for reason: [{reason}].")

async def setup(bot):
    await bot.add_cog(Moderation(bot))
    