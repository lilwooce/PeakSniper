from discord.ext import commands
import discord
from discord import app_commands
from dotenv import load_dotenv
from sqlalchemy import desc
from sqlalchemy.orm import sessionmaker
from classes import User, database

class Leaderboard(commands.Cog, name="Leaderboard"):
    def __init__(self, client: commands.Bot):
        self.client = client

    @app_commands.command(name="leaderboard", description="Display the richest users in the server.")
    async def leaderboard(self, interaction: discord.Interaction):
        guild = interaction.guild
        if not guild:
            await interaction.response.send_message("This command can only be used in a server.", ephemeral=True)
            return
        
        Session = sessionmaker(bind=database.engine)
        session = Session()

        try:
            users = [member.id for member in guild.members if not member.bot]
            embed = discord.Embed(title=f"Richest Users in {guild.name}", color=discord.Color.gold())

            # Query the database for users in this server, ordered by balance
            database_users = session.query(User.User).order_by(desc(User.User.balance)).all()

            count = 0
            for u in database_users:
                if u.user_id in users:
                    member = guild.get_member(u.user_id)
                    if member:
                        embed.add_field(name=member.display_name, value=f"{u.balance} discoins", inline=False)
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
