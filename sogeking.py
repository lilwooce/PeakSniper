import discord
import os
import sys
import traceback
import requests
from discord.ext import commands
from dotenv import load_dotenv

load_dotenv()   
updatePURL = os.getenv('UP_URL')
removePURL = os.getenv('RP_URL')
getPURL = os.getenv('GP_URL')
intents = discord.Intents.default()
intents.members = True
token = os.getenv('DISCORD_TOKEN')

def get_prefix(client, message):
    print("starting getprefix")
    obj = {"f1": "server", "q1": message.guild.id}
    print("obj gotten")
    result = requests.get(getPURL, params=obj, headers={"User-Agent": "XY"})
    prefix = result.text.strip('\"')
    print("got prefix")
    return prefix

bot = commands.Bot(command_prefix=get_prefix, intents=intents, description="The Best Snipe Bot")

initial_extensions = {
    "cogs.Config",
    "cogs.Snipe",
    "cogs.Music"
}


@bot.event
async def on_ready():
    print(f'{bot.user} has connected')
    activity = discord.Game(name="Fiend Catching Simulator")
    await bot.change_presence(status=discord.Status.online, activity=activity)

@bot.event
async def on_raw_reaction_add(payload):
    karuta = await bot.fetch_channel('736411674277576835')
    pogDrops = await bot.fetch_channel('799452182051160064')
    message = await karuta.fetch_message(payload.message_id)
    reaction = payload.emoji

    if (str(message.author.id) == '646937666251915264' and str(reaction) == "⭐"):
        jumpUrl = message.jump_url
        embed = discord.Embed(
            title=message.author.name,
            description = f"{message.content} \n \n Click to jump to message.({jumpUrl})"
        )
        drop = message.attachments[0].url
        embed.set_image(url=drop)
        await pogDrops.send(embed=embed)

@bot.event
async def on_guild_join(guild):
    obj = {"f1": guild.id, "q1": '!'}
    result = requests.post(updatePURL, data=obj, headers={"User-Agent": "XY"})
    print(result.status_code)

@bot.event
async def on_guild_remove(guild):
    obj = {"q1": guild.id}
    result = requests.post(removePURL, data=obj, headers={"User-Agent": "XY"})
    print(result.status_code)


for extension in initial_extensions:
    try:
        bot.load_extension(extension)
    except Exception as e:
        print(f'Failed to load extension {extension}.', file=sys.stderr)
        traceback.print_exc()

@bot.event
async def on_message_delete(message):
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
    channel=bot.get_channel(875117826581626891)
    await channel.send(embed=embed)

@bot.event
async def on_message_edit(message_before, message_after):
    channel=bot.get_channel(875122190931075122)
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

bot.run(token)
