import discord
from discord import app_commands
from discord.ext import commands
from dotenv import load_dotenv

from constants import GUILD_ID, TOKEN

load_dotenv()


if not TOKEN or not GUILD_ID:
    raise ValueError("Create .env file, and ask your leads for the credentials!")


class Client(commands.Bot):
    async def setup_hook(self) -> None:
        extensions = ["commands.hybrid", "commands.prefix", "commands.slash"]

        for ext in extensions:
            await self.load_extension(ext)
            print(f"Loaded extension: {ext}")

    async def on_ready(self):
        print(f"Logged in as {self.user}!")

        try:
            self.tree.copy_global_to(guild=GUILD_ID)
            synced = await self.tree.sync(guild=GUILD_ID)
            print(f"Synced {len(synced)} commands to {GUILD_ID.id}")

        except Exception as e:
            print(f"Error syncing commands: {e}")

    async def on_message(self, message: discord.Message):
        if message.author == self.user:
            return

        await self.process_commands(message)


intents = discord.Intents.default()
intents.message_content = True

client = Client(command_prefix=commands.when_mentioned_or("lux "), intents=intents)


# NOTE: BUTTONS
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


# NOTE: DROP DOWN MENU
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
