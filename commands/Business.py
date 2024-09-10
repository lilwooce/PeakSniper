import discord
from discord.ext import commands
from sqlalchemy.orm import Session
from sqlalchemy.exc import NoResultFound
from datetime import datetime
from classes import Servers, User, database, Jobs, Global, Businesses

class BusinessCog(commands.Cog):
    def __init__(self, bot, session: Session):
        self.bot = bot
        self.session = session

    @commands.hybrid_command(aliases="bs")
    async def businesses(self, ctx):
        """View all currently available businesses."""
        businesses = self.session.query(Businesses.Businesses.Business).filter_by(owner=None).all()

        if not businesses:
            await ctx.send("No businesses are available at the moment.")
            return

        embed = discord.Embed(title="Available Businesses")
        for business in businesses:
            embed.add_field(
                name=business.name,
                value=f"Purchase Value: {business.purchase_value}\n"
                      f"Type: {business.type_of}\n"
                      f"Daily Expense: {business.daily_expense}\n"
                      f"Daily Revenue: {business.daily_revenue}",
                inline=False
            )
        
        await ctx.send(embed=embed)

    @commands.hybrid_command(name="purchase")
    async def acquire(self, ctx, business_name: str):
        """Purchase a business if available."""
        try:
            business = self.session.query(Businesses.Business).filter_by(name=business_name, owner=None).one()

            # Here you would check if the user can afford the business
            # Assuming user has enough money and meets the conditions
            business.owner = ctx.author.id
            self.session.commit()

            await ctx.send(f"{ctx.author.mention}, you have successfully purchased {business_name}!")
        except NoResultFound:
            await ctx.send(f"{ctx.author.mention}, {business_name} is not available or doesn't exist.")

    @commands.hybrid_command(name="list")
    async def auction(self, ctx, business_name: str, price: int):
        """List a business you own for sale."""
        try:
            business = self.session.query(Businesses.Business).filter_by(name=business_name, owner=ctx.author.id).one()

            business.current_value = price
            business.owner = None  # The business is now listed for sale
            self.session.commit()

            await ctx.send(f"{ctx.author.mention}, {business_name} is now listed for {price}!")
        except NoResultFound:
            await ctx.send(f"{ctx.author.mention}, you do not own {business_name} or it is not available.")

    @commands.hybrid_command(name="business")
    async def details(self, ctx, business_name: str):
        """See detailed information about a business."""
        try:
            business = self.session.query(Businesses.Business).filter_by(name=business_name).one()

            embed = discord.Embed(
                title=f"Business: {business.name}",
                description=f"Purchase Value: {business.purchase_value}\n"
                            f"Current Value: {business.current_value}\n"
                            f"Type: {business.type_of}\n"
                            f"Daily Expense: {business.daily_expense}\n"
                            f"Daily Revenue: {business.daily_revenue}\n"
                            f"Revenue: {business.revenue}\n"
                            f"Expenses: {business.expenses}",
            )

            if business.owner is None:
                embed.add_field(name="Status", value="Available for purchase", inline=False)
            else:
                owner = self.bot.get_user(business.owner)
                embed.add_field(name="Owner", value=owner.mention if owner else "Unknown", inline=False)

            await ctx.send(embed=embed)
        except NoResultFound:
            await ctx.send(f"{ctx.author.mention}, no business named {business_name} found.")

    @commands.hybrid_command(name="mb")
    async def mybiz(self, ctx):
        """View all businesses a user owns."""
        businesses = self.session.query(Businesses.Business).filter_by(owner=ctx.author.id).all()

        if not businesses:
            await ctx.send(f"{ctx.author.mention}, you do not own any businesses.")
            return

        embed = discord.Embed(title=f"{ctx.author.display_name}'s Businesses")
        for business in businesses:
            embed.add_field(
                name=business.name,
                value=f"Current Value: {business.current_value}\n"
                      f"Daily Expense: {business.daily_expense}\n"
                      f"Daily Revenue: {business.daily_revenue}",
                inline=False
            )

        await ctx.send(embed=embed)

async def setup(bot):
    session = Session()  # Replace with your session creation logic
    await bot.add_cog(BusinessCog(bot, session))
