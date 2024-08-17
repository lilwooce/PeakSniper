from discord.ext import commands
import os
import requests
import discord 
from dotenv import load_dotenv
import os
import openai
import traceback
import io
import warnings
from PIL import Image
from packaging import version

required_version = version.parse("1.1.1")
current_version = version.parse(openai.__version__)

if current_version < required_version:
    raise ValueError(f"Error: OpenAI version {openai.__version__}"
                     " is less than the required version 1.1.1")
else:
    print("OpenAI version is compatible.")

from openai import OpenAI

load_dotenv()
openAIKey = os.getenv("OPENAI_API_KEY")
client = OpenAI(api_key=openAIKey)
updatePURL = os.getenv('UP_URL')
removePURL = os.getenv('RP_URL')
getPURL = os.getenv('GP_URL')

class Social(commands.Cog, name="Social"):
    def __init__(self, bot):
        self.bot = bot

    @commands.Cog.listener()
    async def on_ready(self):
        print(f"{self.__class__.__name__} Cog has been loaded\n----")

    @commands.command(aliases=["gi"])
    async def GenerateImage(self, ctx, num, *, p):
        num = int(num) or 1
        if(num > 10):
            num = 10
            await ctx.send("You can't make more than 10 pics at the same time.")
        p = p or "Munchkin Cat"
        try:
            response = openai.Image.create(
                prompt=str(p),
                n=num,
                size="1024x1024"
            )
        except Exception as e:
            execp = traceback.format_exec()
            await ctx.channel.send(execp)
            traceback.print_exc()

        for x in range(num):
            image_url = response['data'][x]['url']
            await ctx.channel.send(image_url)
    
    @commands.command(aliases=["a"])
    async def answer(self, ctx, *, p):
        print('answer command starting')
        try:
            response = client.chat.completions.create(
                model="gpt-3.5-turbo",
                temperature=0.5,
                max_tokens=4000,
                top_p=1.0,
                frequency_penalty=0.0,
                presence_penalty=0.0,
                messages=[
    				{"role": "system", "content": "You are a helpful chatbot assistant designed to give the best response to any given question. You excel at explaining complex concepts in simple language so that they can be understood by the general public. Use natural language and phrasing that a real person would use in everyday conversations. No more than 10 percent of your responses should be in passive voice."},
    				{"role": "user", "content": p}
                ]
            )
        except Exception as e:
            traceback.print_exc()
            
        await ctx.channel.send(response.choices[0].message.content)

async def setup(bot):
    await bot.add_cog(Social(bot))  