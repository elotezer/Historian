import discord
from discord.ext import commands
from discord import app_commands
from database import Database
from datetime import datetime, timedelta, timezone
import logging

logger = logging.getLogger("historian.commands")

ACCENT = 0x5865F2
SUCCESS = 0x57F287
WARNING = 0xFEE75C
ERROR = 0xED4245


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
            title="Server Activity",
            description=f"Overview for the past **{days} days**",
            color=ACCENT,
            timestamp=datetime.now(timezone.utc),
        )

        embed.add_field(
            name="💬  Messages",
            value=f"### {len(messages):,}",
            inline=True,
        )

        embed.add_field(
            name="👥  Active Members",
            value=f"### {len(top_users)}",
            inline=True,
        )

        embed.add_field(name="\u200b", value="\u200b", inline=True)

        if top_users:
            user_lines = []
            medals = ["🥇", "🥈", "🥉"]
            for i, user in enumerate(top_users):
                medal = medals[i] if i < 3 else f"`{i + 1}.`"
                line = f"{medal} **{user['username']}** — {user['msg_count']:,} msgs"
                user_lines.append(line)
            embed.add_field(
                name="🏆  Top Chatters",
                value="\n".join(user_lines),
                inline=True,
            )

        if top_reactions:
            reaction_parts = []
            for reaction in top_reactions:
                reaction_parts.append(f"{reaction['emoji']} `{reaction['count']}`")
            embed.add_field(
                name="🔥  Top Reactions",
                value="  ".join(reaction_parts),
                inline=True,
            )

        embed.set_author(
            name=interaction.guild.name,
            icon_url=interaction.guild.icon.url if interaction.guild.icon else None,
        )
        embed.set_footer(text="Historian", icon_url=interaction.client.user.display_avatar.url)

        await interaction.response.send_message(embed=embed)

    @app_commands.command(name="historian-help", description="How to use Historian")
    async def help_cmd(self, interaction: discord.Interaction):
        embed = discord.Embed(
            title="Historian",
            description="I silently watch your server and every Sunday drop a beautiful AI-written recap of everything that happened.",
            color=ACCENT,
        )

        embed.add_field(
            name="📋  Commands",
            value=(
                "> `/recap [days]` — Generate a recap *(admin only)*\n"
                "> `/last-recap` — Show the most recent recap\n"
                "> `/stats [days]` — Activity stats\n"
                "> `/historian-help` — This message"
            ),
            inline=False,
        )

        embed.add_field(
            name="🕕  Auto Recaps",
            value="> Every **Sunday at 6 PM UTC** a recap is posted automatically to your configured channel.",
            inline=False,
        )

        embed.add_field(
            name="⚙️  Setup",
            value="> Set `RECAP_CHANNEL_ID` in your `.env` to enable automatic weekly recaps.",
            inline=False,
        )

        embed.set_thumbnail(url=interaction.client.user.display_avatar.url)
        embed.set_footer(text="Powered by Gemini", icon_url=interaction.client.user.display_avatar.url)

        await interaction.response.send_message(embed=embed)


async def setup(bot):
    await bot.add_cog(CommandsCog(bot))