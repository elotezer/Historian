import sys
import os
from pathlib import Path

src_dir = Path(__file__).parent
cogs_dir = src_dir / "cogs"

sys.path.insert(0, str(src_dir))
sys.path.insert(0, str(cogs_dir))

import discord
from discord.ext import commands
from dotenv import load_dotenv
import logging
from apscheduler.schedulers.asyncio import AsyncIOScheduler

load_dotenv()

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("historian")

intents = discord.Intents.default()
intents.message_content = True
intents.members = True
intents.reactions = True

bot = commands.Bot(command_prefix=commands.when_mentioned, intents=intents)
scheduler = AsyncIOScheduler()


@bot.event
async def on_ready():
    logger.info(f"Historian is online as {bot.user}")

    guild_id = os.getenv("GUILD_ID")
    if not guild_id:
        raise ValueError("GUILD_ID not set in .env")

    guild = discord.Object(id=int(guild_id))

    await bot.load_extension("cogs.listener")
    await bot.load_extension("cogs.recap")
    await bot.load_extension("cogs.commands")

    bot.tree.copy_global_to(guild=guild)
    synced = await bot.tree.sync(guild=guild)
    logger.info(f"Synced {len(synced)} slash commands to guild {guild_id}")

    scheduler.start()


if __name__ == "__main__":
    token = os.getenv("DISCORD_TOKEN")
    if not token:
        raise ValueError("DISCORD_TOKEN not set in .env")
    bot.run(token)