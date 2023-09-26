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

class Admin(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.Cog.listener()
    async def on_ready(self):
        print(f"{self.__class__.__name__} Cog has been loaded\n----")

    @commands.hybrid_command(name="addmoney", aliases=["am"], hidden=True, with_app_command=True)
    @commands.is_owner()
    async def addmoney(self, ctx: commands.Context, user: discord.User, amount: int):
        print("adding money")
        bal = requests.get(getUser, params={"f1": "discoins", "f2": user}, headers={"User-Agent": "XY"})
        bal = bal.text.replace('"', '')
        print(int(bal))
        result = requests.post(updateUser, data={"f1": "discoins", "f2": int(bal)+amount, "f3": user}, headers={"User-Agent": "XY"})
        print(result)
        if (amount < 0) :
            await ctx.reply(f"Removed {amount * -1} discoin(s) from {user}")
        else:
            await ctx.reply(f"Added {amount} discoin(s) to {user}")
    
    @commands.command(hidden=True)
    @commands.guild_only()
    async def sync(self, ctx: commands.Context) -> None:
        synced = await ctx.bot.tree.sync()
        await ctx.send(
            f"Synced {len(synced)} commands to the current guild."
        )
        return

async def setup(bot):
    await bot.add_cog(Admin(bot))