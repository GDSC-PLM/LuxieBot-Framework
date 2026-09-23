import os
from dotenv import load_dotenv

import discord

# NOTE: EDITABLE CONFIGURATIONS

load_dotenv()

# discord things
TOKEN = os.environ["DISCORD_TOKEN"]
GUILD_ID = discord.Object(os.environ["GUILD_ID"])

# internal data
LUXIE_STORY = "Long before Luxie arrived at GDG, Luxie was a Starlight Fragment floating through the digital cosmos, which is a tiny comet powered by curiosity, lighted spirit, and the collective energy of student developers around the world. \n\nWhen Haribot (the bot guardian of PLM's GDG community) was soaring through the digital skyline, looking for a way to guide aspiring student developers, a bright spark flashed across the night sky. \n\nHaribot flew up to meet it, and the two connected instantly. Haribot provided strength, wisdom, and local heritage, while Luxie brought sparkling innovation, speed, and light to illuminate the beauty of networks."
