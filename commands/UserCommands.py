from discord.ext import commands, tasks
import discord
from discord import app_commands
from dotenv import load_dotenv
import os
from sqlalchemy.orm import sessionmaker
from classes import Servers, User, database, Jobs, JobSelector
from .Config import hasAccount
from datetime import datetime, timedelta
import logging
import random
import json

class UserCommands(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.dailyFunds = 250
        self.weeklyFunds = 2500

    @commands.Cog.listener()
    async def on_ready(self):
        print(f"{self.__class__.__name__} Cog has been loaded\n----")

    @commands.hybrid_command(aliases=['loan', 'lend'], description="Simple function that allows users to give discoins to other users.")
    @commands.check(hasAccount)
    async def give(self, ctx, user: discord.User, amount: int):
        author = ctx.author
        if amount == 0:
            await ctx.send("Why are you trying to give someone nothing? What is wrong with you?")
            return
        if amount < 0:
            await ctx.send("You can't give someone negative discoins. Are you dumb?")
            return

        Session = sessionmaker(bind=database.engine)
        session = Session()

        try:
            u = session.query(User.User).filter_by(user_id=author.id).first()

            if not u or u.balance < amount:
                await ctx.send("You don't have enough money. Next time don't bite off more than you can chew.")
                return

            if author.id == user.id:
                await ctx.send("Are you that lonely that you have to give yourself money? Sad.")
                return

            g = session.query(User.User).filter_by(user_id=user.id).first()
            if not g:
                await ctx.send("The recipient does not have an account.")
                return

            u.balance -= amount
            u.total_gifted += amount
            g.balance += amount

            session.commit()

            await ctx.send(f"**{ctx.author.name}#{ctx.author.discriminator}** just gave **{amount}** discoin(s) to **{user.name}#{user.discriminator}**")
        finally:
            session.close()

    @commands.command(description="This function allows the user to see various stats about their activities on the server.")
    @commands.check(hasAccount)
    async def stats(self, ctx, user: discord.User = None):
        user = user or ctx.author
        embed = discord.Embed(title="User Stats", description=f"Showing {user.name}'s stats")

        Session = sessionmaker(bind=database.engine)
        session = Session()

        try:
            u = session.query(User.User).filter_by(user_id=user.id).first()
            if not u:
                await ctx.send("No stats available.")
                return

            embed.add_field(name="Total Earned", value=f"**{u.total_earned}** discoins earned", inline=False)
            embed.add_field(name="Total Lost", value=f"**{u.total_lost}** discoins lost", inline=False)
            embed.add_field(name="Total Given", value=f"**{u.total_gifted}** discoins given to other players", inline=False)
            embed.add_field(name="Bets Made", value=f"**{u.total_bets}** gambles attempted", inline=False)
            embed.add_field(name="Messages Sniped", value=f"**{u.total_snipes}** unique messages sniped", inline=False)

            await ctx.channel.send(embed=embed)
        finally:
            session.close()

    @commands.hybrid_command(name="setsnipe", hidden=True, with_app_command=True)
    async def set_snipe(self, ctx, *, msg: str):
        user = ctx.author

        Session = sessionmaker(bind=database.engine)
        session = Session()

        try:
            u = session.query(User.User).filter_by(user_id=user.id).first()
            if not u:
                await ctx.send("No account found.")
                return

            u.snipe_message = msg
            session.commit()

            await ctx.send(f"You changed your snipe message to [{u.snipe_message}]")
        finally:
            session.close()

    @commands.hybrid_command(description="Display the user's profile.")
    @commands.check(hasAccount)
    async def profile(self, ctx, user: discord.User = None):
        user = user or ctx.author
        embed = discord.Embed(title="User Profile", description=f"Showing {user.name}'s Profile", color=discord.Color.green())

        Session = sessionmaker(bind=database.engine)
        session = Session()

        try:
            u = session.query(User.User).filter_by(user_id=user.id).first()
            if not u:
                await ctx.send("No profile available.")
                return

            embed.set_author(name=user.name, icon_url=user.display_avatar)
            embed.add_field(name="Snipe Message", value=f"**{u.snipe_message}**", inline=False)
            embed.add_field(name="Balance", value=f"**{u.balance}** discoins", inline=False)
            embed.add_field(name="Poll Gamba", value=f"**{u.poll_gamba}** discoins", inline=False)

            await ctx.send(embed=embed)
        finally:
            session.close()

    @commands.hybrid_command(description="Check the user's balance.")
    @commands.check(hasAccount)
    async def bal(self, ctx, user: discord.User = None):
        user = user or ctx.author

        Session = sessionmaker(bind=database.engine)
        session = Session()

        try:
            u = session.query(User.User).filter_by(user_id=user.id).first()
            if not u:
                await ctx.send("No account found.")
                return

            await ctx.send(f"**{user.name}** has `{u.balance}` discoins")
        finally:
            session.close()

    @commands.hybrid_command()
    async def daily(self, ctx):
        Session = sessionmaker(bind=database.engine)
        session = Session()

        try:
            u = session.query(User.User).filter_by(user_id=ctx.author.id).first()
            logging.warning(u.daily_cooldown)
            dailyCD = u.daily_cooldown
            now = datetime.now()
            
            if (now - dailyCD).days >= 1:
                u.balance += self.dailyFunds
                u.total_earned += self.dailyFunds
                u.daily_cooldown = now
                session.commit()  # Commit the changes to the database
                await ctx.send(f"You have earned {self.dailyFunds} discoins")
            else:
                # Calculate the remaining time
                time_left = timedelta(days=1) - (now - dailyCD)
                hours, remainder = divmod(time_left.total_seconds(), 3600)
                minutes, _ = divmod(remainder, 60)

                if hours >= 1:
                    await ctx.send(f"Your daily reward will be available in {int(hours)} hour(s) and {int(minutes)} minute(s).")
                else:
                    await ctx.send(f"Your daily reward will be available in {int(minutes)} minute(s).")
        finally:
            session.close()

    @commands.hybrid_command()
    async def weekly(self, ctx):
        Session = sessionmaker(bind=database.engine)
        session = Session()

        try:
            u = session.query(User.User).filter_by(user_id=ctx.author.id).first()
            weeklyCD = u.weekly_cooldown
            now = datetime.now()
            
            if (now - weeklyCD).days >= 7:
                u.balance += self.weeklyFunds
                u.total_earned += self.weeklyFunds
                u.weekly_cooldown = now
                session.commit()  # Commit the changes to the database
                await ctx.send(f"You have earned {self.weeklyFunds} discoins")
            else:
                # Calculate the remaining time
                time_left = timedelta(days=7) - (now - weeklyCD)
                days, remainder = divmod(time_left.total_seconds(), 86400)  # 86400 seconds in a day
                hours, remainder = divmod(remainder, 3600)
                minutes, _ = divmod(remainder, 60)

                if days >= 1:
                    await ctx.send(f"Your weekly reward will be available in {int(days)} day(s), {int(hours)} hour(s), and {int(minutes)} minute(s).")
                elif hours >= 1:
                    await ctx.send(f"Your weekly reward will be available in {int(hours)} hour(s) and {int(minutes)} minute(s).")
                else:
                    await ctx.send(f"Your weekly reward will be available in {int(minutes)} minute(s).")
        finally:
            session.close()

    @commands.hybrid_command()
    async def apply(self, ctx):
        Session = sessionmaker(bind=database.engine)
        session = Session()
        guild = ctx.guild

        try:
            # Get the server entry
            s = session.query(Servers).filter_by(server_id=guild.id).first()
            u = session.query(User).filter_by(user_id=ctx.author.id).first()

            if not s or not u:
                await ctx.send("Server or user not found.")
                return

            # s.jobs is now a JSON column, which is automatically handled as a Python list
            jobs = []
            for job_name in s.jobs:
                j = session.query(Jobs).filter_by(name=job_name).first()
                if j:
                    jobs.append((job_name, j.chance))

            if not jobs:
                await ctx.send("No jobs available.")
                return

            # Use JobSelector to choose a job
            js = JobSelector(jobs)
            selected_job = js.choose_job()

            # Update or add the new job for the given server_id in user's jobs
            current_jobs = json.loads(u.jobs) if u.jobs else {}
            current_jobs[str(guild.id)] = selected_job

            # Convert the dictionary back to JSON and update the jobs column
            u.jobs = json.dumps(current_jobs)

            # Commit the changes to the database
            session.commit()

            await ctx.send(f"Congratulations! You are now a(n) {selected_job[0]}! You make {selected_job[1]} every time you work.")
        finally:
            session.close()

    @commands.hybrid_command()
    async def jobs(self, ctx):
        guild = ctx.guild
        if not guild:
            await ctx.send("This command can only be used in a server.", ephemeral=True)
            return

        Session = sessionmaker(bind=database.engine)
        session = Session()

        try:
            server = session.query(Servers).filter_by(server_id=guild.id).first()
            if not server:
                await ctx.send("Server not found in the database.", ephemeral=True)
                return

            jobs = json.loads(server.jobs) if server.jobs else []

            embed = discord.Embed(title=f"Jobs in {guild.name}", color=discord.Color.blue())
            if jobs:
                for job_name, salary in jobs.items():
                    embed.add_field(name=job_name, value=f"Salary: {salary} discoins", inline=False)
            else:
                embed.description = "No jobs found for this server."

            await ctx.send(embed=embed)

        except Exception as e:
            await ctx.send("An error occurred while retrieving the jobs.", ephemeral=True)
            print(f"Error: {e}")

        finally:
            session.close()

async def setup(bot):
    await bot.add_cog(UserCommands(bot))
