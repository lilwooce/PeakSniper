from ast import alias
from discord.ext import commands
import discord
from discord import app_commands
import math
from datetime import datetime, timedelta
from dotenv import load_dotenv
import requests
import os 
from sqlalchemy.orm import sessionmaker
from sqlalchemy.sql.expression import func
import random
import json
import logging

from classes import Servers, User, database, Jobs, ShopItem, Stock, Global, Houses, Freelancers, Businesses, Assets, EntityGenerator

load_dotenv()
getUser = os.getenv('GET_USER')
updateUser = os.getenv('UPDATE_USER')
addUser = os.getenv('ADD_USER')

allowed_ids = [347162620996091904]
admins = [347162620996091904, 187323145273868288]
def allowed():
    def predicate(interaction: discord.Interaction) -> bool:
        return interaction.user.id in allowed_ids
    return app_commands.check(predicate)

def admins_only():
    def predicate(interaction: discord.Interaction) -> bool:
        return interaction.user.id in admins
    return app_commands.check(predicate)

class Admin(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.min_num_jobs = 3

    @commands.Cog.listener()
    async def on_ready(self):
        print(f"{self.__class__.__name__} Cog has been loaded\n----")

    

    @commands.hybrid_command(name="addmoney", aliases=["am"], hidden=True, with_app_command=True)
    @commands.is_owner()
    async def addmoney(self, ctx: commands.Context, user: discord.User, amount: int):
        Session = sessionmaker(bind=database.engine)
        session = Session()
        u = session.query(User.User).filter_by(user_id=user.id).first()
        u.balance += amount
        session.commit()
        
        if (amount < 0) :
            await ctx.send(f"Removed {amount * -1} discoin(s) from {user}")
        else:
            await ctx.send(f"Added {amount} discoin(s) to {user}")

    @commands.hybrid_command(name="message", aliases=["msg"], hidden=True, with_app_command=True)
    @commands.is_owner()
    async def message(self, ctx: commands.Context, channel: discord.TextChannel, message: str):
        await channel.send(message)
        await ctx.send(f"message: [{message}] sent to {channel.name}")
    
    @app_commands.command()
    @admins_only()
    async def add_job(self, interaction: discord.Interaction, name: str, salary: int, chance: float):
        Session = sessionmaker(bind=database.engine)
        session = Session()

        try: 
            j = Jobs.Jobs(name, salary, chance)
            session.add(j)
            session.commit()
            await interaction.response.send_message(f"Successfully added a job: name {name}, salary {salary}, chance {chance}")
        finally:
            session.close()
        
    @app_commands.command()
    @allowed()
    async def add_shop_item(self, interaction: discord.Interaction, name: str, price: int, uses: int, command: str, item_type: str, duration: int):
        Session = sessionmaker(bind=database.engine)
        session = Session()

        try: 
            i = ShopItem.ShopItem(name, price, uses, command, item_type, duration)
            session.add(i)
            session.commit()
            await interaction.response.send_message(f"Successfully added a shop item: name {name}, price {price}, uses {uses}, command {command}, type {item_type}, duration {duration} minutes")

        finally:
            session.close()

    @app_commands.command()
    @admins_only()
    async def add_stock(self, interaction: discord.Interaction, name: str, full_name: str, growth_rate: float, start_value:float, volatility: float, swap_chance: float, ruination:float):
        Session = sessionmaker(bind=database.engine)
        session = Session()

        try: 
            s = Stock.Stock(name, full_name, growth_rate, start_value, volatility, swap_chance, ruination)
            session.add(s)
            session.commit()
            await interaction.response.send_message(f"Successfully added a stock item: name {name}, full_name {full_name}, growth_rate {growth_rate}, start_value {start_value}, volatility {volatility}, swap_chance {swap_chance} ruination {ruination}")
        finally:
            session.close()
    
    @app_commands.command()
    @admins_only()
    async def add_house(self, interaction: discord.Interaction, name: str, purchase_value: float, type_of: str, daily_expense: float, growth_rate: float, volatility: float, swap_chance: float, ruination: float):
        Session = sessionmaker(bind=database.engine)
        session = Session()

        try: 
            h = Houses.House(name, purchase_value, type_of, daily_expense)
            s = Stock.Stock(name, name, growth_rate, purchase_value, volatility, swap_chance, ruination)
            session.add(s)
            session.add(h)
            session.commit()
            await interaction.response.send_message(f"Successfully added a house: name {name}, growth_rate {growth_rate}, start_value {purchase_value}, volatility {volatility}, swap_chance {swap_chance} ruination {ruination}")
        finally:
            session.close()

    @app_commands.command()
    @allowed()
    async def daily_generator(self, interaction: discord.Interaction):
        entity_generator = EntityGenerator.EntityGenerator()
        await interaction.response.send_message("Generating things")
        
        # Await the result of the asynchronous entity generation
        result_message = await entity_generator.generate_and_add_entities()  
        await interaction.response.defer()
        
        await interaction.response.edit_message(result_message)



    @app_commands.command()
    @admins_only()
    async def add_business(self, interaction: discord.Interaction, name: str, purchase_value: float, type_of: str, daily_expense: float, daily_revenue: float):
        Session = sessionmaker(bind=database.engine)
        session = Session()

        try:
            b = Businesses.Business(name, purchase_value, type_of, daily_expense, daily_revenue)
            session.add(b)
            session.commit()
            await interaction.response.send_message(f"Successfully added a Business: name {name}, purchase_value {purchase_value}, type_of {type_of}, daily_expense {daily_expense}, daily_revenue {daily_revenue}")
        finally:
            session.close()


    @app_commands.command()
    @admins_only()
    async def add_asset(self, interaction: discord.Interaction, name: str, material: str, purchase_value: float, type_of: str):
        Session = sessionmaker(bind=database.engine)
        session = Session()

        try: 
            a = Assets.Asset(name, material, purchase_value, type_of)
            session.add(a)
            session.commit()
            await interaction.response.send_message(f"Successfully added an Asset: name {name}, material {material}, purchase_value {purchase_value}, type_of {type_of}")
        finally:
            session.close()


    @app_commands.command()
    @admins_only()
    async def add_freelancer(self, interaction: discord.Interaction, name: str, job_title: str, initial_cost: float, daily_expense: float, type_of: str, poach_minimum: float, boost_amount: float):
        Session = sessionmaker(bind=database.engine)
        session = Session()

        try: 
            f = Freelancers.Freelancer(name, job_title, initial_cost, daily_expense, type_of, poach_minimum, boost_amount)
            session.add(f)
            session.commit()
            await interaction.response.send_message(f"Successfully added a freelancer: name {name}, job_title {job_title}, initial_cost {initial_cost}, daily_expense {daily_expense}, type_of {type_of}, poach_minimum {poach_minimum}, boost_amount {boost_amount}")
        finally:
            session.close()


    
    @app_commands.command()
    @allowed()
    async def add_current_stock(self, interaction: discord.Interaction):
        Session = sessionmaker(bind=database.engine)
        session = Session()

        try: 
            stocks = session.query(Stock.Stock).all()
            if not stocks:
                await interaction.response.send_message("No stocks available at the moment.")
                return

            for i, stock in enumerate(stocks, start=1):
                logging.warning(stock.history)
                stock.history.append(stock.previous_value)
                stock.history.append(stock.current_value)
                logging.warning(stock.history)
                session.add(stock)
            session.commit()
            await interaction.response.send_message("Success")
        finally:
            session.close()

    @app_commands.command()
    @allowed()
    async def set_stock_amount(self, interaction: discord.Interaction):
        Session = sessionmaker(bind=database.engine)
        session = Session()

        try: 
            stocks = session.query(Stock.Stock).all()
            if not stocks:
                await interaction.response.send_message("No stocks available at the moment.")
                return

            for i, stock in enumerate(stocks, start=1):
                amount = stock.determine_stock_amount()
                stock.amount = amount
            session.commit()
            await interaction.response.send_message("Success")
        finally:
            session.close()

    def weigh_jobs(self, jobs):
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


    @app_commands.command()
    @allowed()
    async def randomize_jobs(self, interaction: discord.Interaction):
        Session = sessionmaker(bind=database.engine)
        session = Session()
        try:
            g = session.query(Global.Global).first()
            # Get a random list of jobs
            jobs_query = session.query(Jobs.Jobs).order_by(func.rand()).limit(random.randint(self.min_num_jobs, self.min_num_jobs*2)).all()
            jobs = self.weigh_jobs(jobs_query)

            g.jobs = json.dumps(jobs)

            # Commit the changes to the database
            await interaction.response.send_message("Success")
            session.commit()
        finally:
            session.close()
    
    @app_commands.command()
    @allowed()
    async def daily_tax(self, interaction: discord.Interaction):
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
                await interaction.response.send_message("Success")
        finally:
            session.close()
    
    @app_commands.command()
    @allowed()
    async def daily_tax_user(self, interaction: discord.Interaction, user: discord.User):
        Session = sessionmaker(bind=database.engine)
        session = Session()
        try:
            u = session.query(User.User).filter_by(user_id=user.id).first()
            if u.balance == 0 and u.in_jail == True:
                # Don't tax
                return
            
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
            await interaction.response.send_message("Success")
        finally:
            session.close()
    
    @commands.hybrid_command()
    @allowed()
    async def give_item(self, ctx, user: discord.User, amount: int, name: str):
        Session = sessionmaker(bind=database.engine)
        
        with Session() as session:
            try:
                item = session.query(ShopItem.ShopItem).filter_by(name=name).first()
                if not item:
                    await ctx.send(f"{name} was not found in shop.")
                    return

                u = session.query(User.User).filter_by(user_id=user.id).first()

                if not u:
                    await ctx.send("User not found.")
                    return
                
                inven = json.loads(u.inventory) if u.inventory else {}
                inven[item.name] = inven.get(item.name, 0) + amount
                u.inventory = json.dumps(inven)

                session.commit()
                await ctx.send(f"You have given {amount} {name}(s).")
            except Exception as e:
                print(f"Error in give items command: {e}")
                await ctx.send("An error occurred while giving the items.")
        
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
                    freelancer = session.query(Freelancers.Freelancer).filter_by(name=freelancer).first()
                    if freelancer.type_of in "assistant" and (
                        "wealth" in freelancer.job_title.lower() or "business" in freelancer.job_title.lower()
                    ):
                        total_boost += freelancer.boost_amount

                # Calculate the revenue for each business
                for business in businesses:
                    logging.warning(business)
                    b = session.query(Businesses.Business).filter_by(name=business).first()
                    daily_revenue = b.daily_revenue

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
    
    async def daily_expenses(self):
        Session = sessionmaker(bind=database.engine)
        session = Session()
        try:
            users = session.query(User.User).all()
            for u in users:
                # Load the user's businesses and revenue (if any)
                businesses = session.query(Businesses.Business).filter_by(owner=u.user_id).all()
                freelancers = json.loads(u.freelancers) if u.freelancers else {}
                houses = session.query(Houses.House).filter_by(owner=u.user_id).all()
                bills = json.loads(u.bills) if u.bills else {}
                # total_boost = 0

                # # Check if the user has any freelancers of type "assistant" with "wealth" or "business" in their job_name
                # freelancers = json.loads(u.freelancers) if u.freelancers else []
                # for freelancer in freelancers:
                #     freelancer = session.query(Freelancers.Freelancer).filter_by(name=freelancer).first()
                #     if freelancer.type_of in "assistant" and (
                #         "wealth" in freelancer.job_title.lower() or "business" in freelancer.job_title.lower()
                #     ):
                #         total_boost += freelancer.boost_amount

                # Calculate the revenue for each business
                if businesses:
                    for b in businesses:
                        logging.warning(b.name)
                        daily_expense = b.daily_expense
                        if bills and b.name in bills:
                            bills[b.name] += daily_expense
                        else:
                            bills[b.name] = daily_expense
                
                for freelancer in freelancers:
                    logging.warning(freelancer)
                    f = session.query(Freelancers.Freelancer).filter_by(name=freelancer).first()
                    daily_expense = f.daily_expense
                    if bills and f.name in bills:
                        bills[f.name] += daily_expense
                    else:
                        bills[f.name] = daily_expense
                
                if houses:
                    for house in houses:
                        logging.warning(house.name)
                        daily_expense = house.daily_expense
                        if bills and house.name in bills:
                            bills[house.name] += daily_expense
                        else:
                            bills[house.name] = daily_expense

                u.bills = json.dumps(bills)
                # Commit the changes
                session.commit()

        finally:
            session.close()

    @commands.hybrid_command()
    @allowed()
    async def daily_rev_exp(self, ctx): 
        try:
            await self.daily_expenses()
            await self.daily_revenue()
            await ctx.send("Success!")
        except Exception as e:
            await ctx.send(f"Error: {e}")

async def setup(bot):
    await bot.add_cog(Admin(bot))