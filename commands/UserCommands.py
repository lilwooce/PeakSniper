from discord.ext import commands, tasks
import discord
from discord import app_commands
from dotenv import load_dotenv
import os
from sqlalchemy.orm import sessionmaker
from classes import Servers, User, database, Jobs, JobSelector, ShopItem
from .Config import hasAccount
from datetime import datetime, timedelta
import logging
import random
import json
import asyncio

all_array = ['all', 'ALL', 'al', 'alll']

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
            embed.add_field(name="Total Received", value=f"**{u.total_receieved}** discoins received from other players", inline=False)
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

            user_jobs = json.loads(u.jobs)
            job_name = user_jobs[f'{ctx.guild.id}']
            if job_name is None:
                await ctx.send("Job not found for this server. Please apply first before working.")
                return
            j = session.query(Jobs.Jobs).filter_by(name=job_name).first()

            embed.set_author(name=user.name, icon_url=user.display_avatar)
            embed.add_field(name="Snipe Message", value=f"**{u.snipe_message}**", inline=False)
            embed.add_field(name="Balance", value=f"**{u.balance}** discoins", inline=False)
            embed.add_field(name="Poll Gamba", value=f"**{u.poll_gamba}** discoins", inline=False)
            embed.add_field(name="Current Job", value=f"**{j.name}**", inline=False)

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

            await ctx.send(f"**{user.name}** has `{u.balance}` discoins in their wallet\n**{user.name}** has `{u.bank}` discoins in their bank.")
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
            s = session.query(Servers.Servers).filter_by(server_id=guild.id).first()
            u = session.query(User.User).filter_by(user_id=ctx.author.id).first()

            if not u:
                await ctx.send("User not found.")
                return

            used_items = json.loads(u.used_items) if u.used_items else {}

            # Check if the user has a resume
            if not used_items.get("resume", False):
                await ctx.send("You cannot apply for a job without a *Resume*. Try purchasing one from the Shop.")
                return

            if not s:
                await ctx.send("Server not found.")
                return

            # s.jobs is now a JSON column, which is automatically handled as a Python list
            jobs = []
            for job_name in s.jobs:
                j = session.query(Jobs.Jobs).filter_by(name=job_name).first()
                if j:
                    jobs.append((job_name, j.chance))

            if not jobs:
                await ctx.send("No jobs available.")
                return

            # Use JobSelector to choose a job
            js = JobSelector.JobSelection(jobs)
            selected_job = js.choose_job()

            # Update or add the new job for the given server_id in user's jobs
            current_jobs = json.loads(u.jobs) if u.jobs else {}
            current_jobs[str(guild.id)] = selected_job
            del used_items['resume']
            u.used_items = json.dumps(used_items)

            # Convert the dictionary back to JSON and update the jobs column
            u.jobs = json.dumps(current_jobs)

            # Commit the changes to the database
            session.commit()

            j = session.query(Jobs.Jobs).filter_by(name=selected_job).first()
            await ctx.send(f"Congratulations! You are now a(n) {j.name}! You make {j.salary} every time you work.")

        except Exception as e:
            await ctx.send("An error occurred while applying for a job.", ephemeral=True)
            logging.warning(f"Error: {e}")

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
            server = session.query(Servers.Servers).filter_by(server_id=guild.id).first()
            if not server:
                await ctx.send("Server not found in the database.", ephemeral=True)
                return

            jobs = server.jobs if isinstance(server.jobs, list) else []

            embed = discord.Embed(title=f"Jobs in {guild.name}", color=discord.Color.blue())
            if jobs:
                for job_name in jobs:
                    j = session.query(Jobs.Jobs).filter_by(name=job_name).first()
                    # If you store salary information separately, retrieve and display it here
                    embed.add_field(name=job_name, value=f"Salary: {j.salary} | Acceptance Chance: {j.chance}%", inline=False)
            else:
                embed.description = "No jobs found for this server."

            await ctx.send(embed=embed)

        except Exception as e:
            await ctx.send("An error occurred while retrieving the jobs.", ephemeral=True)
            logging.warning(f"Error: {e}")

        finally:
            session.close()

    @commands.hybrid_command()
    async def inventory(self, ctx):
        Session = sessionmaker(bind=database.engine)
        session = Session()

        try:
            # Fetch user data
            user = session.query(User.User).filter_by(user_id=ctx.author.id).first()
            if not user:
                await ctx.send("User not found in the database.", ephemeral=True)
                return

            inventory = json.loads(user.inventory) if user.inventory else {}
            if inventory == {}:
                await ctx.send("Your inventory is empty")

            # Divide inventory items into pages with a max of 5 items per page
            items = list(inventory.items())
            pages = [items[i:i + 5] for i in range(0, len(items), 5)]
            current_page = 0

            # Function to create an embed for a given page
            def create_embed(page):
                embed = discord.Embed(title=f"{ctx.author.name}'s Inventory", description=f"Page {page + 1}/{len(pages)}", color=discord.Color.green())
                for item_name, quantity in pages[page]:
                    embed.add_field(name=item_name.title(), value=f"Quantity: {quantity}", inline=False)
                return embed

            # Send the first embed
            message = await ctx.send(embed=create_embed(current_page))

            # Add reactions if there are multiple pages
            if len(pages) > 1:
                await message.add_reaction("⬅️")
                await message.add_reaction("➡️")

                # Check for reaction events
                def check(reaction, user):
                    return user == ctx.author and reaction.message.id == message.id and str(reaction.emoji) in ["⬅️", "➡️"]

                while True:
                    try:
                        reaction, user = await self.bot.wait_for("reaction_add", timeout=60.0, check=check)

                        if str(reaction.emoji) == "➡️":
                            if current_page < len(pages) - 1:
                                current_page += 1
                                await message.edit(embed=create_embed(current_page))
                        elif str(reaction.emoji) == "⬅️":
                            if current_page > 0:
                                current_page -= 1
                                await message.edit(embed=create_embed(current_page))

                        await message.remove_reaction(reaction, user)

                    except asyncio.TimeoutError:
                        break

                # Clear reactions after the timeout
                await message.clear_reactions()

        except Exception as e:
            await ctx.send("An error occurred while retrieving your inventory.", ephemeral=True)
            logging.warning(f"Error: {e}")

        finally:
            session.close()

    @commands.hybrid_command()
    async def current_effects(self, ctx):
        Session = sessionmaker(bind=database.engine)
        session = Session()

        try:
            # Fetch user data
            u = session.query(User.User).filter_by(user_id=ctx.author.id).first()

            if not u:
                await ctx.send("User not found in the database.", ephemeral=True)
                return

            # Load used items
            used_items = json.loads(u.used_items) if u.used_items else {}
            if used_items == {}:
                await ctx.send("You have no currently applied effects")

            embed = discord.Embed(title="Current Active Effects", color=discord.Color.green())
            if used_items:
                for item_name, effect in used_items.items():
    
                    # Check if 'expires_at' key exists in the effect dictionary
                    expires_at = effect.get('expires_at', None)
                    if expires_at:
                        embed.add_field(name=item_name, value=f"Effect: {effect['description']}\nExpires at: {expires_at}", inline=False)
                    else:
                        embed.add_field(name=item_name, value=f"Effect: {effect['description']}", inline=False)
            else:
                embed.description = "No active effects found."

            await ctx.send(embed=embed)

        except Exception as e:
            await ctx.send("An error occurred while retrieving active effects.", ephemeral=True)
            logging.warning(f"Error: {e}")

        finally:
            session.close()

    @commands.hybrid_command()
    async def use(self, ctx, *, item_name: str):
        Session = sessionmaker(bind=database.engine)
        session = Session()

        try:
            u = session.query(User.User).filter_by(user_id=ctx.author.id).first()

            if not u:
                await ctx.send("User not found in the database.", ephemeral=True)
                return

            inventory = json.loads(u.inventory) if u.inventory else {}
            used_items = json.loads(u.used_items) if u.used_items else {}

            if item_name not in inventory or inventory[item_name] <= 0:
                await ctx.send(f"You don't have {item_name} in your inventory.", ephemeral=True)
                return

            # Fetch the item details from the ShopItem table
            item = session.query(ShopItem.ShopItem).filter_by(name=item_name).first()
            if not item:
                await ctx.send(f"{item_name} not found in the shop.", ephemeral=True)
                return

            to_send = ""
            # Apply the effect of the item
            if item.item_type == "boost":
                effect = {"description": f"{item_name} effect active", "expires_at": str(datetime.now() + timedelta(minutes=item.duration))}
                used_items[item_name] = effect
                to_send = f"You have used {item_name}. Effect is now active for {item.duration} minutes!"
                await self.schedule_effect_removal(ctx.author.id, item_name, datetime.now() + timedelta(minutes=item.duration))
            elif item.item_type == "consumable":
                effect = {"description": f"{item_name} effect active"}
                used_items[item_name] = effect
                to_send = f"You have used {item_name}. Effect is now active!"

            # Update the user's inventory and used_items
            inventory[item_name] -= 1
            if inventory[item_name] == 0:
                del inventory[item_name]
            
            u.inventory = json.dumps(inventory)
            u.used_items = json.dumps(used_items)

            session.commit()

            await ctx.send(to_send, ephemeral=True)

        except Exception as e:
            await ctx.send("An error occurred while using the item.", ephemeral=True)
            logging.warning(f"Error: {e}")

        finally:
            session.close()

    async def schedule_effect_removal(self, user_id, item_name, expiration_time):
        async def remove_after_delay():
            # Calculate the delay in seconds until expiration
            logging.warning("Scheduling effect removal")
            delay = (expiration_time - datetime.now()).total_seconds()
            if delay > 0:
                await asyncio.sleep(delay)
                # Remove effect after the delay
                await self.remove_effect(user_id, item_name)
        
        # Create a background task for effect removal
        asyncio.create_task(remove_after_delay())

    async def remove_effect(self, user_id, item_name):
        Session = sessionmaker(bind=database.engine)
        session = Session()

        try:
            u = session.query(User.User).filter_by(user_id=user_id).first()
            if not u:
                return

            used_items = json.loads(u.used_items) if u.used_items else {}
            if item_name in used_items:
                del used_items[item_name]
                u.used_items = json.dumps(used_items)
                session.commit()
                # Optionally notify the user
                user = self.bot.get_user(user_id)
                if user:
                    await user.send(f"The effect of {item_name} has expired.")
        except Exception as e:
            logging.warning(f"Error: {e}")
        finally:
            session.close()
    
    @commands.hybrid_command()
    async def deposit(self, ctx, amount):
        author = ctx.author
        Session = sessionmaker(bind=database.engine)
        session = Session()

        try:
            u = session.query(User.User).filter_by(user_id=author.id).first()
            if type(amount) == str and amount.lower() in all_array:
                amount = u.balance
            else:
                amount = int(amount)
            if amount == 0:
                await ctx.send("Why are you trying to deposit nothing? What is wrong with you?")
                return
            if amount < 0:
                await ctx.send("You can't deposit negative discoins. Are you dumb?")
                return

            if not u or u.balance < amount:
                await ctx.send("You don't have enough money. Next time don't bite off more than you can chew.")
                return
            
            u.balance -= amount
            u.bank += amount

            session.commit()

            await ctx.send(f"**{ctx.author.name}#{ctx.author.discriminator}** just deposited **{amount}** discoin(s) to their bank")
        finally:
            session.close()
    
    @commands.hybrid_command()
    async def withdraw(self, ctx, amount):
        author = ctx.author
        Session = sessionmaker(bind=database.engine)
        session = Session()

        try:
            u = session.query(User.User).filter_by(user_id=author.id).first()
            if type(amount) == str and amount.lower() in all_array:
                amount = u.bank
            else:
                amount = int(amount)
            if amount == 0:
                await ctx.send("Why are you trying to withdraw nothing? What is wrong with you?")
                return
            if amount < 0:
                await ctx.send("Are you trying to deposit discoins? Try using /deposit")
                return

            if not u or u.bank < amount:
                await ctx.send("You don't have enough money. Next time don't bite off more than you can chew.")
                return
            
            u.balance += amount
            u.bank -= amount

            session.commit()

            await ctx.send(f"**{ctx.author.name}#{ctx.author.discriminator}** just withdrew **{amount}** discoin(s) from their bank")
        finally:
            session.close()

    @commands.hybrid_command()
    async def steal(self, ctx, user: discord.Member):
        thief = ctx.author
        victim = user
        Session = sessionmaker(bind=database.engine)
        session = Session()

        try:
            t = session.query(User.User).filter_by(user_id=thief.id).first()
            v = session.query(User.User).filter_by(user_id=victim.id).first()
            used_items = json.loads(v.used_items) if v.used_items else {}

            # Check if the user is on cooldown
            current_time = datetime.now()
            if t.steal_cooldown and current_time < t.steal_cooldown:
                remaining_time = (t.steal_cooldown - current_time).total_seconds()
                minutes, seconds = divmod(remaining_time, 60)
                await ctx.send(f"You are on cooldown! Please wait {int(minutes)} minutes and {int(seconds)} seconds before stealing again.")
                return

            if (t.balance < 500):
                await ctx.send("You cannot try to rob someone without having at least 500 in your wallet")
                return
            
            # Check if the victim has a padlock
            if used_items.get("padlock", False):
                await ctx.send(f"{victim.name} has a padlock. Your attempt to steal failed, and you got caught by the cops! You lost 500 discoins.")
                # Lose 500 discoins
                t.balance = max(t.balance - 500, 0)
                # Set cooldown even if the steal fails
                t.steal_cooldown = current_time + timedelta(minutes=10)
                session.commit()
                return

            # Implement stealing based on a percentage chance for winning and failing
            steal_success_chance = 15  # 15% chance to succeed
            if random.randint(1, 100) <= steal_success_chance:
                ret = ""
                # Determine the amount stolen based on probabilities
                steal_outcome = random.randint(1, 100)
                if steal_outcome <= 65:  # 65% chance to steal 30% of victim's balance
                    stolen_amount = int(v.balance * 0.30)
                    ret = f"**PAYOUT** YOU STOLE SOME OF THEIR MONEY +{stolen_amount} TO YOU!!!"
                elif steal_outcome <= 90:  # 25% chance to steal 49% of victim's balance
                    stolen_amount = int(v.balance * 0.49)
                    ret = f"**BIG PAYOUT** YOU STOLE ALMOST HALF OF THEIR MONEY +{stolen_amount} TO YOU!!!"
                elif steal_outcome <= 99:  # 14% chance to steal 75% of victim's balance
                    stolen_amount = int(v.balance * 0.75)
                    ret = f"**HUGE PAYOUT** YOU STOLE A BIG PORTION OF THEIR MONEY +{stolen_amount} TO YOU!!!"
                else:  # 1% chance to steal 99% of victim's balance
                    stolen_amount = int(v.balance * 0.99)
                    ret = f"**MASSIVE PAYOUT** YOU STOLE ALMOST ALL OF THEIR MONEY +{stolen_amount} TO YOU!!!"

                # Adjust the balances of the thief and the victim
                t.balance += stolen_amount
                v.balance = max(v.balance - stolen_amount, 0)
                await ctx.send(ret)
            else:
                # Failed steal
                fail_outcome = random.randint(1, 100)
                if fail_outcome <= 60:  # 60% chance to lose 500 discoins
                    t.balance = max(t.balance - 500, 0)
                    await ctx.send(f"You failed to steal from {victim.name} and got caught by the cops! You lost 500 discoins.")
                elif fail_outcome <= 95:  # 35% chance to lose nothing
                    await ctx.send(f"You failed to steal from {victim.name} but managed to escape without any penalties.")
                else:  # 5% chance to lose your job and become a beggar
                    guild = ctx.guild
                    current_jobs = json.loads(t.jobs) if t.jobs else {}
                    current_jobs[str(guild.id)] = "beggar"
                    t.jobs = json.dumps(current_jobs)
                    await ctx.send(f"You failed to steal from {victim.name} and got caught by the cops! You lost your job and are now a beggar.")

            # Set cooldown
            t.steal_cooldown = current_time + timedelta(minutes=10)

            # Commit the changes to the database
            session.commit()

        except Exception as e:
            await ctx.send("An error occurred while attempting to steal.", ephemeral=True)
            logging.warning(f"Error: {e}")

        finally:
            session.close()



async def setup(bot):
    await bot.add_cog(UserCommands(bot))
