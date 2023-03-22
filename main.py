import os

import discord
import openai
from discord.ext import commands
from dotenv import load_dotenv

from config import PROMPTS
from generate import generate
from process_command import process_command, histories
from utility import cut_string_to_json

load_dotenv()

# openai
openai.api_key = os.environ["OPENAI_API_KEY"]

# discord
intents = discord.Intents.default()
bot = commands.Bot(intents=intents)


@bot.slash_command(name="start")
async def on_start(ctx, prompt: str):
    await ctx.respond("Good job! Your prompt: {}".format(prompt))


@bot.slash_command(name="show_history")
async def command_show_history(ctx, history: int):
    author = str(ctx.author)
    messages = []

    if history > 0 and len(histories[author]) > 0:
        num_pass_his = history
        history_messages = []
        for i in range(0, history):
            if num_pass_his <= 0:
                break
            index = len(histories[author]) - i - 1
            if len(histories[author]) > index >= 0:
                history_messages.append(
                    {
                        "role": histories[author][index]["role"],
                        "content": histories[author][index]["content"],
                    }
                )
                if histories[author][index]["role"] == "user":
                    num_pass_his -= 1
        for msg in history_messages[::-1]:
            messages.append(msg)

    str_messages = []

    for msg in messages:
        str_messages.append(
            "{}: {}".format(msg["role"], cut_string_to_json(msg["content"]))
        )

    await ctx.respond("```{}```".format("\n".join(str_messages)))


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
