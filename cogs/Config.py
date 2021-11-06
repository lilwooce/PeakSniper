from discord.ext import commands
import json
import discord 

class Config(commands.Cog, name="Configuration"):
    def __init__(self, bot):
        self.bot = bot

    @commands.Cog.listener()
    async def on_ready(self):
        print(f"{self.__class__.__name__} Cog has been loaded\n----")

    @commands.command()
    async def prefix(self, ctx, new_prefix):
        with open("snipe bot\\prefixes.json", "r") as f:
            prefixes = json.load(f)
            
            prefixes[str(ctx.guild.id)] = new_prefix
            
            with open("snipe bot\\prefixes.json", "w") as f:
                json.dump(prefixes, f, indent=4)
        await ctx.send(f"Changed the prefix to: {new_prefix}")    

        @commands.command()
        async def debug(self, ctx, emoji: discord.Emoji):
            embed = discord.Embed(description=f"emoji: {emoji}", title=f"emoji: {emoji}")
            embed.add_field(name="id", value=repr(emoji.id))
            embed.add_field(name="name", value=repr(emoji.name))
            await ctx.channel.send(embed=embed)
        
        @commands.command(aliases=["ren"])
        async def rename(self, ctx, user: discord.User = None, *nick):
            if not user:
                print("user not found")
            else:
                memer = ctx.guild.get_member(user.id)
                n = ""
                for word in nick:
                    n += f"{word} "
                await memer.edit(nick=n)

        @commands.command()
        async def mute(self, ctx, user: discord.User=None):
            if not user:
                print("user not found")
            else:
                memer = ctx.guild.get_member(user.id)
                await memer.edit(mute=True)

def setup(bot):
    bot.add_cog(Config(bot))