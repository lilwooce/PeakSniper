from ast import alias
from discord.ext import commands
import discord
import math
from datetime import datetime, timedelta
from dotenv import load_dotenv
import requests
import os 
from .Config import hasAccount

load_dotenv()
getUser = os.getenv('GET_USER')
updateUser = os.getenv('UPDATE_USER')
addUser = os.getenv('ADD_USER')
header={"User-Agent": "XY"}

class User(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.Cog.listener()
    async def on_ready(self):
        print(f"{self.__class__.__name__} Cog has been loaded\n----")
    
    @commands.command(aliases=['bal'], description="This function returns the current amount of discoins you currently have.")
    @commands.check(hasAccount)
    async def balance(self, ctx, user: discord.User=None):
        if user is None:
            user = ctx.message.author

        checkBalance = requests.get(getUser, params={"f1": "discoins", "f2": user.id}, headers=header)
        checkBalance = checkBalance.text.replace('"', '')

        await ctx.channel.send(f"{user.name}#{user.discriminator} currently has {checkBalance} discoin(s).")
    
    @commands.command(description="Returns the amount of snipes the user has done, this function is often used to determine the top snipers for the Kyle award.")
    @commands.check(hasAccount)
    async def snipes (self, ctx, user: discord.User=None):
        if user is None:
            user = ctx.message.author

        checkSnipes = requests.get(getUser, params={"f1": "snipes", "f2": user.id}, headers=header)
        checkSnipes = checkSnipes.text.replace('"', '')

        await ctx.channel.send(f"{user.name}#{user.discriminator} has sniped a total of {checkSnipes} message(s).")
    
    @commands.command(aliases=['loan', 'lend'], description="Simple function that allows users to give discoins to other users, this is often used to pay for lunch if lunch was paid in discoins that would be another topic. The gifted discoins are removed from the givers account.")
    @commands.check(hasAccount)
    async def give(self, ctx, user: discord.User, amount: int):
        userID = ctx.author.id
        bal = requests.get(getUser, params={"f1": "discoins", "f2": userID}, headers={"User-Agent": "XY"})
        bal = bal.text.replace('"', '')
        if (amount == 0):
            await ctx.send("Why are you trying to give someone nothing? What is wrong with you?")
            return

        if (amount >= 1):
            if(userID != user.id):
                if (amount <= int(bal)):
                    gBal = requests.get(getUser, params={"f1": "discoins", "f2": user.id}, headers={"User-Agent": "XY"})
                    gBal = gBal.text.replace('"', '')
                    totalGiven = requests.get(getUser, params={"f1": "totalGiven", "f2": user.id}, headers=header)
                    requests.post(updateUser, data={"f1": "discoins", "f2": int(bal)-amount, "f3": userID}, headers={"User-Agent": "XY"})
                    requests.post(updateUser, data={"f1": "discoins", "f2": int(gBal)+amount, "f3": user.id}, headers={"User-Agent": "XY"})
                    requests.post(updateUser, data={"f1": "discoins", "f2": int(totalGiven)+amount, "f3": userID}, headers={"User-Agent": "XY"})
                    await ctx.send(f"**{ctx.author.name}#{ctx.author.discriminator}** just gave **{amount}** discoin(s) to **{user.name}#{user.discriminator}**")
                else:
                    await ctx.send("You don't have enough money. Next time don't bite off more than you can chew.")
            else:
                await ctx.send("Are you that lonely that you have to give yourself money? Sad.")
        else:
            await ctx.send("You can't give someone negative discoins. Are you dumb?")
        
    @commands.command(description="This function allows the user to see a lot of different stats about what he has done on the server, most of these aren't useful but will definitely increase bragging rights. Stats returned include; total amount of discoins earned, lost and given. The total number of bets made is the degenerates stat of the year.")
    @commands.check(hasAccount)
    async def stats(self, ctx, user: discord.User=None):
        if user is None:
            user = ctx.message.author
        
        embed = discord.Embed(title="User Stats", description=f"Showing {user.name}'s stats")

        totalEarned = requests.get(getUser, params={"f1": "totalEarned", "f2": user.id}, headers=header)
        totalEarned = totalEarned.text.replace('"', '')
        totalLost = requests.get(getUser, params={"f1": "totalLost", "f2": user.id}, headers=header)
        totalLost = totalLost.text.replace('"', '')
        totalGiven = requests.get(getUser, params={"f1": "totalGiven", "f2": user.id}, headers=header)
        totalGiven = totalGiven.text.replace('"', '')
        betsMade = requests.get(getUser, params={"f1": "betsMade", "f2": user.id}, headers=header)
        betsMade = betsMade.text.replace('"', '')

        embed.add_field(name="Total Earned", value=f"**{totalEarned}** discoins earned", inline=False)
        embed.add_field(name="Total Lost", value=f"**{totalLost}** discoins lost", inline=False)
        embed.add_field(name="Total Given", value=f"**{totalGiven}** discoins given to other players", inline=False)
        embed.add_field(name="Bets Made", value=f"**{betsMade}** gambles attempted", inline=False)

        await ctx.channel.send(embed=embed)


async def setup(bot):
    await bot.add_cog(User(bot))

