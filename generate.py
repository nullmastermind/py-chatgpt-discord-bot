from config import PROMPTS

COMMAND_CODE_TEMPLATE = """
    @bot.slash_command(name="{COMMAND_NAME}")
    async def command_{COMMAND_NAME}(
        ctx,
        prompt: str,
        temperature: float = prompts["{COMMAND_NAME}"]["temperature"],
        history: int = 0,
        max_tokens: int = 1000,
        continue_conv: bool = False,
    ):
        await process_command(
            bot=bot,
            command_name="{COMMAND_NAME}",
            ctx=ctx,
            prompt=prompt,
            temperature=temperature,
            history=history,
            max_tokens=max_tokens,
            continue_conv=continue_conv,
        )
"""
FILE_TEMPLATE = """
# This file is automatically overwritten after running the app, please do not edit it as it would be meaningless.

def generated_commands(bot, prompts, process_command):
    {COMMAND_CODES}
"""


def generate_command_code(command_name: str):
    return COMMAND_CODE_TEMPLATE.replace("{COMMAND_NAME}", command_name)


def generate():
    codes = []
    for key in PROMPTS:
        codes.append(generate_command_code(key))
    content = FILE_TEMPLATE.replace("{COMMAND_CODES}", "\n".join(codes))
    with open("./generated_commands.py", "w") as f:
        f.write(content)


# for test
if __name__ == "__main__":
    generate()
