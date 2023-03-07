from re import M
import discord
from discord.ext import commands
import datetime
import math
import json
from pytz import timezone
import random
import os
from dotenv import load_dotenv
import requests
from .Config import hasAccount

load_dotenv()
tails = os.getenv('heads')
heads = os.getenv('tails')
updateUser = os.getenv('UPDATE_USER')
addUser = os.getenv('ADD_USER')
getUser = os.getenv('GET_USER')

def validCheck(sniper):
        snipee = sniped.author

        if (sniper.id == snipee.id):
            return False
        
        return True
    
def validSnipe(user, num):
    balance = requests.get(getUser, params={"f1": "discoins", "f2": user}, headers={"User-Agent": "XY"})
    b = balance.text.replace('"', '')
    add = num
    b = int(b) + add

    earned = requests.get(getUser, params={"f1": "totalEarned", "f2": user}, headers={"User-Agent": "XY"})
    e = earned.text.replace('"', '')
    add = num
    e = int(e) + add

    snipes = requests.get(getUser, params={"f1": "snipes", "f2": user}, headers={"User-Agent": "XY"})
    s = snipes.text.replace('"', '')
    s = int(s) + 1

    requests.post(updateUser, data={"f1": "totalEarned", "f2": e, "f3": user}, headers={"User-Agent": "XY"})
    requests.post(updateUser, data={"f1": "discoins", "f2": b, "f3": user}, headers={"User-Agent": "XY"})
    requests.post(updateUser, data={"f1": "snipes", "f2": s, "f3": user}, headers={"User-Agent": "XY"})

class Snipe(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.snipeVal = 5

    @commands.Cog.listener()
    async def on_ready(self):
        print(f"{self.__class__.__name__} Cog has been loaded\n----")

    @commands.Cog.listener()
    async def on_message_delete(self, message="None"):
        eastern = timezone('US/Eastern')
        global sniped
        global imgUrl
        global timestamp

        if message.author.bot == True:
            return
        sniped = message
        imgUrl = ""
        timestamp = datetime.datetime.now(eastern)

        if (message.attachments):
            imgUrl = message.attachments[0].url
        
        '''if(message.author.id == 744615852111954051):
            embed=discord.Embed(title=f"{message.author.name}#{message.author.discriminator}", description="")
            embed.timestamp = timestamp
            embed.add_field(name="Caught! <:sussykasra:873330894260297759>" ,value="My name is George Owusu and I am gay.", inline=True)
            await message.channel.send(embed=embed)'''
        
        await self.bot.process_commands(message)
    
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
        editImg = ""
        editUrl = ""

        if (messageB.attachments):
            editImg = messageB.attachments[0].url
        if (messageA.attachments):
            editUrl = messageA.attachments[0].url
            
    @commands.command(description="Like a infinite dice, this function allows you to enter a number and receive back a randomly selected number from 1 to this high limit, this function is used in many ways, such as determining who will pay for lunch, how many ducks are needed to fight alligators and rolling for double damage.")
    async def roll(self, ctx, arg: int):
        try:
            randValue = random.randint(1, arg)
            
            await ctx.channel.send(f"{ctx.author.mention}, rolled a `{randValue}`")
        except:
            await ctx.channel.send("Please input a valid number")
        
        return randValue

    @commands.command(aliases=["ftn"])
    async def firstToNum(self, ctx, firstTo: int, numberOfChoices: int):
        print("first to 3ing !!!")
        numbers = {}
        first = 0
        for x in range(1, numberOfChoices+1):
            numbers[x] = 0
            print(f"added {x} to numbers")

        print(numbers)

        while firstTo not in numbers.values():
            print(f"nothing has hit {firstTo} rolls yet! rolling!")
            rolled = await self.roll(ctx, numberOfChoices)
            print("rolled")
            numbers[rolled] += 1
            print(f"added 1 to {rolled} it now has a value of {numbers[rolled]}")
            if (numbers[rolled] >= firstTo):
                first = rolled

        await ctx.channel.send(f"{first} was the first to reach {firstTo} rolls")
        


    
    async def getReply(self, m):
        msg = "Not replying to anything"
        if m.reference is not None:
            if m.reference.cached_message is None:
                channelID = m.reference.channel_id
                channel = self.bot.get_channel(channelID)
                msg = await channel.fetch_message(m.reference.message_id)
            else:
                msg = m.reference.cached_message
        return msg

    async def checkReply(self, m):
        if m.reference is not None:
            return True
        return False

    @commands.command(aliases=["s"], description="This function allows you to retrieve the most recent deleted or lost message on the server.")
    @commands.check(hasAccount)
    async def snipe(self, ctx):
        hehe = False
        if (hehe==False):
            sniper = ctx.author
            embed=discord.Embed(title=f"{sniped.author.name}#{sniped.author.discriminator}", description="")
            embed.timestamp = timestamp
            if(sniped.content):
                if (len(sniped.content) > 1024):
                    for i in range(0, (len(sniped.content)), 1024):
                        if (i + 1024 < len(sniped.content)):
                            embed.add_field(name= "Caught! <:sussykasra:873330894260297759>" ,value=sniped.content[i:i+1024], inline=True)     
                        else:
                            embed.add_field(name= "Caught! <:sussykasra:873330894260297759>" ,value=sniped.content[i:len(sniped.content)], inline=True)   
                else:
                    embed.add_field(name= "Caught! <:sussykasra:873330894260297759>" ,value=sniped.content, inline=True) 
            else:
                embed.add_field(name= "Caught! <:sussykasra:873330894260297759>" ,value="No Message Sent", inline=True)
            if (len(imgUrl) > 0):
                embed.set_image(url=imgUrl)
                embed.add_field(name="File Name", value=sniped.attachments[0].url, inline=True)
            if(await self.checkReply(sniped)):
                repMes = await self.getReply(sniped)
                embed.add_field(name="Reply", value=repMes.jump_url, inline=True)  
            
            
            if(sniped.author.id == 0000000000000000):
                await ctx.channel.send("heh sorry guys. i made a deal.")
            else:
                await ctx.channel.send(embed=embed)
                if validCheck(sniper):
                    validSnipe(sniper.id, self.snipeVal)  
        else:
            await ctx.channel.send("HAPPY HALLOWEEN <:sussykasra:873330894260297759><:sussykasra:873330894260297759><:sussykasra:873330894260297759><:sussykasra:873330894260297759><:sussykasra:873330894260297759>")

    @commands.command(aliases=["es"], description="This function allows you to retrieve the most recent edited message on the server.")
    @commands.check(hasAccount)
    async def editsnipe(self, ctx):
        hehe = False
        if (hehe==False):
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
        else:
            await ctx.channel.send("HAPPY HALLOWEEN <:sussykasra:873330894260297759><:sussykasra:873330894260297759><:sussykasra:873330894260297759><:sussykasra:873330894260297759><:sussykasra:873330894260297759>")

    @commands.command(description="This is a simple argument settler, pick a side, flip a coin and get results. This function has settled many arguments and started many wars.")
    @commands.check(hasAccount)
    async def coin(self, ctx):
        choice = random.randint(1,2)
        embed=discord.Embed()
        embed.color =  discord.Color.random()
        if choice == 1:
            embed.title = "You flipped a coin and got: **heads**!"
            embed.set_image(url=heads)
            await ctx.channel.send(embed=embed)
        elif choice == 2:
            embed.title = "You flipped a coin and got: **tails**!"
            embed.set_image(url=tails)
            await ctx.channel.send(embed=embed)

async def setup(bot):
    await bot.add_cog(Snipe(bot))