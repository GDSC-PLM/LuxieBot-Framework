import os

import discord
from discord import app_commands
from discord.ext import commands
from dotenv import load_dotenv

load_dotenv()


TOKEN = os.environ["DISCORD_TOKEN"]
GUILD_ID = discord.Object(os.environ["GUILD_ID"])

if not TOKEN or not GUILD_ID:
    raise ValueError("Create .env file, and ask your leads for the credentials!")


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


@client.tree.command(
    name="introduction", description="Get to know Luxie!", guild=GUILD_ID
)
async def introduction(interaction: discord.Interaction):
    await interaction.response.send_message(
        f"Hello, {interaction.user.mention}! I am Luxie. Long before Luxie arrived at GDG, Luxie was a Starlight Fragment floating through the digital cosmos, which is a tiny comet powered by curiosity, lighted spirit, and the collective energy of student developers around the world. When Haribot (the bot guardian of PLM's GDG community) was soaring through the digital skyline, looking for a way to guide aspiring student developers, a bright spark flashed across the night sky. Haribot flew up to meet it, and the two connected instantly. Haribot provided strength, wisdom, and local heritage, while Luxie brought sparkling innovation, speed, and light to illuminate the beauty of networks."
    )


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


class View(discord.ui.View):
    @discord.ui.button(
        label="Click me daddy", style=discord.ButtonStyle.red, emoji="🥳"
    )
    async def button_callback0(self, button, interaction):
        await button.response.send_message("You clicked me mommy")

    @discord.ui.button(
        label="second button", style=discord.ButtonStyle.blurple, emoji="🥳"
    )
    async def button_callback1(self, button, interaction):
        await button.response.send_message("Im the second child")

    @discord.ui.button(
        label="Click me daddy", style=discord.ButtonStyle.green, emoji="🥳"
    )
    async def button_callback2(self, button, interaction):
        await button.response.send_message("Im the third child")


@client.tree.command(name="button", description="Displaying a button", guild=GUILD_ID)
async def myButton(interaction: discord.Interaction):
    await interaction.response.send_message(view=View())


class Menu(discord.ui.Select):
    def __init__(self):
        options = [
            discord.SelectOption(
                label="option1",
                description="tis a menu dropdown option1",
                emoji="🥳",
            ),
            discord.SelectOption(
                label="option2",
                description="tis a menu dropdown option2",
                emoji="🥳",
            ),
            discord.SelectOption(
                label="option3",
                description="tis a menu dropdown option3",
                emoji="🥳",
            ),
        ]

        super().__init__(
            placeholder="Choose an option daddy:",
            min_values=1,
            max_values=1,
            options=options,
        )

    # NOTE: change function for each option
    async def callback(self, interaction: discord.Interaction):
        if self.values[0] == "option1":
            await interaction.response.send_message("you picked option 1 my bingus")

        if self.values[0] == "option2":
            await interaction.response.send_message("you picked option 2 my bingus")

        if self.values[0] == "option3":
            await interaction.response.send_message("you picked option 3 my bingus")


class MenuView(discord.ui.View):
    def __init__(self):
        super().__init__()
        self.add_item(Menu())


@client.tree.command(name="menu", description="tis a dropdown menu", guild=GUILD_ID)
async def myMenu(interaction: discord.Interaction):
    await interaction.response.send_message(view=MenuView())


client.run(TOKEN)
