import discord
from discord.ext import commands
from discord import app_commands
from cogs.database import Database
from datetime import datetime, timedelta, timezone
import logging

logger = logging.getLogger("historian.commands")


class CommandsCog(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.db = Database()

    @app_commands.command(name="stats", description="Show activity stats for the past N days")
    @app_commands.describe(days="Number of days (default: 7)")
    async def stats(self, interaction: discord.Interaction, days: int = 7):
        guild_id = interaction.guild.id
        end = datetime.now(timezone.utc)
        start = end - timedelta(days=days)

        messages = self.db.get_messages_in_range(guild_id, start, end)
        top_users = self.db.get_top_users(guild_id, start, end)
        top_reactions = self.db.get_top_reactions(guild_id, start, end)

        embed = discord.Embed(
            title=f"📊 Server Stats — Last {days} Days",
            color=discord.Color.blurple(),
            timestamp=datetime.now(timezone.utc),
        )

        embed.add_field(name="Total Messages", value=str(len(messages)), inline=True)

        if top_users:
            user_lines = []
            for i, user in enumerate(top_users):
                line = f"`{i + 1}.` **{user['username']}** — {user['msg_count']} msgs"
                user_lines.append(line)
            users_str = "\n".join(user_lines)
            embed.add_field(name="🏆 Top Chatters", value=users_str, inline=False)

        if top_reactions:
            reaction_parts = []
            for reaction in top_reactions:
                reaction_parts.append(f"{reaction['emoji']} ×{reaction['count']}")
            rxn_str = "  ".join(reaction_parts)
            embed.add_field(name="🔥 Top Reactions", value=rxn_str, inline=False)

        embed.set_footer(text="Historian • powered by Claude AI")
        await interaction.response.send_message(embed=embed)

    @app_commands.command(name="historian-help", description="How to use Historian")
    async def help_cmd(self, interaction: discord.Interaction):
        embed = discord.Embed(
            title="📜 Historian — Help",
            description="I silently watch your server and produce beautiful recaps of everything that happens.",
            color=discord.Color.gold(),
        )
        embed.add_field(
            name="Commands",
            value=(
                "`/recap [days]` — Generate a recap (admin only)\n"
                "`/last-recap` — Show the most recent recap\n"
                "`/stats [days]` — Quick activity stats\n"
                "`/historian-help` — This message"
            ),
            inline=False,
        )
        embed.add_field(
            name="Automatic Recaps",
            value="I post a weekly recap every Sunday at 6 PM UTC in your configured channel.",
            inline=False,
        )
        embed.set_footer(text="Set RECAP_CHANNEL_ID in your .env to configure the auto-recap channel.")
        await interaction.response.send_message(embed=embed)


async def setup(bot):
    await bot.add_cog(CommandsCog(bot))