import discord
from discord.ext import commands
import os
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
    await bot.load_extension("src.cogs.listener")
    await bot.load_extension("src.cogs.recap")
    await bot.load_extension("src.cogs.commands")
    scheduler.start()
    synced = await bot.tree.sync()
    logger.info(f"Synced {len(synced)} slash commands")


if __name__ == "__main__":
    token = os.getenv("DISCORD_TOKEN")
    if not token:
        raise ValueError("DISCORD_TOKEN not set in .env")
    bot.run(token)