import discord


def get_buttons(
    bot,
    process_command,
    command_name: str,
    prompt: str,
    history: int = 0,
    max_tokens: int = 1000,
):
    class RegenerateView(discord.ui.View):
        def __init__(self):
            super().__init__(timeout=3 * 60)

        async def on_timeout(self):
            for child in self.children:
                child.disabled = True
            await self.message.edit(view=self)

        async def handle(self, interaction, temperature: float):
            for child in self.children:
                child.disabled = True
            await self.message.edit(view=self)
            await interaction.response.send_message("**🔄 Regenerate 🔄**")
            await process_command(
                bot=bot,
                command_name=command_name,
                ctx=interaction.channel,
                prompt=prompt,
                temperature=temperature,
                history=history,
                max_tokens=max_tokens,
                author=str(interaction.user),
                is_regenerate=True,
            )

        @discord.ui.button(label="0.0 (Precise)", emoji="🔄")
        async def regenerate_button_callback_00(self, button, interaction):
            await self.handle(interaction=interaction, temperature=0.0)

        @discord.ui.button(label="0.2", emoji="🔄")
        async def regenerate_button_callback_02(self, button, interaction):
            await self.handle(interaction=interaction, temperature=0.2)

        @discord.ui.button(label="0.5 (Balanced)", emoji="🔄")
        async def regenerate_button_callback_05(self, button, interaction):
            await self.handle(interaction=interaction, temperature=0.5)

        @discord.ui.button(label="0.7", emoji="🔄")
        async def regenerate_button_callback_07(self, button, interaction):
            await self.handle(interaction=interaction, temperature=0.7)

        @discord.ui.button(label="1.0 (Creative)", emoji="🔄")
        async def regenerate_button_callback_10(self, button, interaction):
            await self.handle(interaction=interaction, temperature=1.0)

    return RegenerateView()
