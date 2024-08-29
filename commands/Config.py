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
        self.min_num_jobs = 3
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

        total_weight = sum(job.chance for job in jobs)  # Sum of unnormalized chances
        normalized_weights = [(job.chance / total_weight) * 100 for job in jobs]  # Normalize the weights

        ret = {}
        for job, weight in zip(jobs, normalized_weights):  # Zip through jobs and normalized weights
            ret[job.name] = weight  # Assign the normalized weight to the corresponding job name

        return ret

        

    time = datetime.time(hour=[8,20], tzinfo=eastern)
    @tasks.loop(time=time)
    async def randomize_jobs(self, ctx):
        Session = sessionmaker(bind=database.engine)
        session = Session()
        try:
            servers = session.query(Servers.Servers).all()
            for server in servers:
                # Get a random list of jobs
                jobs_query = session.query(Jobs.Jobs).order_by(func.rand()).limit(random.randint(self.min_num_jobs, self.min_num_jobs*2)).all()
                jobs = self.weigh_jobs(jobs_query)

                server.jobs = json.dumps(jobs)

            # Commit the changes to the database
            session.commit()
        finally:
            session.close()

async def setup(bot):
    await bot.add_cog(Config(bot))
