from discord.ext import commands
import discord
from dotenv import load_dotenv
import os
from sqlalchemy.orm import sessionmaker
from classes import Servers, User, database
from .Config import hasAccount

class UserCommands(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

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
            embed.add_field(name="Messages Sniped", value=f"**{u.total_snipes}** messages sniped", inline=False)

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

async def setup(bot):
    await bot.add_cog(UserCommands(bot))
