from discord.ext import commands
import discord
import datetime
import math
import json
from pytz import timezone
import random

curr = 0

class Snipe(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.Cog.listener()
    async def on_ready(self):
        print(f"{self.__class__.__name__} Cog has been loaded\n----")

    @commands.Cog.listener()
    async def on_message_delete(self, message):
        global sniped
        global imgUrl
        if message.author.bot == True:
            return
        sniped = message
        imgUrl = ""

        if (message.attachments):
            imgUrl = message.attachments[0].url
    
    @commands.Cog.listener()
    async def on_message_edit(self, messageBefore, messageAfter):
        global messageB
        global messageA
        global editImg
        global editUrl
        if messageBefore.author.bot == True:
            return
        if messageAfter.author.bot == True:
            return
        messageB = messageBefore
        messageA = messageAfter
        editImg = "";
        editUrl = "";

        if (messageB.attachments):
            editImg = messageB.attachments[0].url
        if (messageA.attachments):
            editUrl = messageA.attachments[0].url

    @commands.command()
    async def roll(self, ctx, arg: int):
        rig = True
        seq = [2,3,2,2]
        try:
            randValue = random.randint(1, arg)
            if rig == True:
                num = seq[curr]
                await ctx.channel.send(f"{ctx.author.mention}, rolled a `{num}`")
                curr += 1
            else:
                await ctx.channel.send(f"{ctx.author.mention}, rolled a `{randValue}`")
        except:
            await ctx.channel.send("Please input a valid number")

    @commands.command(aliases=["s", "S"])
    async def snipe(self, ctx):
        eastern = timezone('US/Eastern')
        if (sniped):
            embed=discord.Embed(title=f"{sniped.author.name}#{sniped.author.discriminator}", description="")
            embed.timestamp = datetime.datetime.now(eastern)
            if (len(sniped.content) > 1024):
                for i in range(0, (len(sniped.content)), 1024):
                    if (i + 1024 < len(sniped.content)):
                        embed.add_field(name= "Caught! <:sussykasra:873330894260297759>" ,value=sniped.content[i:i+1024], inline=True)        
                    else:
                        embed.add_field(name= "Caught! <:sussykasra:873330894260297759>" ,value=sniped.content[i:len(sniped.content)], inline=True)        
            else:
                embed.add_field(name= "Caught! <:sussykasra:873330894260297759>" ,value=sniped.content, inline=True)
        else:
            embed=discord.Embed(title="Noone", description="")
            embed.timestamp = datetime.datetime.now(eastern)
            embed.add_field(name= "Caught! <:sussykasra:873330894260297759>" ,value="No Message Sent", inline=True)
        if (len(imgUrl) > 0):
            embed.set_image(url=imgUrl)
            embed.add_field(name="File Name", value=sniped.attachments[0].url, inline=True)
        await ctx.channel.send(embed=embed)

    @commands.command(aliases=["es"])
    async def editsnipe(self, ctx):
        eastern = timezone('US/Eastern')
        if (messageB.author.bot): return
        if (messageA.author.bot): return
        embed=discord.Embed(title=f"{messageB.author.name} edited a message from #{messageB.channel.name} <:sussykasra:873330894260297759>", description="")
        embed.timestamp = datetime.datetime.now(eastern)
        embedA=discord.Embed(title=f"{messageA.author.name} edited a message from #{messageA.channel.name} <:sussykasra:873330894260297759>", description="")
        embedA.timestamp = datetime.datetime.now(eastern)
        if (messageB.content):
            embed.add_field(name= messageB.content ,value="Before", inline=True)
        else:
            embed.add_field(name="No content" ,value="Before", inline=True)
        if (messageA.content):
            embed.add_field(name= messageA.content ,value="After", inline=True)
        else:
            embed.add_field(name="No content" ,value="After", inline=True)
        if (messageB.attachments):
            embed.set_image(url=messageB.attachments[0].url)
            embed.add_field(name="File Name", value=messageB.attachments[0].url, inline=True)
        if (messageA.attachments):
            embedA.set_image(url=messageA.attachments[0].url)
            embed.add_field(name="File Name", value=messageA.attachments[0].url, inline=True)
            await ctx.channel.send(ctx.channel, embed=embedA)
            
        await ctx.channel.send(embed=embed)

    @commands.command()
    async def coin(self, ctx):
        heads = discord.File("pointsbot\\images\\usoppheads.png")
        tails = discord.File("pointsbot\\images\\sogekingtails.png")
        choice = random.randint(1,2)

        if choice == 1:
            await ctx.channel.send("flipped a coin: **heads**", file=heads)
        elif choice == 2:
            await ctx.channel.send("flipped a coin: **tails**", file=tails)

def setup(bot):
    bot.add_cog(Snipe(bot))