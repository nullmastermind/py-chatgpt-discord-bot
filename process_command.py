import time

import openai

from config import OPENAI_COMPLETION_OPTIONS, CHAT_BOT_NAME, PROMPTS, MODEL, MAX_HISTORY
from utility import (
    is_message_limit,
    break_answer,
    preprocess_prompt,
    cut_string_to_json,
)
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
continue_histories = {
    "nil": [
        {
            "role": "user",
            "content": "",
            "prompt": "",
        },
    ]
}


def get_history_description(
    author: str,
    history: int,
    continue_conv: bool = False,
):
    messages = []

    if author in histories and history > 0 and len(histories[author]) > 0:
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
    else:
        if (
            author in continue_histories
            and continue_conv
            and len(continue_histories[author]) > 0
        ):
            for msg in continue_histories[author]:
                messages.append(
                    {
                        "role": msg["role"],
                        "content": msg["content"],
                    }
                )

    str_messages = []

    for msg in messages:
        role = "# {}".format(msg["role"])
        if msg["role"] == "user":
            role = "+ user"
        str_messages.append("{}: {}".format(role, cut_string_to_json(msg["content"])))

    return "{}".format("\n".join(str_messages)).strip()


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
    origin_data=None,
    continue_conv: bool = False,
):
    global histories, continue_histories

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
    history_message = {
        "role": "user",
        "content": prompt,
        "prompt": prompt,
    }
    append_to_history = False
    append_to_continue_history = False

    if not is_regenerate:
        if author not in continue_histories or not continue_conv:
            continue_histories[author] = [history_message]
        elif continue_conv:
            append_to_continue_history = True

    if author not in histories:
        histories[author] = [history_message]
    else:
        if not is_regenerate:
            append_to_history = True
        if len(histories[author]) >= MAX_HISTORY:
            histories[author].pop(0)

    if origin_data is not None:
        history_description = origin_data["history_description"]
        messages = origin_data["messages"]
    else:
        history_description = get_history_description(
            author=author,
            history=history,
            continue_conv=continue_conv,
        )
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
        else:
            if continue_conv and len(continue_histories[author]) > 0:
                for msg in continue_histories[author]:
                    messages.append(
                        {
                            "role": msg["role"],
                            "content": msg["content"],
                        }
                    )

        messages.append({"role": "user", "content": prompt})

    await respond_fn(
        ">>> /{}: temperature={}, history={}, max_tokens={}, continue_conv={} ```{}``` {}".format(
            command_name,
            temperature,
            history,
            max_tokens,
            continue_conv,
            prompt,
            "Timeline: ```diff\n{}\n+ user: {}```".format(
                history_description,
                cut_string_to_json(prompt),
            )
            if len(history_description) > 0
            else "",
        ),
        view=None,
    )

    message = await ctx.send("...")
    answer = ""
    trim_answer = ""
    full_answer = ""
    try:
        start_time = time.time()
        options = {
            **OPENAI_COMPLETION_OPTIONS,
            "temperature": temperature,
            "max_tokens": max_tokens,
        }

        if append_to_history:
            histories[author].append(history_message)
        if append_to_continue_history:
            continue_histories[author].append(history_message)

        for r in openai.ChatCompletion.create(
            model=MODEL,
            messages=messages,
            stream=True,
            **options,
        ):
            if "content" in r.choices[0]["delta"]:
                stream_message = r.choices[0]["delta"]["content"]
                answer += stream_message
                full_answer += stream_message
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
                        histories[author][i] = {
                            "role": "assistant",
                            "content": full_answer.strip(),
                            "prompt": prompt,
                        }
                for i in range(0, len(continue_histories[author])):
                    if (
                        continue_histories[author][i]["prompt"] == prompt
                        and continue_histories[author][i]["role"] == "assistant"
                    ):
                        continue_histories[author][i] = {
                            "role": "assistant",
                            "content": full_answer.strip(),
                            "prompt": prompt,
                        }
            else:
                histories[author].append(
                    {
                        "role": "assistant",
                        "content": full_answer.strip(),
                        "prompt": prompt,
                    },
                )
                continue_histories[author].append(
                    {
                        "role": "assistant",
                        "content": full_answer.strip(),
                        "prompt": prompt,
                    },
                )
        await message.edit(
            content=trim_answer,
            view=get_buttons(
                bot=bot,
                process_command=process_command,
                command_name=command_name,
                prompt=prompt,
                history=history,
                max_tokens=max_tokens,
                origin_data={
                    "history_description": history_description,
                    "messages": messages,
                    "temperature": temperature,
                },
            ),
        )
    except Exception as e:
        trim_answer += "\n\n{}".format(e)
        await message.edit(
            content=trim_answer,
            view=get_buttons(
                bot=bot,
                process_command=process_command,
                command_name=command_name,
                prompt=prompt,
                history=history,
                max_tokens=max_tokens,
                origin_data={
                    "history_description": history_description,
                    "messages": messages,
                    "temperature": temperature,
                },
            ),
        )
