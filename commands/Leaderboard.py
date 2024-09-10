from discord.ext import commands
import discord
from discord import app_commands
from dotenv import load_dotenv
from sqlalchemy import desc, func
from sqlalchemy.orm import sessionmaker
from classes import User, database, Stock
import logging
import json

class Leaderboard(commands.Cog, name="Leaderboard"):
    def __init__(self, client: commands.Bot):
        self.client = client

    #@app_commands.command(name="leaderboard", description="Display the richest users in the server.")
    @commands.hybrid_command(aliases=['lb'])
    async def leaderboard(self, ctx, stat: str = "Wealth"):
        guild = ctx.guild
        if not guild:
            await ctx.send("This command can only be used in a server.", ephemeral=True)
            return
        
        Session = sessionmaker(bind=database.engine)
        session = Session()

        try:
            users = [member.id for member in guild.members if not member.bot]
            embed = discord.Embed(title=f"Highest Net Worth in {guild.name}", color=discord.Color.gold())

            # Retrieve all users
            database_users = session.query(User.User).filter(User.User.user_id.in_(users)).all()

            # Calculate total value for each user
            user_values = []
            for u in database_users:
                total_value = u.balance + u.bank
                portfolio = json.loads(u.portfolio) if u.portfolio else {}
                for stock_name, shares in portfolio.items():
                    stock = session.query(Stock.Stock).filter_by(name=stock_name).first()
                    if stock:
                        total_value += int(stock.current_value) * shares
                user_values.append((u.user_id, total_value))

            # Sort users by total value in descending order
            user_values.sort(key=lambda x: x[1], reverse=True)

            count = 0
            for user_id, total_value in user_values:
                if count >= 10:  # Display top 10 users
                    break
                member = guild.get_member(user_id)
                if member:
                    embed.add_field(name=member.display_name, value=f"{total_value} discoins", inline=False)
                    count += 1

            if count == 0:
                embed.description = "No users found in the leaderboard."

            await ctx.send(embed=embed)

        except Exception as e:
            await ctx.send("An error occurred while retrieving the leaderboard.", ephemeral=True)
            logging.warning(f"Error: {e}")

        finally:
            session.close()

async def setup(bot):
    await bot.add_cog(Leaderboard(bot))
