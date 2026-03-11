import discord
from discord.ext import commands
from discord import app_commands
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from datetime import datetime, timedelta, timezone
import os
import logging
import random

from cogs.database import Database
from generator import generate_recap

logger = logging.getLogger("historian.recap")

RECAP_CHANNEL_ENV = "RECAP_CHANNEL_ID"


class RecapCog(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.db = Database()
        self._schedule_recap()

    def _schedule_recap(self):
        scheduler = AsyncIOScheduler()
        scheduler.add_job(
            self._post_weekly_recap,
            trigger="cron",
            day_of_week="sun",
            hour=18,
            minute=0,
        )
        scheduler.start()

    async def _post_weekly_recap(self):
        channel_id = os.getenv(RECAP_CHANNEL_ENV)
        if not channel_id:
            logger.warning("RECAP_CHANNEL_ID not set — skipping scheduled recap")
            return

        channel = self.bot.get_channel(int(channel_id))
        if not channel:
            return

        await self._send_recap(channel, days=7, label="weekly")

    async def _send_recap(self, channel: discord.TextChannel, days: int, label: str):
        guild_id = channel.guild.id
        end = datetime.now(timezone.utc)
        start = end - timedelta(days=days)

        messages = self.db.get_messages_in_range(guild_id, start, end)
        if not messages:
            await channel.send("📭 Not enough activity this period to generate a recap!")
            return

        sample_size = min(50, len(messages))
        messages_sample = random.sample(list(messages), sample_size)

        messages_as_dicts = []
        for message in messages_sample:
            messages_as_dicts.append(dict(message))

        top_users_as_dicts = []
        for user in self.db.get_top_users(guild_id, start, end):
            top_users_as_dicts.append(dict(user))

        top_reactions_as_dicts = []
        for reaction in self.db.get_top_reactions(guild_id, start, end):
            top_reactions_as_dicts.append(dict(reaction))

        active_channels_as_dicts = []
        for active_channel in self.db.get_active_channels(guild_id, start, end):
            active_channels_as_dicts.append(dict(active_channel))

        events_as_dicts = []
        for event in self.db.get_events_in_range(guild_id, start, end):
            events_as_dicts.append(dict(event))

        stats = {
            "total_messages": len(messages),
            "messages_sample": messages_as_dicts,
            "top_users": top_users_as_dicts,
            "top_reactions": top_reactions_as_dicts,
            "active_channels": active_channels_as_dicts,
            "events": events_as_dicts,
        }

        await channel.send("📜 *Generating your server recap... one moment!*")

        try:
            recap_text = generate_recap(stats, period_label=label)
            self.db.save_recap(guild_id, label, recap_text)
        except Exception as e:
            logger.error(f"Recap generation failed: {e}")
            await channel.send("❌ Failed to generate recap. Check your `GEMINI_API_KEY`.")
            return

        chunks = []
        for i in range(0, len(recap_text), 1900):
            chunks.append(recap_text[i:i + 1900])

        for chunk in chunks:
            await channel.send(chunk)

    @app_commands.command(name="recap", description="Generate a server recap for the past N days")
    @app_commands.describe(days="Number of days to recap (default: 7)")
    @app_commands.checks.has_permissions(manage_guild=True)
    async def recap_command(self, interaction: discord.Interaction, days: int = 7):
        await interaction.response.defer(thinking=True)
        await self._send_recap(interaction.channel, days=days, label=f"{days}-day")
        await interaction.followup.send("✅ Recap posted!", ephemeral=True)

    @app_commands.command(name="last-recap", description="Show the last generated recap")
    async def last_recap(self, interaction: discord.Interaction):
        row = self.db.get_last_recap(interaction.guild.id)
        if not row:
            await interaction.response.send_message("No recaps generated yet. Use `/recap` to create one!")
            return

        generated_timestamp = int(datetime.fromisoformat(row["generated_at"]).timestamp())
        summary_preview = row["summary"][:1800]

        await interaction.response.send_message(
            f"**Last recap** (generated <t:{generated_timestamp}:R>):\n\n{summary_preview}"
        )


async def setup(bot):
    await bot.add_cog(RecapCog(bot))