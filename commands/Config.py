from discord.ext import commands
import os
import requests
import discord 
from dotenv import load_dotenv
from sqlalchemy.orm import sessionmaker

from classes import Servers, User, database

async def addAccount(user, session):
    u = User.User(user=user)
    session.add(u)
    session.commit()
    
async def hasAccount(ctx):
    user = ctx.author
    Session = sessionmaker(bind=database.engine)
    session = Session()
    try:
        u = session.query(User.User).filter_by(user_id=user.id).first()
        if u:
            return True
        else:
            await addAccount(user, session)
            return True
    finally:
        session.commit()
        session.close()

class Config(commands.Cog, name="Configuration"):
    def __init__(self, bot):
        self.bot = bot

    @commands.Cog.listener()
    async def on_ready(self):
        print(f"{self.__class__.__name__} Cog has been loaded\n----")

    @commands.command(description="Allows the user to change the prefix of the bot")
    async def prefix(self, ctx, new_prefix=None):
        if new_prefix:
            Session = sessionmaker(bind=database.engine)
            session = Session()
            try:
                s = session.query(Servers.Servers).filter_by(server_id=ctx.guild.id).first()
                s.prefix = new_prefix
                await ctx.send(f"Successfully changed prefix to {new_prefix}")
            finally:
                session.commit()
                session.close()
        else:
            await ctx.send("Please input a new prefix.")

async def setup(bot):
    await bot.add_cog(Config(bot))
