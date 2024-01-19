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
from stability_sdk import client
import stability_sdk.interfaces.gooseai.generation.generation_pb2 as generation
from packaging import version

required_version = version.parse("1.1.1")
current_version = version.parse(openai.__version__)

if current_version < required_version:
    raise ValueError(f"Error: OpenAI version {openai.__version__}"
                     " is less than the required version 1.1.1")
else:
    print("OpenAI version is compatible.")
    
from openai import OpenAI

os.environ['STABILITY_HOST'] = 'grpc.stability.ai:443'
load_dotenv()
openAIKey = os.getenv("OPENAI_API_KEY")
client = OpenAI(api_key=openAIKey)
os.environ['STABILITY_KEY'] = os.getenv('STABILITY_KEY')
updatePURL = os.getenv('UP_URL')
removePURL = os.getenv('RP_URL')
getPURL = os.getenv('GP_URL')

stability_api = client.StabilityInference(
    key=os.environ['STABILITY_KEY'], # API Key reference.
    verbose=True, # Print debug messages.
    engine="stable-diffusion-v1-5", # Set the engine to use for generation. 
    # Available engines: stable-diffusion-v1 stable-diffusion-v1-5 stable-diffusion-512-v2-0 stable-diffusion-768-v2-0 
    # stable-diffusion-512-v2-1 stable-diffusion-768-v2-1 stable-inpainting-v1-0 stable-inpainting-512-v2-0
)

class AI(commands.Cog, name="OpenAI"):
    def __init__(self, bot):
        self.bot = bot

    @commands.Cog.listener()
    async def on_ready(self):
        print(f"{self.__class__.__name__} Cog has been loaded\n----")

    @commands.command(aliases=["i"])
    async def Image(self, ctx, *, p):
        answers = stability_api.generate(
            prompt=str(p),
            seed=992446758, # If a seed is provided, the resulting generated image will be deterministic.
                            # What this means is that as long as all generation parameters remain the same, you can always recall the same image simply by generating it again.
                            # Note: This isn't quite the case for Clip Guided generations, which we'll tackle in a future example notebook.
            steps=30, # Amount of inference steps performed on image generation. Defaults to 30. 
            cfg_scale=8.0, # Influences how strongly your generation is guided to match your prompt.
                        # Setting this value higher increases the strength in which it tries to match your prompt.
                        # Defaults to 7.0 if not specified.
            width=1024, # Generation width, defaults to 512 if not included.
            height=1024, # Generation height, defaults to 512 if not included.
            samples=1, # Number of images to generate, defaults to 1 if not included.
            sampler=generation.SAMPLER_K_DPMPP_2M # Choose which sampler we want to denoise our generation with.
                                                        # Defaults to k_dpmpp_2m if not specified. Clip Guidance only supports ancestral samplers.
                                                        # (Available Samplers: ddim, plms, k_euler, k_euler_ancestral, k_heun, k_dpm_2, k_dpm_2_ancestral, k_dpmpp_2s_ancestral, k_lms, k_dpmpp_2m)
        )

        # Set up our warning to print to the console if the adult content classifier is tripped.
        # If adult content classifier is not tripped, save generated images.
        for resp in answers:
            for artifact in resp.artifacts:
                if artifact.finish_reason == generation.FILTER:
                    warnings.warn(
                        "Your request activated the API's safety filters and could not be processed."
                        "Please modify the prompt and try again.")
                    await ctx.channel.send("Your request activated the API's safety filters and could not be processed. Please modify the prompt and try again.")
                if artifact.type == generation.ARTIFACT_IMAGE:
                    img = Image.open(io.BytesIO(artifact.binary))
                    with io.BytesIO() as image_binary:
                        img.save(image_binary, 'PNG')
                        image_binary.seek(0)
                        await ctx.send(file=discord.File(fp=image_binary, filename='image.png')) 

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
        try:
            response = openai.chat.completions.create(
                model="gpt-3.5-turbo-instruct",
                temperature=2,
                max_tokens=4000,
                top_p=1.0,
                response_format={ "type": "json_object" },
                frequency_penalty=0.0,
                presence_penalty=0.0,
                messages=[
    				{"role": "system", "content": "You are a helpful assistant designed to give the best response to any given question."},
    				{"role": "user", "content": p}
                ]
            )
        except Exception as e:
            traceback.print_exc()
            
        await ctx.channel.send(response.choices[0].message.content)

async def setup(bot):
    await bot.add_cog(AI(bot))