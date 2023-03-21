import time

import openai

from config import OPENAI_COMPLETION_OPTIONS, CHAT_BOT_NAME, PROMPTS, MODEL, MAX_HISTORY
from utility import is_message_limit, break_answer, preprocess_prompt
from views import get_buttons

histories = {
    "nil": [
        {
            "role": "user",
            "content": "",
            "prompt": "",
        },
    ]
}


async def process_command(
    bot,
    command_name: str,
    ctx,
    prompt: str,
    temperature: float = 0.2,
    history: int = 0,
    max_tokens: int = 1000,
    author: str = None,
    is_regenerate: bool = False,
):
    global histories

    if author is None or len(author) == 0:
        author = str(ctx.author)

    valid_ctx = "respond" in dir(ctx)
    respond_fn = ctx.respond if valid_ctx else ctx.send
    if openai.api_key is None or len(openai.api_key) < 5:
        await respond_fn(
            "The value of OPENAI_API_KEY is invalid. Please run the command `/set_openai_api_key`"
        )
        return

    prompt = preprocess_prompt(prompt)

    if author not in histories:
        histories[author] = [
            {
                "role": "user",
                "content": prompt,
                "prompt": prompt,
            },
        ]
    else:
        if len(histories[author]) >= MAX_HISTORY:
            histories[author].pop(0)

    await respond_fn(
        "`/{}` prompt: ```{}```\n*temperature={}, history={}, max_tokens={}*".format(
            command_name,
            prompt,
            temperature,
            history,
            max_tokens,
        ),
        view=get_buttons(
            bot=bot,
            process_command=process_command,
            command_name=command_name,
            prompt=prompt,
            history=history,
            max_tokens=max_tokens,
        ),
    )

    message = await ctx.send("...")
    answer = ""
    trim_answer = ""
    try:
        start_time = time.time()
        options = {
            **OPENAI_COMPLETION_OPTIONS,
            "temperature": temperature,
            "max_tokens": max_tokens,
        }
        messages = [
            {
                "role": "system",
                "content": PROMPTS[command_name]["content"].replace(
                    "{CHAT_BOT_NAME}",
                    CHAT_BOT_NAME,
                ),
            },
        ]

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

        messages.append({"role": "user", "content": prompt})

        for r in openai.ChatCompletion.create(
            model=MODEL,
            messages=messages,
            stream=True,
            **options,
        ):
            if "content" in r.choices[0]["delta"]:
                answer += r.choices[0]["delta"]["content"]
                trim_answer = answer.strip()
                if trim_answer.count("```") % 2 == 1:
                    trim_answer += "```"
                if len(trim_answer) > 0 and time.time() - start_time >= 1.0:
                    start_time = time.time()
                    if is_message_limit(answer):
                        answers = break_answer(trim_answer)
                        await message.edit(content=answers[0])
                        message = await ctx.send(answers[1])
                        answer = answers[1]
                    else:
                        await message.edit(content=trim_answer + "\n\n...")
        if len(trim_answer) == 0:
            trim_answer = "No answer."
        else:
            if is_regenerate:
                for i in range(0, len(histories[author])):
                    if (
                        histories[author][i]["prompt"] == prompt
                        and histories[author][i]["role"] == "assistant"
                    ):
                        print("i: {}, {}", i, prompt)
                        histories[author][i] = {
                            "role": "assistant",
                            "content": trim_answer,
                            "prompt": prompt,
                        }
            else:
                histories[author].append(
                    {
                        "role": "assistant",
                        "content": trim_answer,
                        "prompt": prompt,
                    },
                )
        await message.edit(content=trim_answer)
    except Exception as e:
        trim_answer += "\n\n{}".format(e)
        await message.edit(content=trim_answer)
