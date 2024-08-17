from discord.ext import commands
import os
import requests
import discord 
from dotenv import load_dotenv

load_dotenv()
updatePURL = os.getenv('UP_URL')
removePURL = os.getenv('RP_URL')
getPURL = os.getenv('GP_URL')
updateUser = os.getenv('UPDATE_USER')
addUser = os.getenv('ADD_USER')
getUser = os.getenv('GET_USER')
header={"User-Agent": "XY"}

async def addAccount(user):
    obj = {"f1": user}
    r = requests.post(addUser, data=obj, headers=header)
    
async def hasAccount(ctx):
    userID = ctx.author.id
    obj = {"f1": "user", "f2": userID}
    result = requests.get(getUser, params=obj, headers=header)
    id = result.text.replace('"', '')
    if (id == str(userID)):
        return True
    else:
        await addAccount(ctx.author.id)
        return True

class Config(commands.Cog, name="Configuration"):
    def __init__(self, bot):
        self.bot = bot

    @commands.Cog.listener()
    async def on_ready(self):
        print(f"{self.__class__.__name__} Cog has been loaded\n----")

    @commands.command(description="Allows the user to change the prefix of the bot")
    async def prefix(self, ctx, new_prefix=None):
        if(new_prefix):
            obj = {"f1": ctx.message.guild.id, "f2": new_prefix}
            result = requests.post(updatePURL, data=obj, headers={"User-Agent": "XY"})
            print(result.status_code)
            await ctx.send(f"Changed the prefix to: {new_prefix}")  
        else:
            await ctx.send("Please input a new prefix.")

async def setup(bot):
    await bot.add_cog(Config(bot))