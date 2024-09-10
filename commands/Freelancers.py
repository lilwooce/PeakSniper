import discord
from discord.ext import commands
from sqlalchemy.orm import Session, sessionmaker
from sqlalchemy.exc import NoResultFound
from classes import Servers, User, database, Jobs, Global, Freelancers

class FreelancerCog(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.hybrid_command(aliases=['fl'])
    async def freelancers(self, ctx):
        Session = sessionmaker(bind=database.engine)
        session = Session()
        """Lists all currently available freelancers."""
        freelancers = session.query(Freelancers.Freelancer).filter_by(is_free=True).all()

        if not freelancers:
            await ctx.send("No freelancers are available at the moment.")
            return
        
        embed = discord.Embed(title="Available Freelancers")
        for freelancer in freelancers:
            embed.add_field(
                name=freelancer.name, 
                value=f"Job: {freelancer.job_title}\n"
                      f"Initial Cost: {freelancer.initial_cost}\n"
                      f"Daily Expense: {freelancer.daily_expense}\n"
                      f"Poach Minimum: {freelancer.poach_minimum}\n"
                      f"Type: {freelancer.type_of}", 
                inline=False
            )
        
        await ctx.send(embed=embed)

    @commands.hybrid_command()
    async def hire(self, ctx, freelancer_name: str):
        Session = sessionmaker(bind=database.engine)
        session = Session()
        """Hire a freelancer if available."""
        try:
            freelancer = session.query(Freelancers.Freelancer).filter_by(name=freelancer_name, is_free=True).one()

            # Here, you would check if the user can afford the freelancer and proceed accordingly
            # Assuming user has enough money and meets the conditions
            freelancer.boss = ctx.author.id
            freelancer.is_free = False
            session.commit()
            await ctx.send(f"{ctx.author.mention}, you successfully hired {freelancer_name}!")
        except NoResultFound:
            await ctx.send(f"{ctx.author.mention}, {freelancer_name} is not available or doesn't exist.")
    
    @commands.hybrid_command()
    async def fire(self, ctx, freelancer_name: str):
        Session = sessionmaker(bind=database.engine)
        session = Session()
        """Fire a freelancer you currently employ."""
        try:
            freelancer = session.query(Freelancers.Freelancer).filter_by(name=freelancer_name, boss=ctx.author.id).one()

            freelancer.boss = None
            freelancer.is_free = True
            session.commit()
            await ctx.send(f"{freelancer_name} has been fired.")
        except NoResultFound:
            await ctx.send(f"{ctx.author.mention}, you do not have a freelancer named {freelancer_name}.")

    @commands.hybrid_command()
    async def poach(self, ctx, freelancer_name: str):
        Session = sessionmaker(bind=database.engine)
        session = Session()
        """Poach a freelancer from another user."""
        try:
            freelancer = session.query(Freelancers.Freelancer).filter_by(name=freelancer_name, is_free=False).one()

            if freelancer.poach_minimum > ctx.author.balance:
                await ctx.send(f"{ctx.author.mention}, you do not have enough funds to poach {freelancer_name}.")
                return
            
            old_boss = self.bot.get_user(freelancer.boss)
            freelancer.boss = ctx.author.id
            freelancer.is_free = False
            session.commit()

            await ctx.send(f"{ctx.author.mention} successfully poached {freelancer_name} from {old_boss.mention}!")
        except NoResultFound:
            await ctx.send(f"{ctx.author.mention}, {freelancer_name} is not available for poaching.")

    @commands.hybrid_command()
    async def info(self, ctx, freelancer_name: str):
        Session = sessionmaker(bind=database.engine)
        session = Session()
        """See detailed information about a specific freelancer."""
        try:
            freelancer = session.query(Freelancers.Freelancer).filter_by(name=freelancer_name).one()

            embed = discord.Embed(
                title=f"Freelancer: {freelancer.name}",
                description=f"Job Title: {freelancer.job_title}\n"
                            f"Initial Cost: {freelancer.initial_cost}\n"
                            f"Daily Expense: {freelancer.daily_expense}\n"
                            f"Type: {freelancer.type_of}\n"
                            f"Boost Amount: {freelancer.boost_amount}"
            )

            if freelancer.is_free:
                embed.add_field(name="Availability", value="Available for hire", inline=False)
            else:
                boss = self.bot.get_user(freelancer.boss)
                embed.add_field(name="Current Boss", value=boss.mention, inline=False)

            await ctx.send(embed=embed)
        except NoResultFound:
            await ctx.send(f"{ctx.author.mention}, no freelancer named {freelancer_name} found.")

async def setup(bot):
    await bot.add_cog(FreelancerCog(bot))