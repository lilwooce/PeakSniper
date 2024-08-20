from ast import alias
from discord.ext import commands
import discord
import math
from datetime import datetime, timedelta
from dotenv import load_dotenv
import requests
import os 
from .Config import hasAccount
from sqlalchemy.orm import sessionmaker

from classes import Servers, User, database

load_dotenv()
getUser = os.getenv('GET_USER')
updateUser = os.getenv('UPDATE_USER')
addUser = os.getenv('ADD_USER')
header={"User-Agent": "XY"}

class UserCommands(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.Cog.listener()
    async def on_ready(self):
        print(f"{self.__class__.__name__} Cog has been loaded\n----")
    
    @commands.hybrid_command(aliases=['loan', 'lend'], description="Simple function that allows users to give discoins to other users. The gifted discoins are removed from the givers account.")
    @commands.check(hasAccount)
    async def give(self, ctx, user: discord.User, amount: int):
        author = ctx.author
        Session = sessionmaker(bind=database.engine)
        session = Session()
        u = session.query(User.User).filter_by(user_id=author.id).first()

        if (amount == 0):
            await ctx.send("Why are you trying to give someone nothing? What is wrong with you?")
            return

        if (amount >= 1):
            if(author.id != user.id):
                if (amount <= int(u.balance)):
                    g = session.query(User.User).filter_by(user_id=user.id).first()

                    u.balance -= amount
                    u.total_gifted += amount
                    g.balance += amount
                    
                    session.commit()
                    session.close()

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
        user = user or ctx.author
        
        embed = discord.Embed(title="User Stats", description=f"Showing {user.name}'s stats")
        Session = sessionmaker(bind=database.engine)
        session = Session()
        u = session.query(User.User).filter_by(user_id=user.id).first()
        total_earned = u.total_earned
        total_lost = u.total_lost
        total_gifted = u.total_gifted
        total_bets = u.total_bets
        total_snipes = u.total_snipes

        embed.add_field(name="Total Earned", value=f"**{total_earned}** discoins earned", inline=False)
        embed.add_field(name="Total Lost", value=f"**{total_lost}** discoins lost", inline=False)
        embed.add_field(name="Total Given", value=f"**{total_gifted}** discoins given to other players", inline=False)
        embed.add_field(name="Bets Made", value=f"**{total_bets}** gambles attempted", inline=False)
        embed.add_field(name="Messages Sniped", value=f"**{total_snipes}** messages sniped", inline=False)

        await ctx.channel.send(embed=embed)

    @commands.hybrid_command(name="setsnipe", hidden=True, with_app_command=True)
    async def set_snipe(self, ctx, msg: str):
        user = ctx.author
        message = ""
        for m in msg:
            message += m

        Session = sessionmaker(bind=database.engine)
        session = Session()
        u = session.query(User.User).filter_by(user_id=user.id).first()
        u.snipe_message = message
        await ctx.send(f"You changed your snipe message to [{u.snipe_message}]")
        session.commit()
        session.close()

    @commands.hybrid_command(description="")
    @commands.check(hasAccount)
    async def profile(self, ctx, user: discord.User=None):
        user = user or ctx.author
        
        embed = discord.Embed(title="User Profile", description=f"Showing {user.name}'s Profile", color=discord.Color.green())
        Session = sessionmaker(bind=database.engine)
        session = Session()
        u = session.query(User.User).filter_by(user_id=user.id).first()
        snipe_message = u.snipe_message
        balance = u.balance
        
        embed.set_author(name=user.name, icon_url=user.display_avatar)
        embed.add_field(name="Snipe Message", value=f"**{snipe_message}**", inline=False)
        embed.add_field(name="Balance", value=f"**{balance}** discoins ", inline=False)

        await ctx.send(embed=embed)

async def setup(bot):
    await bot.add_cog(UserCommands(bot))

