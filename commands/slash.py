import discord
from discord import app_commands
from discord.ext import commands


class SlashCommands(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot

    @app_commands.command(name="slash", description="test slash")
    async def intro(self, interaction: discord.Interaction):
        await interaction.response.send_message("test slash")


async def setup(bot: commands.Bot):
    await bot.add_cog(SlashCommands(bot))
