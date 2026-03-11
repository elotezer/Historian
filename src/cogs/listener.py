import discord
from discord.ext import commands
from storage.database import Database
import logging

logger = logging.getLogger("historian.listener")


class Listener(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.db = Database()

    @commands.Cog.listener()
    async def on_message(self, message: discord.Message):
        if message.author.bot:
            return

        self.db.log_message(
            guild_id=message.guild.id if message.guild else None,
            channel_id=message.channel.id,
            user_id=message.author.id,
            username=str(message.author.display_name),
            content=message.content,
            timestamp=message.created_at,
            has_attachment=len(message.attachments) > 0,
            has_embed=len(message.embeds) > 0,
        )

    @commands.Cog.listener()
    async def on_reaction_add(self, reaction: discord.Reaction, user: discord.User):
        if user.bot:
            return

        self.db.log_reaction(
            guild_id=reaction.message.guild.id if reaction.message.guild else None,
            message_id=reaction.message.id,
            user_id=user.id,
            emoji=str(reaction.emoji),
            timestamp=reaction.message.created_at,
        )

    @commands.Cog.listener()
    async def on_member_join(self, member: discord.Member):
        self.db.log_event(
            guild_id=member.guild.id,
            event_type="member_join",
            data={"user_id": member.id, "username": str(member)},
        )

    @commands.Cog.listener()
    async def on_member_remove(self, member: discord.Member):
        self.db.log_event(
            guild_id=member.guild.id,
            event_type="member_leave",
            data={"user_id": member.id, "username": str(member)},
        )


async def setup(bot):
    await bot.add_cog(Listener(bot))