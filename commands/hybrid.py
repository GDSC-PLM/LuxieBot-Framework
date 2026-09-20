import discord
from discord.ext import commands

from constants import LUXIE_STORY


class HybridCommands(commands.Cog):
    def __init__(self, bot: commands.Bot) -> None:
        self.bot = bot

    @commands.hybrid_command(
        name="introduction",
        aliases=["hello", "intro"],
        description="Get to know Luxie!",
    )
    async def introduction(self, ctx: commands.Context):
        await ctx.send(f"Hello, {ctx.author.mention}! I am Luxie. \n\n{LUXIE_STORY}")

    # NOTE: help command

    # @commands.hybrid_command(
    #     name="",
    #     description="Luxie got you covered!",
    # )
    # async def help(self, ctx: commands.Context):
    #     embed = discord.Embed(
    #         title="Command list",
    #         url="https://app.notion.com/library/favorites?spaceId=fb82cb6005844ce195739779dc9a4d98",
    #         description="I am your guiding light!",
    #         color=discord.Color.blue(),
    #     )
    #     embed.set_thumbnail(
    #         url="https://preview.redd.it/opinions-about-momo-as-a-character-v0-aqgnvh6l2sug1.jpg?width=640&crop=smart&auto=webp&s=128b2a8c516ecf74187257dd1aa793377725e01f"
    #     )
    #     embed.add_field(name="field test", value="i love momo ayase", inline=False)
    #     embed.add_field(name="test 2", value="i love momo ayase", inline=False)
    #     embed.add_field(name="test 3", value="i love momo ayase 2", inline=False)
    #     embed.set_footer(text="am a footer!")
    #     embed.set_author(
    #         name=ctx.author.name,
    #         url="https://app.notion.com/library/favorites?spaceId=fb82cb6005844ce195739779dc9a4d98",
    #         icon_url="https://preview.redd.it/opinions-about-momo-as-a-character-v0-aqgnvh6l2sug1.jpg?width=640&crop=smart&auto=webp&s=128b2a8c516ecf74187257dd1aa793377725e01f",
    #     )
    #     await ctx.send(embed=embed)


async def setup(bot: commands.Bot):
    await bot.add_cog(HybridCommands(bot))
