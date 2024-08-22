import discord
from discord.ext import commands
import traceback

class ExceptionHandler(commands.Cog):
    def __init__(self, bot: commands.Bot) -> None:
        self.bot = bot

    @commands.Cog.listener()
    async def on_command_error(self, ctx: commands.Context, error) -> None:
        if isinstance(error, commands.CommandOnCooldown):
            await ctx.send('This command is on a %.2fs cooldown' % error.retry_after)
        elif isinstance(error, commands.MissingPermissions):
            await ctx.send("You don't have the necessary permissions to use this command.")
        elif isinstance(error, commands.MissingRequiredArgument):
            await ctx.send(f"Missing arguments: {error.param}")
        else:
            # Log the error to console for other types of errors
            print(f"An error occurred: {error}")
            traceback.print_exception(type(error), error, error.__traceback__)

            # Send a generic error message to the user
            await ctx.send("An unexpected error occurred. Please try again.")
        
async def setup(bot: commands.Bot) -> None:
    await bot.add_cog(ExceptionHandler(bot))