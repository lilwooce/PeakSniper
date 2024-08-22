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
from sqlalchemy.orm import sessionmaker
from .Config import hasAccount
from classes import Servers, User, database
import logging

load_dotenv()
tails = os.getenv('heads')
heads = os.getenv('tails')

def validCheck(sniper):
    server = sniper.guild
    logging.warning(server.id)
    Session = sessionmaker(bind=database.engine)
    session = Session()
    
    try:
        u = session.query(User.User).filter_by(user_id=sniper.id).first()
        s = session.query(Servers.Servers).filter_by(server_id=server.id).first()
        if sniper.id != s.recently_deleted_user and u.last_snipe != s.recently_deleted_user:
            return True
        return False
    finally:
        session.close()

def validSnipe(user, num):
    Session = sessionmaker(bind=database.engine)
    session = Session()
    
    try:
        u = session.query(User.User).filter_by(user_id=user.id).first()
        u.balance += num
        u.total_earned += num
        u.total_snipes += 1
        session.commit()
    finally:
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
        if message.author.bot:
            return

        server = message.guild
        Session = sessionmaker(bind=database.engine)
        session = Session()

        try:
            s = session.query(Servers.Servers).filter_by(server_id=server.id).first()
            if not s:
                return

            s.recently_deleted_message = message.content
            s.recently_deleted_user = message.author.id
            s.recently_deleted_timestamp = message.created_at

            if message.attachments:
                s.recently_deleted_images = "/".join(att.url for att in message.attachments)
            else:
                s.recently_deleted_images = ""

            s.recently_deleted_reply = message.jump_url if await self.checkReply(message) else ""
            
            session.commit()
        finally:
            session.close()

        await self.bot.process_commands(message)
    
    @commands.Cog.listener()
    async def on_message_edit(self, messageBefore: discord.Message, messageAfter: discord.Message):
        if messageBefore.author.bot or messageAfter.author.bot:
            return

        server = messageAfter.guild
        Session = sessionmaker(bind=database.engine)
        session = Session()

        try:
            s = session.query(Servers.Servers).filter_by(server_id=server.id).first()
            if not s:
                return

            s.recently_edited_before_message = messageBefore.content
            s.recently_edited_after_message = messageAfter.content

            if messageBefore.attachments:
                s.recently_edited_images = "/".join(att.url for att in messageBefore.attachments)
            else:
                s.recently_edited_images = ""

            s.recently_edited_reply = messageBefore.jump_url if await self.checkReply(messageBefore) else ""

            session.commit()
        finally:
            session.close()
    
    @commands.command(description="Roll a dice with a range of 1 to the specified number.")
    async def roll(self, ctx, arg: int):
        try:
            randValue = random.randint(1, arg)
            await ctx.channel.send(f"{ctx.author.mention}, rolled a `{randValue}`")
        except:
            await ctx.channel.send("Please input a valid number")
    
    @commands.command(aliases=["ftn"])
    async def firstToNum(self, ctx, firstTo: int, numberOfChoices: int):
        msg = ""
        numbers = {x: 0 for x in range(1, numberOfChoices+1)}

        while firstTo not in numbers.values():
            rolled = random.randint(1, numberOfChoices)
            numbers[rolled] += 1
            msg += f"{ctx.author.name}, rolled a `{rolled}`\n"
            if numbers[rolled] >= firstTo:
                msg += f"{rolled} was the first to reach {firstTo} rolls"
                break

        await ctx.channel.send(msg)
    
    async def getReply(self, m):
        if m.reference is None:
            return "Not replying to anything"
        
        channel = self.bot.get_channel(m.reference.channel_id)
        msg = await channel.fetch_message(m.reference.message_id)
        return msg if m.reference.cached_message is None else m.reference.cached_message

    async def checkReply(self, m):
        return m.reference is not None

    @commands.command(aliases=["s"], description="Retrieve the most recent deleted message on the server.")
    @commands.check(hasAccount)
    async def snipe(self, ctx):
        user = ctx.author
        server = ctx.guild

        Session = sessionmaker(bind=database.engine)
        session = Session()
        
        try:
            s = session.query(Servers.Servers).filter_by(server_id=server.id).first()
            u = session.query(User.User).filter_by(user_id=user.id).first()
            if not s:
                await ctx.channel.send("No snipes available")
                return
            if not u:
                await ctx.send("User does not have any data")
                return

            guild = await self.bot.fetch_guild(s.server_id)
            sniper = await guild.fetch_member(s.recently_deleted_user)
            images = s.recently_deleted_images.split("/")
            reply = s.recently_deleted_reply
            
            embed = discord.Embed(title=f"{sniper.name}", description="")
            embed.timestamp = s.recently_deleted_timestamp

            if s.recently_deleted_message:
                self.add_long_field(embed, u.snipe_message, s.recently_deleted_message)
            else:
                embed.add_field(name=u.snipe_message, value="No Message Sent", inline=True)
            
            for img in images:
                if img:
                    embed.set_image(url=img)
                    embed.add_field(name="File Name", value=img, inline=True)
            
            if reply:
                embed.add_field(name="Reply", value=reply, inline=True)
            
            if validCheck(user):
                validSnipe(user, self.snipeVal)

            await ctx.channel.send(embed=embed)
        finally:
            session.close()

    @commands.command(aliases=["es"], description="Retrieve the most recent edited message on the server.")
    @commands.check(hasAccount)
    async def editsnipe(self, ctx):
        user = ctx.author
        server = ctx.guild

        Session = sessionmaker(bind=database.engine)
        session = Session()

        try:
            s = session.query(Servers.Servers).filter_by(server_id=server.id).first()
            if not s:
                await ctx.channel.send("No snipes available")
                return

            guild = await self.bot.fetch_guild(s.server_id)
            sniper = await guild.fetch_member(s.recently_edited_user)
            images = s.recently_edited_images.split("/")
            reply = s.recently_edited_reply
            
            embed = discord.Embed(title=f"{sniper.name} edited a message", description="")
            embed.timestamp = s.recently_edited_timestamp

            if s.recently_edited_before_message:
                embed.add_field(name="Before", value=s.recently_edited_before_message, inline=True)
            else:
                embed.add_field(name="Before", value="No content", inline=True)

            if s.recently_edited_after_message:
                embed.add_field(name="After", value=s.recently_edited_after_message, inline=True)
            else:
                embed.add_field(name="After", value="No content", inline=True)

            for img in images:
                if img:
                    embed.set_image(url=img)
                    embed.add_field(name="File Name", value=img, inline=True)
            
            if reply:
                embed.add_field(name="Reply", value=reply, inline=True)
            
            await ctx.channel.send(embed=embed)
        finally:
            session.close()

    @commands.command(description="Flip a coin to settle arguments.")
    @commands.check(hasAccount)
    async def coin(self, ctx):
        choice = random.randint(1, 2)
        message = tails if choice == 2 else heads
        await ctx.channel.send(message)

    def add_long_field(self, embed, name, value):
        while value:
            embed.add_field(name=name, value=value[:1024], inline=True)
            value = value[1024:]

async def setup(bot):
    await bot.add_cog(Snipe(bot))
