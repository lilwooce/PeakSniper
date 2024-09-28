from discord.ext import commands, tasks
import os
import requests
import discord 
from dotenv import load_dotenv
from sqlalchemy.orm import sessionmaker
from sqlalchemy.sql.expression import func
import datetime
from datetime import time
import random
import json
from zoneinfo import ZoneInfo
import logging
import math
from classes import Servers, User, database, Jobs, Global, Stock, Assets, Freelancers, Businesses, Houses, EntityGenerator
eastern = ZoneInfo("America/New_York")
time_am = time(hour=8, tzinfo=eastern)  # 8:00 AM Eastern
time_pm = time(hour=20, tzinfo=eastern)  # 8:00 PM Eastern

async def addAccount(user, session):
    u = User.User(user=user)
    session.add(u)
    session.commit()

def handle_amount(amount, to_get):
    if type(amount) == str and amount.lower() in "all":
        amount = to_get
    elif type(amount) == str and amount.lower() in "half":
        amount = to_get / 2
    else:
        amount = int(amount)
    return amount
    
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

# Define update methods for each type of stock
def update_house_value(stock, session):
    house = session.query(Houses.House).filter_by(id=stock.reference_id).first()
    if house:
        house.current_value = stock.current_value
        session.commit()

def update_asset_value(stock, session):
    asset = session.query(Assets.Asset).filter_by(id=stock.reference_id).first()
    if asset:
        asset.current_value = stock.current_value
        session.commit()

def update_business_value(stock, session):
    business = session.query(Businesses.Business).filter_by(id=stock.reference_id).first()
    if business:
        business.current_value = stock.current_value
        session.commit()

class Config(commands.Cog, name="Configuration"):
    def __init__(self, bot):
        self.bot = bot
        self.min_num_jobs = 3
        # Stock type mapping
        self.stock_update_mapping = {
            "house": update_house_value,
            "asset": update_asset_value,
            "business": update_business_value,
        }
        self.daily_generator.start()
        self.randomize_jobs.start()
        self.daily_tax.start()
        self.daily_revenue.start()
        self.update_stocks.start()

    @commands.Cog.listener()
    async def on_ready(self):
        print(f"{self.__class__.__name__} Cog has been loaded\n----")
    
    def cog_unload(self):
        self.daily_generator
        self.randomize_jobs()
        self.daily_tax()
        self.daily_revenue()
        self.update_stocks()

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
    
    def weigh_jobs_salary(self, jobs):
        if len(jobs) <= 0:
            return {}

        # Invert the salary values: higher salary becomes a lower weight
        inverted_weights = []
        for job in jobs:
            if job.chance > 0:
                logging.warning(f"{job.name} | {job.chance}")
                inverted_weights.append(job.chance)
            else:
                logging.warning(f"{job.name} | {job.salary}")
                inverted_weights.append(1 / job.salary)

        logging.warning(inverted_weights)
        # Sum the inverted weights
        total_inverted_weight = sum(inverted_weights)

        # Normalize the inverted weights
        normalized_weights = [(weight / total_inverted_weight) * 100 for weight in inverted_weights]

        ret = {}
        for job, weight in zip(jobs, normalized_weights):  # Zip through jobs and normalized weights
            ret[job.name] = weight  # Assign the normalized weight to the corresponding job name
            logging.warning(f"{job.name} | {ret[job.name]} % chance")

        return ret

    @tasks.loop(time=[time_am, time_pm])
    async def randomize_jobs(self):
        Session = sessionmaker(bind=database.engine)
        session = Session()
        try:
            g = session.query(Global.Global).first()
            # Get a random list of jobs
            jobs_query = session.query(Jobs.Jobs).order_by(func.rand()).limit(random.randint(self.min_num_jobs, self.min_num_jobs*2)).all()
            jobs = self.weigh_jobs_salary(jobs_query)

            g.jobs = json.dumps(jobs)

            # Commit the changes to the database
            session.commit()
        finally:
            session.close()
    
    async def send_reminder(self, id, message):
        user = self.bot.get_user(id)
        if user:
            await user.send(message)

    @tasks.loop(time=[time_pm])
    async def daily_generator(self):
        entity_generator = EntityGenerator.EntityGenerator()
        result_message = entity_generator.generate_and_add_entities()
        print(result_message)  # Or handle it however you prefer

    @tasks.loop(time=[time_pm])
    async def daily_tax(self):
        Session = sessionmaker(bind=database.engine)
        session = Session()
        try:
            users = session.query(User.User).all()
            for u in users:
                if u.balance == 0 and u.in_jail == True:
                    # Don't tax
                    continue
        
                # Get the user's bills
                bills = json.loads(u.bills) if u.bills else {}
                
                if bills and "daily" in bills:
                    # Double the daily tax amount
                    bills["daily"] *= 2
                    
                    # Update the user's bills
                    u.bills = json.dumps(bills)
                else:
                    bills["daily"] = 1000
                    u.bills = json.dumps(bills)
                
                # Check if reminders are enabled
                if u.reminders == True:
                    # Calculate current day (n) based on the daily tax amount
                    n = math.log2(bills["daily"] / 1000) + 1
                    
                    # Calculate days left before going to jail
                    days_left = 7 - n
                    
                    # Send reminder message
                    if days_left > 0:
                        await self.send_reminder(u, f"You have {days_left} days left to pay your bills before you lose your job, all your money, and go to jail.")
                    else:
                        # Handle the case where the user should now go to jail
                        u.in_jail = True
                        u.balance = -10000
                        u.bank = 0
                        u.job = "beggar"
                            
                # Commit the changes to the database
                session.commit()
        finally:
            session.close()

    @tasks.loop(time=[time_pm])
    async def daily_revenue(self):
        Session = sessionmaker(bind=database.engine)
        session = Session()
        try:
            users = session.query(User.User).all()
            for u in users:
                # Load the user's businesses and revenue (if any)
                businesses = json.loads(u.businesses) if u.businesses else {}
                revenue_data = json.loads(u.revenue) if u.revenue else {}

                total_revenue = 0
                total_boost = 0

                # Check if the user has any freelancers of type "assistant" with "wealth" or "business" in their job_name
                freelancers = json.loads(u.freelancers) if u.freelancers else []
                for freelancer in freelancers:
                    if freelancer["job_type"] == "assistant" and (
                        "wealth" in freelancer["job_name"].lower() or "business" in freelancer["job_name"].lower()
                    ):
                        total_boost += freelancer.get("boost_amount", 0)

                # Calculate the revenue for each business
                for business_id, business in businesses.items():
                    daily_revenue = business.get("daily_revenue", 0)

                    # Apply the boost to the revenue
                    boosted_revenue = daily_revenue * (1 + total_boost)

                    # Add the boosted revenue to the total
                    total_revenue += boosted_revenue

                # Update the user's revenue in the JSON variable
                revenue_data["daily"] = revenue_data.get("daily", 0) + total_revenue
                u.revenue = json.dumps(revenue_data)

                # Commit the changes
                session.commit()

        finally:
            session.close()
    
    times = [time(hour=h, tzinfo=eastern) for h in range(0, 24, 3)]
    @tasks.loop(time=times)
    async def update_stocks(self):
        Session = sessionmaker(bind=database.engine)
        session = Session()
        try:
            stocks = session.query(Stock.Stock).all()
            for stock in stocks:
                stock.update()

            # Commit the changes to the database
            session.commit()
        finally:
            session.close()

    @tasks.loop(time=times)
    async def update_stock_visuals(self):
        Session = sessionmaker(bind=database.engine)
        session = Session()
        try:
            stocks = session.query(Stock.Stock).all()
            for stock in stocks:
                # Get the stock type
                stock_type = stock.type_of
                
                # Check if the stock type has a corresponding update method
                if stock_type in self.stock_update_mapping:
                    # Call the appropriate update method
                    self.stock_update_mapping[stock_type](stock, session)
            
            # Commit changes to the database
            session.commit()
        finally:
            session.close()



async def setup(bot):
    await bot.add_cog(Config(bot))
