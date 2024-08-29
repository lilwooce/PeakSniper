from discord.ext import commands, tasks
import os
import requests
import discord 
from dotenv import load_dotenv
from sqlalchemy.orm import sessionmaker
from sqlalchemy.sql.expression import func
import datetime
import random
import json
from zoneinfo import ZoneInfo

from classes import Servers, User, database, Jobs
eastern = ZoneInfo("America/New_York")

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
        self.randomize_jobs.start()

    @commands.Cog.listener()
    async def on_ready(self):
        print(f"{self.__class__.__name__} Cog has been loaded\n----")
    
    def cog_unload(self):
        self.randomize_jobs()

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

    def weigh_jobs(self, jobs):
        if len(jobs) <= 0:
            return {}
        total_weight = sum((weight) for _, weight in jobs)
        normalized_weights = [((weight / total_weight) * 100) for _, weight in self.jobs]
        ret = {}
        for name, weight in jobs:
            ret[name] = weight
        return ret
        

    time = datetime.time(hour=20, tzinfo=eastern)
    @tasks.loop(time=time)
    async def randomize_jobs(self):
        Session = sessionmaker(bind=database.engine)
        session = Session()
        try:
            servers = session.query(Servers.Servers).all()
            for server in servers:
                # Get a random list of jobs
                jobs_query = session.query(Jobs.Jobs).order_by(func.rand()).limit(random.randint(3, 6)).all()
                jobs = self.weigh_jobs(jobs_query)

                server.jobs = json.dumps(jobs)

            # Commit the changes to the database
            session.commit()
        finally:
            session.close()

async def setup(bot):
    await bot.add_cog(Config(bot))
