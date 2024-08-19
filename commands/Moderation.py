from ast import alias
from discord.ext import commands
import discord
import math
from datetime import datetime, timedelta
from dotenv import load_dotenv
import requests
import os 
from sqlalchemy.orm import sessionmaker

from classes import Servers, User, database

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
        isBanned = requests.get(getUser, params={'f1': 'blacklisted', 'f2': user.id}, headers={'User-Agent': 'XY'})
        reasonReq = requests.get(getUser, params={'f1': 'reason', 'f2': user.id}, headers={'User-Agent': 'XY'})
        if (isBanned.text == 1):
            await ctx.reply(f"User [{user.name}] is already banned because of [{reasonReq.text}]")

        blReq = requests.post(updateUser, data={"f1": "blacklisted", "f2": 1, "f3": user.id}, headers={"User-Agent": "XY"})
        reasReq = requests.post(updateUser, data={"f1": "reason", "f2": reason, "f3": user.id}, headers={"User-Agent": "XY"})
        await ctx.reply(f"User {user.name} has been banned for reason: [{reason}].")
    
    @commands.hybrid_command(name="unban", aliases=['unblacklist, ubl'], hidden=True, with_app_command=True)
    @commands.is_owner()
    async def unban(self, ctx: commands.Context, user: discord.User):
        isBanned = requests.get(getUser, params={'f1': 'blacklisted', 'f2': user.id}, headers={'User-Agent': 'XY'})
        if (isBanned.text == 0):
            await ctx.reply(f"User [{user.name}] is not banned.")

        blReq = requests.post(updateUser, data={"f1": "blacklisted", "f2": 0, "f3": user.id}, headers={"User-Agent": "XY"})
        reasReq = requests.post(updateUser, data={"f1": "reason", "f2": '', "f3": user.id}, headers={"User-Agent": "XY"})
        await ctx.reply(f"User {user.name} has been unbanned.")

async def setup(bot):
    await bot.add_cog(Moderation(bot))
    