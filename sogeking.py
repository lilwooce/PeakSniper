import discord
import os
import sys
import traceback
import asyncio
import requests
from discord.ext import commands
from discord import Intents
from dotenv import load_dotenv
import logging
import platform
from discord.ext import commands, tasks
from discord.ui import Button, View
from sqlalchemy.orm import sessionmaker

from classes import Servers, User, database

load_dotenv()
header={"User-Agent": "XY"}
getUser = os.getenv('GET_USER')
updateUser = os.getenv('UPDATE_USER')
addUser = os.getenv('ADD_USER')
updatePURL = os.getenv('UP_URL')
removePURL = os.getenv('RP_URL')
getPURL = os.getenv('GP_URL')
token = os.getenv('DISCORD_TOKEN')

class Client(commands.Bot):
    def __init__(self):
        Session = sessionmaker(bind=database.engine)
        session = Session()
        intents = discord.Intents.default()
        intents.members = True
        intents.message_content = True
        super().__init__(command_prefix='.', intents=intents, description="The Best Snipe Bot")
        self.session = session
        self.game_count = 0

    async def setup_hook(self):
        try:
            synced = await self.tree.sync()
            print(f'Successfully synced {len(synced)} command(s)')
        except Exception as e:
            print(f'Failed to sync commands: {e}')

    async def check_user(self, user):
        if user.bot:
            return
        if not self.session.query(User.User).filter_by(user_id=user.id).first():
            print(f"user not in database {user.name}")
            u = User.User(user=user)
            self.session.add(u)
            self.session.commit()

    async def check_server(self, guild):
        if not self.session.query(Servers.Servers).filter_by(server_id=guild.id).first():
            print(f"guild not in database {guild.name}")
            u = Servers.Servers(server=guild)
            self.session.add(u)
            self.session.commit()

    async def account_check(self):
        async for guild in self.fetch_guilds(limit=None):
            await self.check_server(guild)
            async for member in guild.fetch_members(limit=None):
                await self.check_user(member)

    async def on_ready(self):
        print(f"Logged in as {self.user.name}")
        print(f"Bot ID {str(self.user.id)}")
        print(f"Discord Version {discord.__version__}")
        print(f"Python Version {str(platform.python_version())}")
        await self.setup_hook()
        

        #check to make sure everyone in every server and every server is in the database
        await self.account_check()

        logging.warning("Now logging..")

        # get the initial world count on startup
        
        self.server_count = self.session.query(Servers.Servers).count()

        self.update_bot_status.start()

        #xecuteQueue(client=self).start()

    @tasks.loop(seconds=60)
    async def update_bot_status(self):
        await self.change_presence(status=discord.Status.online, activity=discord.Activity(type=discord.ActivityType.playing , name=f"Fiend Catching Simulator in {self.server_count} servers"))

client = Client()
client.run(os.getenv("DISCORD_TOKEN"))

# @bot.check
# async def checkBanned(ctx):
#     print("checking if user is banned")
#     userID = ctx.author.id
#     member = await ctx.guild.fetch_member(userID)
#     result = requests.get(getUser, params={"f1": "blacklisted", "f2": userID}, headers=header)
#     reason = requests.get(getUser, params={"f1": "reason", "f2": userID}, headers=header)
#     reason = reason.text.replace('"', '')
#     check = result.text.replace('"', '')
#     if (check == str(1)):
#         await ctx.send(f"{member.mention} you have been banned from using commands until future notice. The reason for your ban is as follows: [{reason}]")
#         return False
#     else:
#         return True

@client.event
async def on_raw_reaction_add(payload):
    karuta = await client.fetch_channel('736411674277576835')
    pogDrops = await client.fetch_channel('799452182051160064')
    message = await karuta.fetch_message(payload.message_id)
    reaction = payload.emoji

    if (str(message.author.id) == '646937666251915264' and str(reaction) == "⭐" and message.channel.id == 736411674277576835):
        jumpUrl = message.jump_url
        embed = discord.Embed(
            title=message.author.name,
            description = f"{message.content} \n \n Click to jump to message.({jumpUrl})"
        )
        drop = message.attachments[0].url
        embed.set_image(url=drop)
        await pogDrops.send(embed=embed)

@client.event
async def on_guild_join(guild):
    #add server to database
    return

@client.event
async def on_guild_remove(guild):
    #remove "currentlyUsingBot"
    return
            

@client.event
async def on_message(message):
    if message.author == client.user:
        return
    if isinstance(message.channel, discord.channel.DMChannel):
        embed=discord.Embed(title=f"{message.author.name} dmed the bot", description="")
        if message.content:
            embed.add_field(name= "Caught!" ,value=message.content, inline=True)
            channel=client.get_channel(1191170489280901120)
            await channel.send(embed=embed)
    await client.process_commands(message)


@client.event
async def on_message_delete(message):
    #check server and update database to reflect current most recently deleted message
    if (message.author.bot): return
    embed=discord.Embed(title=f"{message.author.name}#{message.author.discriminator} deleted a message from #{message.channel.name}", description="")
    if (message.content):
        if (len(message.content) > 1024):
            for i in range(0, (len(message.content)), 1024):
                if (i + 1024 < len(message.content)):
                    embed.add_field(name= "Caught!" ,value=message.content[i:i+1024], inline=True)        
                else:
                    embed.add_field(name= "Caught!" ,value=message.content[i:len(message.content)], inline=True)        
        else:
            embed.add_field(name= "Caught!" ,value=message.content, inline=True)
    else:
        embed.add_field(name= "This is the message that has been deleted" ,value="No Message Sent", inline=True)
    if (message.attachments):
        embed.set_image(url=message.attachments[0].url)
        embed.add_field(name="File Name", value=message.attachments[0].url, inline=True)
    channel = client.get_channel(875117826581626891)
    await channel.send(embed=embed)
    await client.process_commands(message)

@client.event
async def on_message_edit(message_before, message_after):
    #same as above on message delete
    channel=client.get_channel(875122190931075122)
    if (message_before.author.bot): return
    if (message_after.author.bot): return
    embed=discord.Embed(title=f"{message_before.author.name} edited a message from #{message_before.channel.name} in {message_before.guild.name}", description="")
    embedA=discord.Embed(title=f"{message_after.author.name} edited a message from #{message_after.channel.name} in {message_after.guild.name}", description="")
    if (message_before.content):
        embed.add_field(name= message_before.content ,value="This is the message before the edit", inline=True)
    else:
        embed.add_field(name="No content" ,value="This is the message before the edit", inline=True)
    if (message_after.content):
        embed.add_field(name= message_after.content ,value="This is the message after the edit", inline=True)
    else:
        embed.add_field(name="No content" ,value="This is the message after the edit", inline=True)
    if (message_before.attachments):
        embed.set_image(url=message_before.attachments[0].url)
        embed.add_field(name="File Name", value=message_before.attachments[0].url, inline=True)
    if (message_after.attachments):
        embedA.set_image(url=message_after.attachments[0].url)
        embed.add_field(name="File Name", value=message_after.attachments[0].url, inline=True)
        await channel.send(channel, embed=embedA)

    await channel.send(channel, embed=embed)

class MyHelpCommand(commands.MinimalHelpCommand):
    async def send_pages(self):
        destination = self.get_destination()
        e = discord.Embed(color=discord.Color.blurple(), description='')
        for page in self.paginator.pages:
            e.description += page
        await destination.send(embed=e)

client.help_command = MyHelpCommand()