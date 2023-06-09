import asyncio
import dataclasses
import math
import time

import openai

from config import (
    OPENAI_COMPLETION_OPTIONS,
    CHAT_BOT_NAME,
    PROMPTS,
    MODEL,
    MAX_HISTORY,
    TIMEOUT,
)
from utility import (
    is_message_limit,
    break_answer,
    preprocess_prompt,
    cut_string_to_json,
    replace_with_characters_map,
)


@dataclasses.dataclass
class LastCommand:
    command: str = dataclasses.field(default="")
    temperature: float = dataclasses.field(default=0.0)
    max_tokens: int = dataclasses.field(default=1000)


@dataclasses.dataclass
class HistoryItem:
    role: str = dataclasses.field(default="user")
    content: str = dataclasses.field(default="")
    prompt: str = dataclasses.field(default="")
    command: str = dataclasses.field(default="")
    continue_conv: bool = dataclasses.field(default=False)
    temperature: float = dataclasses.field(default=0.2)


histories = {"nil": [HistoryItem(role="user")]}
continue_histories = {"nil": [HistoryItem(role="user")]}
last_command: LastCommand = None


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
                        "role": histories[author][index].role,
                        "content": histories[author][index].content,
                    }
                )
                if histories[author][index].role == "user":
                    num_pass_his -= 1
        for msg in history_messages[::-1]:
            messages.append(msg)
    else:
        if (
            author in continue_histories
            and continue_conv
            and len(continue_histories[author]) > 0
        ):
            continue_messages = []
            for j in range(len(continue_histories[author]) - 1, -1, -1):
                msg = continue_histories[author][j]
                continue_messages.insert(0, msg)
                if msg.role == "user" and not msg.continue_conv:
                    break
            for msg in continue_messages:
                messages.append(
                    {
                        "role": msg.role,
                        "content": msg.content,
                    }
                )

    str_messages = []

    for msg in messages:
        role = "# {}".format(msg["role"])
        if msg["role"] == "user":
            role = "+ user"
        str_messages.append("{}: {}".format(role, cut_string_to_json(msg["content"])))

    return "{}".format("\n".join(str_messages)).strip()


def get_regenerate_data(author: str):
    global histories

    if author not in histories:
        return None

    while histories[author] and histories[author][-1].role != "user":
        histories[author].pop()

    if author in continue_histories:
        while (
            continue_histories[author] and continue_histories[author][-1].role != "user"
        ):
            continue_histories[author].pop()
        if continue_histories[author]:
            continue_histories[author].pop()

    if histories[author]:
        return histories[author].pop()

    return None


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
    global histories, continue_histories, last_command

    if author is None or len(author) == 0:
        author = str(ctx.author)

    valid_ctx = "respond" in dir(ctx)
    respond_fn = None
    send_fn = None
    if not valid_ctx:
        if "channel" in dir(ctx) and "send" in dir(ctx.channel):
            respond_fn = ctx.channel.send
            send_fn = ctx.channel.send
    if respond_fn is None:
        respond_fn = ctx.respond if valid_ctx else ctx.send
        send_fn = ctx.send
    if openai.api_key is None or len(openai.api_key) < 5:
        await respond_fn(
            "The value of OPENAI_API_KEY is invalid. Please run the command `/set_openai_api_key`"
        )
        return

    last_command = LastCommand(
        command=command_name,
        max_tokens=max_tokens,
        temperature=temperature,
    )
    prompt = preprocess_prompt(prompt)
    history_message = HistoryItem(
        role="user",
        content=prompt,
        prompt=prompt,
        command=command_name,
        continue_conv=continue_conv,
        temperature=temperature,
    )
    append_to_history = False
    append_to_continue_history = False

    if author not in continue_histories:
        continue_histories[author] = [history_message]
    else:
        if not is_regenerate:
            append_to_continue_history = True
        if len(continue_histories[author]) >= MAX_HISTORY:
            continue_histories[author].pop(0)

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
                            "role": histories[author][index].role,
                            "content": histories[author][index].content,
                        }
                    )
                    if histories[author][index].role == "user":
                        num_pass_his -= 1
            for msg in history_messages[::-1]:
                messages.append(msg)
        else:
            if continue_conv and len(continue_histories[author]) > 0:
                continue_messages = []
                for j in range(len(continue_histories[author]) - 1, -1, -1):
                    msg = continue_histories[author][j]
                    continue_messages.insert(0, msg)
                    if msg.role == "user" and not msg.continue_conv:
                        break
                for msg in continue_messages:
                    messages.append(
                        {
                            "role": msg.role,
                            "content": msg.content,
                        }
                    )

        messages.append({"role": "user", "content": prompt})
        if "suffix" in PROMPTS[command_name]:
            messages.append(
                {"role": "user", "content": PROMPTS[command_name]["suffix"]}
            )

    await respond_fn(
        ">>> /{}: temperature={}, history={}, max_tokens={}, continue_conv={} ```{}``` {}".format(
            command_name,
            temperature,
            history,
            max_tokens,
            continue_conv,
            prompt.replace("`", '"'),
            "Timeline: ```diff\n{}\n+ user: {}```".format(
                history_description,
                cut_string_to_json(prompt),
            )
            if len(history_description) > 0
            else "",
        )
    )

    if append_to_history:
        histories[author].append(history_message)
    if append_to_continue_history:
        continue_histories[author].append(history_message)

    history_index = len(histories[author])
    continue_history_index = len(continue_histories[author])

    message = await send_fn(content="**{}** is thinking...".format(CHAT_BOT_NAME))
    full_answer = ""
    start_generate_time = time.time()
    is_typing_ready = False
    start_thinking = time.time()

    async def overtime():
        start_wait = time.time()
        current_message = "."
        while "Waiting":
            if time.time() - start_wait >= TIMEOUT:
                break
            if is_typing_ready:
                break
            await message.edit(
                content="**{}** is thinking{} ({}s)".format(
                    CHAT_BOT_NAME,
                    current_message,
                    math.ceil(time.time() - start_thinking),
                )
            )
            if current_message == ".":
                current_message = ".."
            elif current_message == "..":
                current_message = "..."
            elif current_message == "...":
                current_message = "."
            await asyncio.sleep(0.1)
        return None

    while len(full_answer) == 0:
        await ctx.channel.trigger_typing()

        answer = ""
        trim_answer = ""
        chunk_answer = ""

        try:
            start_time = time.time()
            options = {
                **OPENAI_COMPLETION_OPTIONS,
                "temperature": temperature,
                "max_tokens": max_tokens,
            }
            done, pending = await asyncio.wait(
                [
                    asyncio.create_task(overtime()),
                    asyncio.create_task(
                        openai.ChatCompletion.acreate(
                            model=MODEL,
                            messages=messages,
                            stream=True,
                            **options,
                        )
                    ),
                ],
                return_when=asyncio.FIRST_COMPLETED,
            )
            stream = done.pop().result()
            if stream is None:
                # print("retry")
                continue

            is_typing_ready = True

            async for r in stream:
                if "content" in r.choices[0]["delta"]:
                    stream_message = r.choices[0]["delta"]["content"]
                    answer += stream_message
                    chunk_answer += stream_message
                    full_answer += stream_message
                    trim_answer = answer
                    if trim_answer.count("```") % 2 == 1:
                        trim_answer += "```"
                    if len(chunk_answer) >= 100 or (
                        len(chunk_answer.strip()) > 0
                        and time.time() - start_time >= 1.0
                    ):
                        chunk_answer = ""
                        start_time = time.time()
                        if is_message_limit(answer):
                            answers = break_answer(trim_answer)
                            message = await send_message(
                                send_fn=send_fn,
                                message=message,
                                content=answers[0],
                            )
                            message = await send_fn(answers[1])
                            answer = answers[1]
                        else:
                            message = await send_message(
                                send_fn=send_fn,
                                message=message,
                                content=trim_answer,
                            )
                        await ctx.channel.trigger_typing()
            if len(trim_answer) == 0:
                trim_answer = "No answer."
            else:
                if is_regenerate:
                    for i in range(0, len(histories[author])):
                        if (
                            histories[author][i].prompt == prompt
                            and histories[author][i].role == "assistant"
                        ):
                            histories[author][i].content = full_answer.strip()
                            histories[author][i].prompt = prompt.strip()
                    for i in range(0, len(continue_histories[author])):
                        if (
                            continue_histories[author][i].prompt == prompt
                            and continue_histories[author][i].role == "assistant"
                        ):
                            continue_histories[author][i].content = full_answer.strip()
                            continue_histories[author][i].prompt = prompt.strip()
                else:
                    new_history_item = HistoryItem(
                        role="assistant",
                        content=full_answer.strip(),
                        prompt=prompt,
                        command=command_name,
                        continue_conv=continue_conv,
                        temperature=temperature,
                    )
                    histories[author].insert(history_index, new_history_item)
                    continue_histories[author].insert(
                        continue_history_index,
                        new_history_item,
                    )
            message = await send_message(
                send_fn=send_fn, message=message, content=trim_answer
            )
        except Exception as e:
            error_info = "```{}```".format(e)
            trim_answer += error_info
            full_answer += error_info
            message = await send_message(
                send_fn=send_fn, message=message, content=trim_answer
            )

    end_message = await send_fn(
        replace_with_characters_map(
            "{:.2f}s".format(time.time() - start_generate_time)
        ),
    )
    await asyncio.sleep(1)
    await end_message.delete()


async def send_message(send_fn, message, content, copyable: bool = False):
    if copyable:
        content = "```{}```".format(content)
    if message is None:
        message = await send_fn(content=content)
    else:
        await message.edit(content=content)
    return message
