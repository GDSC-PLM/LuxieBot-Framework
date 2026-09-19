import os

import discord
from dotenv import load_dotenv

load_dotenv()


token = os.getenv("DISCORD_TOKEN")

if token is None:
    raise ValueError("Create .env file, and ask your leads for the discord token!")


class Client(discord.Client):
    async def on_ready(self):
        print(f"Logged on as {self.user}!")

    async def on_message(self, message):
        if message.author == self.user:
            return

        if message.content.startswith("lux"):
            await message.channel.send(
                f"Hello, {message.author}! I am Luxie. I am your best friend who's always there for you 24/7! Luxie is always right beside you, smiling in the dark, counting the pause between your each breath to see how much of you is left to collect!"
            )


intents = discord.Intents.default()
intents.message_content = True

client = Client(intents=intents)
client.run(token)
