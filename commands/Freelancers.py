import discord
from discord.ext import commands
from sqlalchemy.orm import Session, sessionmaker
from sqlalchemy.exc import NoResultFound
from classes import Servers, User, database, Jobs, Global, Freelancers
import json
from sqlalchemy.sql.expression import func
import random
import asyncio

class FreelancerCog(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.min_num = 2
        self.max_num = 4

    @commands.hybrid_command(aliases=['fl'])
    async def freelancers(self, ctx):
        Session = sessionmaker(bind=database.engine)
        session = Session()
        
        """Lists all currently available freelancers."""
        freelancers = session.query(Freelancers.Freelancer).filter_by(is_free=True).order_by(func.rand()).all()
        
        if not freelancers:
            await ctx.send("No freelancers are available at the moment.")
            return
        
        # Prepare to paginate
        embeds = []
        freelancers_per_page = 5
        total_pages = (len(freelancers) + freelancers_per_page - 1) // freelancers_per_page

        for page in range(total_pages):
            embed = discord.Embed(title=f"Available Freelancers (Page {page + 1}/{total_pages})", color=discord.Color.blue())
            start = page * freelancers_per_page
            end = start + freelancers_per_page

            for freelancer in freelancers[start:end]:
                embed.add_field(
                    name=freelancer.name, 
                    value=f"Job: {freelancer.job_title}\n"
                        f"Initial Cost: {freelancer.initial_cost}\n"
                        f"Daily Expense: {freelancer.daily_expense}\n"
                        f"Poach Minimum: {freelancer.poach_minimum}\n"
                        f"Type: {freelancer.type_of}", 
                    inline=False
                )
            
            embeds.append(embed)

        # Send the embeds with pagination
        if embeds:
            message = await ctx.send(embed=embeds[0])
            page = 0

            if len(embeds) > 1:
                await message.add_reaction("◀️")
                await message.add_reaction("▶️")

            def check(reaction, user):
                return user == ctx.author and str(reaction.emoji) in ["◀️", "▶️"] and reaction.message.id == message.id
            
            session.close()
            while True:
                try:
                    reaction, user = await self.bot.wait_for("reaction_add", timeout=60.0, check=check)

                    if str(reaction.emoji) == "▶️" and page < len(embeds) - 1:
                        page += 1
                        await message.edit(embed=embeds[page])
                    elif str(reaction.emoji) == "◀️" and page > 0:
                        page -= 1
                        await message.edit(embed=embeds[page])

                    await message.remove_reaction(reaction, user)
                except asyncio.TimeoutError:
                    await message.clear_reactions()
                    break
        else:
            session.close()


    @commands.hybrid_command()
    async def hire(self, ctx, name: str):
        Session = sessionmaker(bind=database.engine)
        session = Session()
        """Hire a freelancer if available."""
        try:
            freelancer = session.query(Freelancers.Freelancer).filter_by(name=name, is_free=True).first()

            if not freelancer:
                await ctx.send(f"{name} was not found in shop.")
                return

            u = session.query(User.User).filter_by(user_id=ctx.author.id).first()

            if not u:
                await ctx.send("User not found.")
                return

            if u.balance < freelancer.initial_cost:
                await ctx.send("You cannot afford to hire this person.")
                return

            u.balance -= freelancer.initial_cost
            freelancers = json.loads(u.freelancers) if u.freelancers else {}
            freelancers[freelancer.name] = freelancer.type_of
            u.freelancers = json.dumps(freelancers)
            freelancer.boss = ctx.author.id
            freelancer.is_free = False
            session.commit()
            await ctx.send(f"{ctx.author.mention}, you successfully hired {name}!")
        except NoResultFound:
            await ctx.send(f"{ctx.author.mention}, {name} is not available or doesn't exist.")
    
    @commands.hybrid_command()
    async def fire(self, ctx, freelancer_name: str):
        Session = sessionmaker(bind=database.engine)
        session = Session()
        """Fire a freelancer you currently employ."""
        try:
            freelancer = session.query(Freelancers.Freelancer).filter_by(name=freelancer_name, boss=ctx.author.id).first()

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
            freelancer = session.query(Freelancers.Freelancer).filter_by(name=freelancer_name, is_free=False).first()

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
            freelancer = session.query(Freelancers.Freelancer).filter_by(name=freelancer_name).first()

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
