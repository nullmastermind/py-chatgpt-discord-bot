import os

import discord
import openai
from discord.ext import commands
from dotenv import load_dotenv

from config import PROMPTS
from generate import generate
from process_command import process_command

load_dotenv()

# openai
openai.api_key = os.environ["OPENAI_API_KEY"]

# discord
intents = discord.Intents.default()
bot = commands.Bot(intents=intents)


@bot.slash_command(name="start")
async def on_start(ctx, prompt: str):
    await ctx.respond("Good job! Your prompt: {}".format(prompt))


@bot.slash_command(name="set_openai_api_key")
async def on_start(ctx, openai_api_key: str):
    if len(openai_api_key) < 5:
        await ctx.respond("The value of OPENAI_API_KEY is invalid.")
        return

    def mask_string(s):
        return "*" * (len(s) - 3) + s[-3:]

    openai.api_key = openai_api_key
    await ctx.respond(
        "The OPENAI_API_KEY has been set to {}.".format(mask_string(openai_api_key))
    )


def run_commands():
    from generated_commands import generated_commands

    generated_commands(bot=bot, process_command=process_command, prompts=PROMPTS)


generate()
run_commands()


@bot.event
async def on_ready():
    print(f"We have logged in as {bot.user}")


bot.run(os.environ["BOT_TOKEN"])
