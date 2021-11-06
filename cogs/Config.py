from discord.ext import commands
import os
import requests
import discord 
from dotenv import load_dotenv

load_dotenv()
insertPURL = os.getenv('IP_URL')
deletePURL = os.getenv('DP_URL')
geturl = os.getenv('GET_URL')

class Config(commands.Cog, name="Configuration"):
    def __init__(self, bot):
        self.bot = bot

    @commands.Cog.listener()
    async def on_ready(self):
        print(f"{self.__class__.__name__} Cog has been loaded\n----")

    @commands.command()
    async def prefix(self, ctx, new_prefix=None):
        if(new_prefix):
            obj = {"f1": ctx.message.guild.id, "f2": new_prefix}
            result = requests.post(insertPURL, data=obj, headers={"User-Agent": "XY"})
            print(result.status_code)
            await ctx.send(f"Changed the prefix to: {new_prefix}")  
        else:
            await ctx.send("Please input a new prefix.")

def setup(bot):
    bot.add_cog(Config(bot))