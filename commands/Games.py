from discord.ext import commands
import os
import requests
import discord 
import random
from dotenv import load_dotenv
from asyncio import gather
import asyncio
from .Config import hasAccount
from classes import Game, Gift, User

load_dotenv()
updateUser = os.getenv('UPDATE_USER')
addUser = os.getenv('ADD_USER')
getUser = os.getenv('GET_USER')

class Games(commands.Cog, name="Games"):
    def __init__(self, bot):
        self.bot = bot
        self.minCoinBid = 1
        self.cfMulti = 1

    @commands.Cog.listener()
    async def on_ready(self):
        print(f"{self.__class__.__name__} Cog has been loaded\n----")
    
    @commands.command(aliases=["we"], description="Starts a game of White Elephant, a classic party game where each player chooses a secret gift from a pile of them. Players then take turns opening and exchanging gifts with each other, with the goal of ending up with the best gift in the room.")
    @commands.check(hasAccount)
    async def WhiteElephant(self, ctx):
        timeout = 30
        minimumPlayers = 2
        randomSeed = random.randint(1,99999999)
        channel = ctx.channel
        currentPlayer = None
        recentlyStolen = None
        turns = 1
        users = []
        gifts = []

        msg = await ctx.send(f"A new White Elephant game is being created. Please react to the 👍 within {timeout} seconds if you would like to join this game.")
        await msg.add_reaction("👍")
        await asyncio.sleep(timeout)
        msg = await ctx.fetch_message(msg.id)
        
        for reaction in msg.reactions:
            user_list = [user async for user in reaction.users() if user != self.bot.user]
            if (str(reaction) == "👍") and (len(user_list) >= minimumPlayers):
                async for user in reaction.users():
                    if not user.bot:
                        member = await ctx.guild.fetch_member(user.id)
                        u = User.User(user.id)
                        users.append(u)
                        await member.send(f"You have joined a game of White Elephant in, {ctx.guild.name}!")
            elif reaction != "👍":
                continue
            else:
                await ctx.send(f"Not enough people joined the game. At least {minimumPlayers} players need to react in order to start a game of White Elephant.")

        newGame = Game.Game(randomSeed, users)

        for player in newGame.getPlayers():
            member = await ctx.guild.fetch_member(player.getID())
            embed = discord.Embed()
            await member.send(f"The game is starting soon, you will have 2 minute to decide what gift you will give. For your next message, type a short description of what your gift is. If you would like, add an image to this description.")
            try:
                msg = await self.bot.wait_for('message', check=lambda message: message.author == member and isinstance(message.channel, discord.DMChannel), timeout=120)
                if not msg.attachments:
                    g = Gift.Gift(msg.content)
                else:
                    g = Gift.Gift(msg.content, msg.attachments[0].url)
                player.setGift(g)
                gifts.append(g)
                embed.title = g.getText()
                if(g.getImage() == None):
                    await member.send(embed=embed)
                else:
                    embed.set_image(url=g.getImage())
                    await member.send(embed=embed)
            except asyncio.TimeoutError:
                g = Gift.Gift("No gift supplied")
                player.setGift(g)
                gifts.append(g)
            turns +=1

        stealing = False
        grabbing = False

        while turns > 0:
            if currentPlayer == None:
                currentPlayer = newGame.getPlayers()[0]
            member = await ctx.guild.fetch_member(currentPlayer.getID())

            m = await ctx.channel.send(f"{member.mention} Please either choose a gift from the pile (g) or steal someone else's gift (s).")
            r = await self.bot.wait_for('message', check=lambda message: message.author == member and message.channel == channel, timeout=30)
            r = str(r.content)
            if r.lower() == "g":
                grabbing = True
                numGifts = len(gifts)
                while grabbing:
                    if(numGifts > 1):
                        await ctx.send(f"Please choose a number between 1 and {numGifts}.")
                        reply = await self.bot.wait_for('message', check=lambda message: message.author == member and message.channel == channel, timeout=30)
                        try:
                            reply =  int(reply.content)
                        except ValueError:
                            await ctx.send("That is not a valid number.")
                            continue
                        else:
                            if not (1 <= reply <= numGifts):
                                await ctx.send("That is not a valid number in the provided range.")
                                continue
                            else:
                                currentPlayer.setRecieve(gifts[reply-1])
                                grabbing = False
                    elif (numGifts == 1):
                        currentPlayer.setRecieve(gifts[0])
                        grabbing = False
                    else:
                        await ctx.send("There are no gifts for you to grab from the pile, please steal one from someone else.")
                        continue
                    embed = discord.Embed()
                    plrGift = currentPlayer.getRecieve()
                    text = plrGift.getText()
                    img = plrGift.getImage()
                    embed.title = text
                    embed.set_image(url=img)
                    await ctx.send(f"Congratulations {member.mention}, you grabbed a gift!", embed=embed)
                    gifts.remove(plrGift)
                    nextPlayer = None
                    if (len(gifts) > 0):
                        for u in users:
                            if u.getRecieve():
                                continue
                            else:
                                nextPlayer = u
                        currentPlayer = nextPlayer
                    turns -= 1
                    grabbing = False
            elif r.lower() == "s":
                stealing = True
                if (len(gifts) == len(users)):
                    await ctx.channel.send(f"No gifts have been taken yet you fucking dumbass, why would you choose this option?")
                    grabbing = False
                    continue
                else:
                    while stealing == True:
                        await ctx.send(f"Please mention the player you would like to steal from.")
                        reply = await self.bot.wait_for('message', check=lambda message: message.author == member and message.channel == channel, timeout=30)
                        if (reply.mentions):
                            reply = reply.mentions[0].id
                            if not newGame.getPlayer(reply):
                                await ctx.send("This user is not in the game.")
                                continue
                        else:
                            continue
                        
                        plr = newGame.getPlayer(reply)
                        gift = plr.getRecieve()
                        if(gift != None):
                            if(currentPlayer != recentlyStolen) and (gift.canSteal()):
                                currentPlayer.setRecieve(gift)
                                nextPlayer = plr
                                currentPlayer = nextPlayer
                                recentlyStolen = nextPlayer
                                stealing = False
                                embed = discord.Embed()
                                text = gift.getText()
                                img = gift.getImage()
                                embed.title = text
                                embed.set_image(url=img)
                                await ctx.send(f"Congratulations {member.mention}, you stole a gift!", embed=embed)
                            else:
                                await ctx.send(f"This player does not have a gift that can be stolen, please choose another person.")
                                continue
                        else:
                            await ctx.send(f"This player does not have a gift that can be stolen, please choose another person.")
                            continue
            if turns==1:
                currentPlayer = newGame.getPlayers()[0]
                member = await ctx.guild.fetch_member(currentPlayer.getID())
                m = await ctx.channel.send(f"{member.mention} Final turn! Would you like to keep the gift that you have (k) or swap it with someone else's (s)?")
                r = await self.bot.wait_for('message', check=lambda message: message.author == member and message.channel == channel, timeout=30)
                r = r.content
                swapping = True

                if r.lower() == "k":
                    gift = currentPlayer.getGift()
                    embed = discord.Embed()
                    text = gift.getText()
                    img = gift.getImage()
                    embed.title = text
                    embed.set_image(url=img)
                    await ctx.send("Congratulations! You kept this gift!", embed=embed)
                    turns = 0
                elif r.lower()  == "s":
                    while swapping == True:
                        await ctx.send(f"Please mention the player you would like to swap with.")
                        reply = await self.bot.wait_for('message', check=lambda message: message.author == member and message.channel == channel, timeout=30)
                        if (reply.mentions):
                            reply = reply.mentions[0].id
                            if not newGame.getPlayer(reply):
                                await ctx.send("This user is not in the game.")
                                continue
                        else:
                            continue
                        
                        currentGift = currentPlayer.getGift()
                        plr = newGame.getPlayer(reply)
                        gift = plr.getRecieve()
                        if (gift.canSteal()):
                            currentPlayer.setRecieve(gift)
                            plr.setRecieve(currentGift)
                            swapping = False
                            turns = 0
                            embed = discord.Embed()
                            text = gift.getText()
                            img = gift.getImage()
                            embed.title = text
                            embed.set_image(url=img)
                            await ctx.send(f"Congratulations {member.mention}, you swapped for a gift!", embed=embed)
                            turns = 0
                        else:
                            await ctx.send(f"This gift cannot be swapped with, please choose another.")
                            continue
        print("GAME COMPLETE")
        msg = ""
        for player in newGame.getPlayers():
            reciever = newGame.getReciever(player.getGift())
            pMember = await ctx.guild.fetch_member(player.getID())
            rMember = await ctx.guild.fetch_member(reciever.getID())
            msg += f"{pMember.mention} gifted {player.getGift().getText()} to {rMember.mention} \n"
        await ctx.send(msg)        
            
async def setup(bot):
    await bot.add_cog(Games(bot)) 