import os

import discord
import openai
from discord import SlashCommand, Option
from discord.ext import commands
from dotenv import load_dotenv

from config import PROMPTS, MAX_HISTORY
from process_command import (
    process_command,
    get_history_description,
    get_regenerate_data,
    HistoryItem,
)

load_dotenv()

# openai
openai.api_key = os.environ["OPENAI_API_KEY"]

# discord
intents = discord.Intents.default()
bot = commands.Bot(intents=intents)


@bot.event
async def on_message(message):
    from process_command import last_command

    if message.author == bot.user:
        return

    if last_command is None:
        command_list = []
        for k in PROMPTS:
            command_list.append("`/{}`: {}".format(k, PROMPTS[k]["description"]))
        await message.channel.send(
            "You don't have any previous messages. Please use the following command list:\n\n{}".format(
                "\n".join(command_list)
            )
        )
        return

    # await message.channel.send("hello")
    if message.content:
        await process_command(
            bot=bot,
            command_name=last_command.command,
            ctx=message,
            prompt=message.content,
            temperature=last_command.temperature,
            history=0,
            max_tokens=last_command.max_tokens,
            continue_conv=True,
            is_regenerate=False,
        )


@bot.slash_command(name="regenerate")
async def on_regenerate(
    ctx,
    continue_conv: bool = None,
    temperature: float = None,
):
    author = str(ctx.author)
    data: HistoryItem = get_regenerate_data(author=author)
    if data is None:
        return await ctx.respond("You have no messages.")
    if temperature is None:
        temperature = data.temperature
    if continue_conv is None:
        continue_conv = data.continue_conv
    await process_command(
        bot=bot,
        command_name=data.command,
        ctx=ctx,
        prompt=data.prompt,
        temperature=temperature,
        history=0,
        max_tokens=1000,
        continue_conv=continue_conv,
        is_regenerate=False,
    )


@bot.slash_command(name="show_history")
async def command_show_history(ctx, history: int):
    author = str(ctx.author)
    history_description = get_history_description(author, history)

    if len(history_description) == 0:
        history_description = "There is no message history"

    await ctx.respond("```diff\n{}```".format(history_description))


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


def get_command(name: str):
    config_options = PROMPTS[name]["options"] if "options" in PROMPTS[name] else {}

    prompt_options = Option(str, description="Prompt", name="prompt")
    if "prompt" in config_options:
        prompt_config_options = config_options["prompt"]
        if "description" in prompt_config_options:
            prompt_options.description = prompt_config_options["description"]
        if "name" in prompt_config_options:
            prompt_options.name = prompt_config_options["name"]

    async def _command(
        ctx,
        prompt: prompt_options,
        continue_conv: Option(
            bool, description="Continue conversion", default=False, autocomplete=True
        ),
        temperature: Option(
            float,
            description="What sampling temperature to use, between 0 and 2. Higher values will make the output more random",
            default=PROMPTS[name]["temperature"],
            min_value=0.0,
            max_value=2.0,
        ),
        history: Option(
            int,
            description="To continue the conversation, how many previous messages will be used?",
            min_value=0,
            default=0,
            max_value=MAX_HISTORY,
        ),
        max_tokens: Option(
            int,
            description="The maximum number of tokens to generate in the completion.",
            default=1000,
            min_value=1,
        ),
    ):
        await process_command(
            bot=bot,
            command_name=name,
            ctx=ctx,
            prompt=prompt,
            temperature=temperature,
            history=history,
            max_tokens=max_tokens,
            continue_conv=continue_conv,
        )

    return _command


for command_name in PROMPTS:
    bot.add_application_command(
        SlashCommand(
            func=get_command(command_name),
            name=command_name,
            description=PROMPTS[command_name]["description"],
        )
    )


@bot.event
async def on_ready():
    print(f"We have logged in as {bot.user}")


bot.run(os.environ["BOT_TOKEN"])
