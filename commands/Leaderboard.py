from discord.ext import commands
import discord
from discord import app_commands
from dotenv import load_dotenv
from sqlalchemy import desc, func
from sqlalchemy.orm import sessionmaker
from classes import User, database, Stock

class Leaderboard(commands.Cog, name="Leaderboard"):
    def __init__(self, client: commands.Bot):
        self.client = client

    @app_commands.command(name="leaderboard", description="Display the richest users in the server.")
    async def leaderboard(self, interaction: discord.Interaction, stat: str = "Wealth"):
        guild = interaction.guild
        if not guild:
            await interaction.response.send_message("This command can only be used in a server.", ephemeral=True)
            return
        
        Session = sessionmaker(bind=database.engine)
        session = Session()

        try:
            users = [member.id for member in guild.members if not member.bot]
            embed = discord.Embed(title=f"Highest Net Worth in {guild.name}", color=discord.Color.gold())

            # Query to order users by the combined total of balance and bank
            database_users = session.query(User.User).order_by(desc(func.coalesce(User.User.balance, 0) + func.coalesce(User.User.bank, 0))).all()

            count = 0
            for u in database_users:
                if u.user_id in users:
                    member = guild.get_member(u.user_id)
                    if member:
                        portfolio = u.portfolio
                        total_value = 0
                        for stock_name, shares in portfolio.items():
                            stock = session.query(Stock.Stock).filter_by(name=stock_name).first()
                            if stock:
                                value = int(stock.current_value) * shares
                                total_value += value
                        embed.add_field(name=member.display_name, value=f"{u.balance + u.bank + total_value} discoins", inline=False)
                        count += 1
                        if count >= 10:  # Display top 10 users
                            break

            if count == 0:
                embed.description = "No users found in the leaderboard."

            await interaction.response.send_message(embed=embed)

        except Exception as e:
            await interaction.response.send_message("An error occurred while retrieving the leaderboard.", ephemeral=True)
            print(f"Error: {e}")

        finally:
            session.close()

async def setup(bot):
    await bot.add_cog(Leaderboard(bot))
