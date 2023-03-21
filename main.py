import os
import sys

import discord
from discord.ext import commands
from dotenv import load_dotenv
import openai
import time

from utility import is_message_limit

load_dotenv()

# openai
openai.api_key = os.environ["OPENAI_API_KEY"]

# discord
intents = discord.Intents.default()
intents.message_content = True

bot = commands.Bot(command_prefix="/", intents=intents)

OPENAI_COMPLETION_OPTIONS = {
    "temperature": 0.2,
    "max_tokens": 1000,
    "top_p": 1,
    "frequency_penalty": 0,
    "presence_penalty": 0,
}


@bot.command(name="code")
async def on_code(ctx, prompt: str):
    print("prompt: {}".format(prompt))
    message = await ctx.send("Thingking...")
    answer = ""
    start_time = time.time()
    for r in openai.ChatCompletion.create(
        model="gpt-3.5-turbo",
        messages=[
            {
                "role": "system",
                "content": "As an advanced chatbot named NullGPT, your primary goal is to assist users to write code. This may involve designing/writing/editing/describing code or providing helpful information. Where possible you should provide code examples to support your points and justify your recommendations or solutions. Make sure the code you provide is correct and can be run without errors. Be detailed and thorough in your responses. Your ultimate goal is to provide a helpful and enjoyable experience for the user. Write code inside ```{code}```.",
            },
            {"role": "user", "content": prompt},
        ],
        stream=True,
        **OPENAI_COMPLETION_OPTIONS,
    ):
        if "content" in r.choices[0]["delta"]:
            answer += r.choices[0]["delta"]["content"]
            if len(answer.strip()) > 0 and time.time() - start_time >= 1.0:
                start_time = time.time()
                if is_message_limit(answer):
                    await message.edit(content=answer.strip())
                    message = await ctx.send("Thingking...")
                    answer = ""
                else:
                    await message.edit(content=answer.strip())
    if len(answer.strip()) == 0:
        answer = "No answer."
    await message.edit(content=answer.strip())


@bot.event
async def on_ready():
    print(f"We have logged in as {bot.user}")


bot.run(os.environ["BOT_TOKEN"])
