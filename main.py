import os
from re import A

import discord
from discord import app_commands
from discord.ext import commands
from dotenv import load_dotenv

load_dotenv()


token = os.getenv("DISCORD_TOKEN")

GUILD_ID = discord.Object(id=1534840767338516642)

if token is None:
    raise ValueError("Create .env file, and ask your leads for the discord token!")


class Client(commands.Bot):
    async def on_ready(self):
        print(f"Logged in as {self.user}!")

        try:
            synced = await self.tree.sync(guild=GUILD_ID)
            print(f"Synced {len(synced)} commands to {GUILD_ID.id}")

        except Exception as e:
            print(f"Error syncing commands: {e}")

    async def on_message(self, message):
        if message.author == self.user:
            return

        if message.content.startswith("lux"):
            await message.channel.send(
                f"Hello, {message.author}! I am Luxie. I am your best friend who's always there for you 24/7! Luxie is always right beside you, smiling in the dark, counting the pause between your each breath to see how much of you is left to collect!"
            )


intents = discord.Intents.default()
intents.message_content = True

client = Client(command_prefix="!", intents=intents)


@client.tree.command(name="hello", description="Say hello", guild=GUILD_ID)
async def say_hello(interaction: discord.Interaction):
    await interaction.response.send_message("I am Luxie, hello!")


@client.tree.command(name="printer", description="I am gaya gaya", guild=GUILD_ID)
async def printer(interaction: discord.Interaction, printer: str):
    await interaction.response.send_message(printer)


@client.tree.command(name="embed", description="Embedable tings", guild=GUILD_ID)
async def embed(interaction: discord.Interaction):
    embed = discord.Embed(
        title="Lux",
        url="https://app.notion.com/library/favorites?spaceId=fb82cb6005844ce195739779dc9a4d98",
        description="I am your guiding light!",
        color=discord.Color.blue(),
    )
    embed.set_thumbnail(
        url="https://preview.redd.it/opinions-about-momo-as-a-character-v0-aqgnvh6l2sug1.jpg?width=640&crop=smart&auto=webp&s=128b2a8c516ecf74187257dd1aa793377725e01f"
    )
    embed.add_field(name="field test", value="i love momo ayase", inline=False)
    embed.add_field(name="test 2", value="i love momo ayase", inline=False)
    embed.add_field(name="test 3", value="i love momo ayase 2", inline=False)
    embed.set_footer(text="am a footer!")
    embed.set_author(
        name=interaction.user.name,
        url="https://app.notion.com/library/favorites?spaceId=fb82cb6005844ce195739779dc9a4d98",
        icon_url="https://preview.redd.it/opinions-about-momo-as-a-character-v0-aqgnvh6l2sug1.jpg?width=640&crop=smart&auto=webp&s=128b2a8c516ecf74187257dd1aa793377725e01f",
    )
    await interaction.response.send_message(embed=embed)


client.run(token)
