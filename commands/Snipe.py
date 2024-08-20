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
from sqlalchemy.orm import sessionmaker

from classes import Servers, User, database

load_dotenv()
tails = os.getenv('heads')
heads = os.getenv('tails')
updateUser = os.getenv('UPDATE_USER')
addUser = os.getenv('ADD_USER')
getUser = os.getenv('GET_USER')

def validCheck(sniper):
    server = sniper.guild
    Session = sessionmaker(bind=database.engine)
    session = Session()
    s = session.query(Servers.Servers).filter_by(server_id=server.id).first()

    if (sniper.id == s.recently_deleted_user):
        return False
    
    return True
    
def validSnipe(user, num):
    Session = sessionmaker(bind=database.engine)
    session = Session()
    u = session.query(User.User).filter_by(user_id=user.id).first()
    
    u.balance += num
    u.total_earned += num
    u.total_snipes += 1
    session.commit()
    session.close()

class Snipe(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.snipeVal = 5

    @commands.Cog.listener()
    async def on_ready(self):
        print(f"{self.__class__.__name__} Cog has been loaded\n----")

    @commands.Cog.listener()
    async def on_message_delete(self, message: discord.Message="None"):
        server = message.guild
        Session = sessionmaker(bind=database.engine)
        session = Session()
        s = session.query(Servers.Servers).filter_by(server_id=server.id).first()

        if message.author.bot == True:
            return
        
        s.recently_deleted_message = message.content
        s.recently_deleted_user = message.author.id
        s.recently_deleted_timestamp = message.created_at

        if (message.attachments):
            for att in message.attachments:
                s.recently_deleted_images += f"{att.url}/"
        else:
            s.recently_deleted_images = ""
        
        if (await self.checkReply(message)):
            s.recently_deleted_reply = message.jump_url
        else:
            s.recently_deleted_reply = ""
                
        session.commit()
        session.close()
        await self.bot.process_commands(message)
    
    @commands.Cog.listener()
    async def on_message_edit(self, messageBefore: discord.Message, messageAfter: discord.Message):
        server = messageAfter.guild
        Session = sessionmaker(bind=database.engine)
        session = Session()
        s = session.query(Servers.Servers).filter_by(server_id=server.id).first()

        if messageBefore.author.bot == True:
            return
        if messageAfter.author.bot == True:
            return
        
        s.recently_edited_before_message = messageBefore.content
        s.recently_edited_after_message = messageAfter.content

        if (messageBefore.attachments):
            for att in messageBefore.attachments:
                s.recently_edited_images += f"{att.url}/"
        else:
            s.recently_edited_images = ""
        
        if (await self.checkReply(messageBefore)):
            s.recently_edited_reply = messageBefore.jump_url
        else:
            s.recently_edited_reply = ""

        session.commit()
        session.close()
            
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
        msg = ""
        numbers = {}
        first = 0
        for x in range(1, numberOfChoices+1):
            numbers[x] = 0

        while firstTo not in numbers.values():
            rolled = random.randint(1, numberOfChoices)
            numbers[rolled] += 1
            msg += f"{ctx.author.name}, rolled a `{rolled}`\n"
            if (numbers[rolled] >= firstTo):
                first = rolled
                msg += f"{first} was the first to reach {firstTo} rolls"

        await ctx.channel.send(msg)
    
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
        user = ctx.author
        server = ctx.guild

        Session = sessionmaker(bind=database.engine)
        session = Session()
        s = session.query(Servers.Servers).filter_by(server_id=server.id).first()
        sniped = s.recently_deleted_message
        timestamp = s.recently_deleted_timestamp
        images = s.recently_deleted_images.split("/")
        sniper = await self.bot.fetch_user(s.recently_deleted_user)
        u = session.query(User.User).filter_by(user_id=user.id).first()
        reply = s.recently_deleted_reply
        channel = self.bot.get_channel(773916648317911140)
        await channel.send(sniper.name)

        hehe = False
        if (hehe==False):
            embed=discord.Embed(title=f"{sniper.name}", description="")
            embed.timestamp = timestamp
            if(sniped):
                if (len(sniped) > 1024):
                    for i in range(0, (len(sniped)), 1024):
                        if (i + 1024 < len(sniped)):
                            embed.add_field(name=u.snipe_message ,value=sniped[i:i+1024], inline=True)     
                        else:
                            embed.add_field(name=u.snipe_message ,value=sniped[i:len(sniped)], inline=True)   
                else:
                    embed.add_field(name= u.snipe_message ,value=sniped, inline=True) 
            else:
                embed.add_field(name= u.snipe_message ,value="No Message Sent", inline=True)

            if (images[0] != ""):
                for img in images:
                    embed.set_image(url=img)
                    embed.add_field(name="File Name", value=img, inline=True)
            if(reply != ""):
                embed.add_field(name="Reply", value=reply, inline=True)  
            
            
            if(sniper.id == 0000000000000000):
                await ctx.channel.send("heh sorry guys. i made a deal.")
            else:
                await ctx.channel.send(embed=embed)
                if validCheck(sniper):
                    validSnipe(sniper, self.snipeVal)  
        else:
            await ctx.channel.send("HAPPY HALLOWEEN <:sussykasra:873330894260297759><:sussykasra:873330894260297759><:sussykasra:873330894260297759><:sussykasra:873330894260297759><:sussykasra:873330894260297759>")

    @commands.command(aliases=["es"], description="This function allows you to retrieve the most recent edited message on the server.")
    @commands.check(hasAccount)
    async def editsnipe(self, ctx):
        user = ctx.author
        server = ctx.guild

        Session = sessionmaker(bind=database.engine)
        session = Session()
        s = session.query(Servers.Servers).filter_by(server_id=server.id).first()
        messageB = s.recently_edited_before_message
        messageA = s.recently_edited_after_message
        timestamp = s.recently_edited_timestamp
        images = s.recently_edited_images.split("/")
        snipee = await self.bot.fetch_user(s.recently_edited_user)
        reply = s.recently_edited_reply

        hehe = False
        if (hehe==False):
            embed=discord.Embed(title=f"{snipee.name} edited a message <:sussykasra:873330894260297759>", description="")
            embed.timestamp = timestamp
            embedA=discord.Embed(title=f"{messageA.author.name} edited a message from <:sussykasra:873330894260297759>", description="")
            embedA.timestamp = timestamp
            if (messageB):
                embed.add_field(name= messageB ,value="Before", inline=True)
            else:
                embed.add_field(name="No content" ,value="Before", inline=True)

            if (messageA):
                embed.add_field(name= messageA ,value="After", inline=True)
            else:
                embed.add_field(name="No content" ,value="After", inline=True)
            
            if (images[0] != ""):
                for img in images:
                    embedA.set_image(url=img)
                    embedA.add_field(name="File Name", value=img, inline=True)
                    embed.set_image(url=img)
                    embed.add_field(name="File Name", value=img, inline=True)
            if(reply != ""):
                embed.add_field(name="Reply", value=reply, inline=True)  
                embedA.add_field(name="Reply", value=reply, inline=True)  
                
            await ctx.channel.send(embed=embed)
        else:
            await ctx.channel.send("HAPPY HALLOWEEN <:sussykasra:873330894260297759><:sussykasra:873330894260297759><:sussykasra:873330894260297759><:sussykasra:873330894260297759><:sussykasra:873330894260297759>")

    @commands.command(description="This is a simple argument settler, pick a side, flip a coin and get results. This function has settled many arguments and started many wars.")
    @commands.check(hasAccount)
    async def coin(self, ctx):
        choice = random.randint(1,2)
        embed=discord.Embed()
        embed.color = discord.Color.random()
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