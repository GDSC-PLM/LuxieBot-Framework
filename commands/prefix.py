import discord
from discord.ext import commands


class PrefixCommands(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot

    @commands.command(name="test prefix")
    async def placeholder(self, ctx: commands.Context):
        await ctx.send("test prefix")


async def setup(bot: commands.Bot):
    await bot.add_cog(PrefixCommands(bot))
