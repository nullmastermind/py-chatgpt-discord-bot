
# This file is automatically overwritten after running the app, please do not edit it as it would be meaningless.

def generated_commands(bot, prompts, process_command):
    
    @bot.slash_command(name="code")
    async def command_code(
        ctx,
        prompt: str,
        temperature: float = prompts["code"]["temperature"],
        history: int = 0,
        max_tokens: int = 1000,
        continue_conv: bool = False,
    ):
        await process_command(
            bot=bot,
            command_name="code",
            ctx=ctx,
            prompt=prompt,
            temperature=temperature,
            history=history,
            max_tokens=max_tokens,
            continue_conv=continue_conv,
        )


    @bot.slash_command(name="assistant")
    async def command_assistant(
        ctx,
        prompt: str,
        temperature: float = prompts["assistant"]["temperature"],
        history: int = 0,
        max_tokens: int = 1000,
        continue_conv: bool = False,
    ):
        await process_command(
            bot=bot,
            command_name="assistant",
            ctx=ctx,
            prompt=prompt,
            temperature=temperature,
            history=history,
            max_tokens=max_tokens,
            continue_conv=continue_conv,
        )


    @bot.slash_command(name="english_translator")
    async def command_english_translator(
        ctx,
        prompt: str,
        temperature: float = prompts["english_translator"]["temperature"],
        history: int = 0,
        max_tokens: int = 1000,
        continue_conv: bool = False,
    ):
        await process_command(
            bot=bot,
            command_name="english_translator",
            ctx=ctx,
            prompt=prompt,
            temperature=temperature,
            history=history,
            max_tokens=max_tokens,
            continue_conv=continue_conv,
        )


    @bot.slash_command(name="english_translator_technical")
    async def command_english_translator_technical(
        ctx,
        prompt: str,
        temperature: float = prompts["english_translator_technical"]["temperature"],
        history: int = 0,
        max_tokens: int = 1000,
        continue_conv: bool = False,
    ):
        await process_command(
            bot=bot,
            command_name="english_translator_technical",
            ctx=ctx,
            prompt=prompt,
            temperature=temperature,
            history=history,
            max_tokens=max_tokens,
            continue_conv=continue_conv,
        )


    @bot.slash_command(name="english_teacher")
    async def command_english_teacher(
        ctx,
        prompt: str,
        temperature: float = prompts["english_teacher"]["temperature"],
        history: int = 0,
        max_tokens: int = 1000,
        continue_conv: bool = False,
    ):
        await process_command(
            bot=bot,
            command_name="english_teacher",
            ctx=ctx,
            prompt=prompt,
            temperature=temperature,
            history=history,
            max_tokens=max_tokens,
            continue_conv=continue_conv,
        )


    @bot.slash_command(name="text_improver")
    async def command_text_improver(
        ctx,
        prompt: str,
        temperature: float = prompts["text_improver"]["temperature"],
        history: int = 0,
        max_tokens: int = 1000,
        continue_conv: bool = False,
    ):
        await process_command(
            bot=bot,
            command_name="text_improver",
            ctx=ctx,
            prompt=prompt,
            temperature=temperature,
            history=history,
            max_tokens=max_tokens,
            continue_conv=continue_conv,
        )

