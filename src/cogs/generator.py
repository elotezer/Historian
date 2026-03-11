import google.genai as genai
import os
import logging

logger = logging.getLogger("historian.ai")

client = genai.Client(api_key=os.getenv("GEMINI_API_KEY"))


def build_prompt(stats: dict, period_label: str) -> str:
    messages_sample = stats.get("messages_sample", [])
    top_users = stats.get("top_users", [])
    top_reactions = stats.get("top_reactions", [])
    active_channels = stats.get("active_channels", [])
    events = stats.get("events", [])
    total_messages = stats.get("total_messages", 0)

    sample_lines = []
    for message in messages_sample[:40]:
        if message["content"].strip():
            line = f"- [{message['username']}]: {message['content'][:120]}"
            sample_lines.append(line)
    sample_text = "\n".join(sample_lines)

    user_lines = []
    for i, user in enumerate(top_users):
        line = f"  {i + 1}. {user['username']} ({user['msg_count']} messages)"
        user_lines.append(line)
    users_text = "\n".join(user_lines)

    reaction_parts = []
    for reaction in top_reactions:
        reaction_parts.append(f"{reaction['emoji']} x{reaction['count']}")
    reactions_text = ", ".join(reaction_parts)

    channel_lines = []
    for channel in active_channels:
        line = f"  #{channel['channel_id']} — {channel['msg_count']} messages"
        channel_lines.append(line)
    channels_text = "\n".join(channel_lines)

    event_lines = []
    for event in events[:10]:
        line = f"  - {event['event_type']}: {event['data']}"
        event_lines.append(line)
    events_text = "\n".join(event_lines) if event_lines else "  None"

    return f"""You are the Historian — a witty, warm chronicler of a Discord community.

Write a {period_label} recap newsletter for this server. It should feel like a fun community digest, not a dry report.

== SERVER STATS ==
Total messages: {total_messages}

Top chatters:
{users_text}

Most used reactions: {reactions_text}

Most active channels:
{channels_text}

Notable events:
{events_text}

== MESSAGE SAMPLE ==
{sample_text}

== INSTRUCTIONS ==
Write a recap with these sections using Discord markdown:
1. **📰 This Week in [Server]** — A punchy 2-3 sentence opening that captures the vibe/mood of the period
2. **🏆 MVP of the Week** — Highlight the top chatter with a fun, specific observation
3. **💬 Hot Topics** — 2-3 themes or discussions you noticed in the messages
4. **😂 Moment of the Week** — Pick one interesting/funny/notable message or exchange and highlight it (quote it if possible)
5. **📊 By the Numbers** — Fun stats summary (total messages, top emojis, etc.)
6. **👋 Community Updates** — Member joins/leaves if any
7. **🔮 Looking Ahead** — A short playful sign-off

Keep the tone fun, celebratory, and community-focused. Use Discord markdown. Avoid anything negative or mean-spirited.
"""


def generate_recap(stats: dict, period_label: str = "weekly") -> str:
    prompt = build_prompt(stats, period_label)
    response = client.models.generate_content(
        model="gemini-1.5-flash",
        contents=prompt,
    )
    return response.text