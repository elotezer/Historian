<div align="center">

# Historian

**Your Discord server has a story. Let AI tell it.**

Every Sunday, Historian reads your server's week and writes a real recap —<br/>
who carried the conversation, what everyone was talking about, and the moment that defined the week.

<br/>

[![Python](https://img.shields.io/badge/Python-3.11+-3776AB?style=for-the-badge&logo=python&logoColor=white)](https://www.python.org/)
[![discord.py](https://img.shields.io/badge/discord.py-2.4-5865F2?style=for-the-badge&logo=discord&logoColor=white)](https://discordpy.readthedocs.io)
[![Gemini](https://img.shields.io/badge/Gemini_1.5_Flash-Free-4285F4?style=for-the-badge&logo=google&logoColor=white)](https://aistudio.google.com/)
[![License](https://img.shields.io/badge/License-MIT-22c55e?style=for-the-badge)](LICENSE)

</div>

<br/>

---

## What it looks like

> **📰 This Week in Awesome Server**
>
> 1,203 messages. 9 channels. One server that really cannot stop talking about pineapple pizza.
> #general was unhinged as usual, #memes actually delivered, and somehow a 3-day debate started
> over a single image posted at 2 AM on Tuesday.
>
> **🏆 MVP of the Week — Alex**
> 218 messages. That's not a typo. Alex single-handedly kept #off-topic from going silent
> and wins the coveted title of Person Who Needs To Touch Grass.
>
> **💬 Hot Topics**
> The new game drop had everyone hyped. The sci-fi movie ranking thread got heated fast.
> And nobody can agree on whether the server should get a #pets channel.
>
> **😂 Moment of the Week**
> *"I have been awake for 34 hours and I think I can see sounds now"*
> — Jordan, Tuesday 3:47 AM, #general
>
> **📊 By the Numbers**
> 1,203 messages · 47 active members · 🔥 ×312 · 💀 ×208 · 👀 ×174
>
> **👋 Community Updates**
> Three new members joined this week. Welcome to the chaos.

---

## Why it's different

Most Discord bots count things. Historian *understands* things.

It reads a sample of your actual messages, figures out what people were genuinely talking about, picks the funniest or most memorable exchange, and writes something your community will actually want to read — not a spreadsheet dressed up as a recap.

And it costs nothing to run.

---

## Setup — under 5 minutes

**1. Clone and install**

```bash
git clone https://github.com/yourusername/historian.git
cd historian
pip install -r requirements.txt
```

**2. Create your `.env`**

```bash
cp .env.example .env
```

```env
DISCORD_TOKEN=your_discord_bot_token
GEMINI_API_KEY=your_gemini_api_key
GUILD_ID=your_server_id
RECAP_CHANNEL_ID=your_channel_id
```

**3. Run**

```bash
python src/core.py
```

Historian is now live. It will post its first recap next Sunday at 6 PM UTC.

---

## Docker

```bash
docker build -t historian .
docker run -d \
  --env-file .env \
  -v $(pwd)/data:/app/data \
  --name historian \
  historian
```

---

## Getting your API keys

**Discord token — free**
1. Go to [discord.com/developers/applications](https://discord.com/developers/applications)
2. New Application → Bot → Reset Token
3. Under *Privileged Gateway Intents*, enable `MESSAGE CONTENT INTENT` and `SERVER MEMBERS INTENT`
4. Invite with scopes `bot` + `applications.commands`, permissions: Read Messages, Send Messages, Read Message History, Embed Links

**Gemini API key — free, no credit card**
1. Go to [aistudio.google.com](https://aistudio.google.com)
2. Get API Key → Create API key

---

## Commands

| Command | Permission | Description |
|---|---|---|
| `/recap [days]` | Admin | Generate a recap right now for the past N days |
| `/last-recap` | Everyone | Show the most recent recap |
| `/stats [days]` | Everyone | Quick activity snapshot |
| `/historian-help` | Everyone | Usage guide |

---

## Project structure

```
historian/
├── src/
│   ├── core.py              — entry point
│   └── cogs/
│       ├── listener.py      — captures messages, reactions, member events
│       ├── recap.py         — scheduled and on-demand recap delivery
│       ├── commands.py      — slash commands
│       ├── generator.py     — builds the prompt and calls Gemini
│       └── database.py      — SQLite, all data stays on your machine
├── Dockerfile
├── requirements.txt
└── .env.example
```

---

## Roadmap

- [ ] Monthly recaps + year in review
- [ ] Per-channel breakdowns
- [ ] Web dashboard to browse recap history
- [ ] Export recap as a shareable image
- [ ] Multi-language recap support

PRs are welcome. If you add something cool, open a PR and it'll get merged.

---

## License

MIT — self-host it, fork it, do whatever you want with it.

<br/>

<div align="center">

Built with [discord.py](https://discordpy.readthedocs.io) and [Gemini](https://aistudio.google.com)

If your community enjoys it, a ⭐ goes a long way

</div>
