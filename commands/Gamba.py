from discord.ext import commands
import os
import requests
import discord 
import random
from dotenv import load_dotenv
from asyncio import gather
import asyncio
from .Config import hasAccount
from classes import Game, User
import io
import asyncio
from discord import app_commands, File, hybrid_command
from sqlalchemy import update
from sqlalchemy.orm import sessionmaker
from classes.database import engine
import random

load_dotenv()
updateUser = os.getenv('UPDATE_USER')
addUser = os.getenv('ADD_USER')
getUser = os.getenv('GET_USER')

class Gamba(commands.Cog, name="Gamba"):
    def __init__(self, client: commands.Bot):
        self.client = client
        Session = sessionmaker(bind=engine)
        session = Session()

    @commands.command(aliases=['cf'], description="This is a simple game where the user selects between heads or tails. You double your wager each time you win. It's simple yet addictive, side bets are always welcome!")
    async def coinflip(self, ctx, bet, amount: int):
        userID = ctx.author.id
        heads = ["heads", "head", "h"]
        tails = ["tails", "tail", "t"]
        bal = requests.get(getUser, params={"f1": "discoins", "f2": ctx.author.id}, headers={"User-Agent": "XY"})
        bal = bal.text.replace('"', '')
        earned = requests.get(getUser, params={"f1": "totalEarned", "f2": userID}, headers={"User-Agent": "XY"})
        e = earned.text.replace('"', '')

        if(amount <= int(bal)):
            if (amount >= self.minCoinBid):
                if((bet.lower() in heads) or (bet.lower() in tails)):
                    bal = requests.get(getUser, params={"f1": "discoins", "f2": userID}, headers={"User-Agent": "XY"})
                    bal = bal.text.replace('"', '')
                    cBal = int(bal) - amount
                    result = random.randint(0,1)
                    if (result == 0 and bet.lower() in heads):
                        total = amount * (1+self.cfMulti)
                        won = total - amount
                        e = int(e) + won
                        afterBet = total + cBal
                        requests.post(updateUser, data={"f1": "discoins", "f2": afterBet, "f3": userID}, headers={"User-Agent": "XY"})
                        requests.post(updateUser, data={"f1": "totalEarned", "f2": e, "f3": userID}, headers={"User-Agent": "XY"})
                        await ctx.send(f"Congrats!!! You won {int(won)} discoins")
                    elif (result == 1 and bet.lower() in tails):
                        total = amount * (1+self.cfMulti)
                        won = total - amount
                        e = int(e) + won
                        afterBet = int(total) + cBal
                        requests.post(updateUser, data={"f1": "totalEarned", "f2": e, "f3": userID}, headers={"User-Agent": "XY"})
                        requests.post(updateUser, data={"f1": "discoins", "f2": afterBet, "f3": userID}, headers={"User-Agent": "XY"})
                        await ctx.send(f"Congrats!!! You won {int(won)} discoins")
                    else:
                        lost = requests.get(getUser, params={"f1": "totalLost", "f2": userID}, headers={"User-Agent": "XY"})
                        l = lost.text.replace('"', '')
                        l = int(l) + amount
                        requests.post(updateUser, data={"f1": "discoins", "f2": int(bal)-amount, "f3": userID}, headers={"User-Agent": "XY"})
                        requests.post(updateUser, data={"f1": "totalLost", "f2": l, "f3": userID}, headers={"User-Agent": "XY"})
                        await ctx.send(f"You lost. lol. -{amount} discoins")
                    betsMade = requests.get(getUser, params={"f1": "betsMade", "f2": userID}, headers={"User-Agent": "XY"})
                    bM = betsMade.text.replace('"', '')
                    bM = int(bM) + 1
                    requests.post(updateUser, data={"f1": "betsMade", "f2": bM, "f3": userID}, headers={"User-Agent": "XY"})
                else:
                    await ctx.send("Please type heads or tails")
            else:
                await ctx.send("Bet more money you poor fuck. The minimum bet is 5 discoins.")
        else:
            await ctx.send("You are too poor to afford this bet. Check your balance before betting next time.")

    @commands.command(description="Lottery style betting functionality, allowing players that have earned coins to pick a number and bet a certain amount to win even more coins. This function is part of our gaming pivot, allowing for more currency based functions.")
    async def bet(self, ctx, bet: int, amount: int):
        userID = ctx.author.id
        bal = requests.get(getUser, params={"f1": "discoins", "f2": ctx.author.id}, headers={"User-Agent": "XY"})
        bal = bal.text.replace('"', '')
        bal = int(bal)

        if (amount <= bal):
            if(bet >= 1 and bet <= 100):
                if (amount >= 0):
                    result = random.randint(1,100)
                    if (result == bet):
                        earned = requests.get(getUser, params={"f1": "totalEarned", "f2": userID}, headers={"User-Agent": "XY"})
                        e = earned.text.replace('"', '')
                        won = amount * 100
                        total = won + bal
                        add = won
                        e = int(e) + add
                        requests.post(updateUser, data={"f1": "discoins", "f2": total, "f3": userID}, headers={"User-Agent": "XY"})
                        requests.post(updateUser, data={"f1": "totalEarned", "f2": e, "f3": userID}, headers={"User-Agent": "XY"})
                        await ctx.send(f"Congrats!!! You won {int(won)} discoins")
                    else:
                        lost = requests.get(getUser, params={"f1": "totalLost", "f2": userID}, headers={"User-Agent": "XY"})
                        l = lost.text.replace('"', '')
                        l = int(l) + amount
                        requests.post(updateUser, data={"f1": "discoins", "f2": bal-amount, "f3": userID}, headers={"User-Agent": "XY"})
                        requests.post(updateUser, data={"f1": "totalLost", "f2": l, "f3": userID}, headers={"User-Agent": "XY"})
                        await ctx.send(f"You lost. You chose **{bet}** but the bot chose **{result}**. Better luck next time.")
                    betsMade = requests.get(getUser, params={"f1": "betsMade", "f2": userID}, headers={"User-Agent": "XY"})
                    bM = betsMade.text.replace('"', '')
                    bM = int(bM) + 1
                    requests.post(updateUser, data={"f1": "betsMade", "f2": bM, "f3": userID}, headers={"User-Agent": "XY"})
                else:
                    await ctx.send("Are you an idiot? You can't bet less than 1 discoin.")
            else:
                await ctx.send("Please choose a number between 1 and 100 for your bet. Including 1 and 100.")
        else:   
            await ctx.send("You are too poor to afford this bet. Check your balance before betting next time.")
    
    @hybrid_command()
    async def setPollGamba(self, ctx, amount):
        if not amount:
            await ctx.send("Please set an amount for your next poll gamble")
        
        userID = ctx.author.id
        bal = requests.get(getUser, params={"f1": "discoins", "f2": ctx.author.id}, headers={"User-Agent": "XY"})
        bal = bal.text.replace('"', '')
        bal = int(bal)

        if amount > bal:
            await ctx.send("You are too poor to afford that gamble")
        
        if amount <= 0:
            await ctx.send("Please bet more than 0")
        
        #set the amount in the database

    @hybrid_command()
    async def payout(self, ctx, poll):
        return
