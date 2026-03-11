import sqlite3
import json
from datetime import datetime
from pathlib import Path
import logging

logger = logging.getLogger("historian.db")

DB_PATH = Path("data/historian.db")


class Database:
    def __init__(self):
        DB_PATH.parent.mkdir(exist_ok=True)
        self.conn = sqlite3.connect(DB_PATH, check_same_thread=False)
        self.conn.row_factory = sqlite3.Row
        self._init_schema()

    def _init_schema(self):
        self.conn.executescript("""
            CREATE TABLE IF NOT EXISTS messages (
                id          INTEGER PRIMARY KEY AUTOINCREMENT,
                guild_id    INTEGER,
                channel_id  INTEGER,
                user_id     INTEGER,
                username    TEXT,
                content     TEXT,
                timestamp   TEXT,
                has_attachment INTEGER DEFAULT 0,
                has_embed      INTEGER DEFAULT 0
            );

            CREATE TABLE IF NOT EXISTS reactions (
                id          INTEGER PRIMARY KEY AUTOINCREMENT,
                guild_id    INTEGER,
                message_id  INTEGER,
                user_id     INTEGER,
                emoji       TEXT,
                timestamp   TEXT
            );

            CREATE TABLE IF NOT EXISTS events (
                id          INTEGER PRIMARY KEY AUTOINCREMENT,
                guild_id    INTEGER,
                event_type  TEXT,
                data        TEXT,
                timestamp   TEXT DEFAULT (datetime('now'))
            );

            CREATE TABLE IF NOT EXISTS recaps (
                id          INTEGER PRIMARY KEY AUTOINCREMENT,
                guild_id    INTEGER,
                period      TEXT,
                generated_at TEXT,
                summary     TEXT
            );

            CREATE INDEX IF NOT EXISTS idx_messages_guild_ts
                ON messages(guild_id, timestamp);
            CREATE INDEX IF NOT EXISTS idx_reactions_guild
                ON reactions(guild_id, timestamp);
        """)
        self.conn.commit()

    def log_message(self, guild_id, channel_id, user_id, username,
                    content, timestamp, has_attachment, has_embed):
        self.conn.execute(
            """INSERT INTO messages
               (guild_id, channel_id, user_id, username, content, timestamp, has_attachment, has_embed)
               VALUES (?,?,?,?,?,?,?,?)""",
            (guild_id, channel_id, user_id, username, content,
             timestamp.isoformat(), int(has_attachment), int(has_embed)),
        )
        self.conn.commit()

    def log_reaction(self, guild_id, message_id, user_id, emoji, timestamp):
        self.conn.execute(
            "INSERT INTO reactions (guild_id, message_id, user_id, emoji, timestamp) VALUES (?,?,?,?,?)",
            (guild_id, message_id, user_id, emoji, timestamp.isoformat()),
        )
        self.conn.commit()

    def log_event(self, guild_id, event_type, data):
        self.conn.execute(
            "INSERT INTO events (guild_id, event_type, data) VALUES (?,?,?)",
            (guild_id, event_type, json.dumps(data)),
        )
        self.conn.commit()

    def get_messages_in_range(self, guild_id, start: datetime, end: datetime):
        cur = self.conn.execute(
            """SELECT * FROM messages
               WHERE guild_id=? AND timestamp BETWEEN ? AND ?
               ORDER BY timestamp ASC""",
            (guild_id, start.isoformat(), end.isoformat()),
        )
        return cur.fetchall()

    def get_top_users(self, guild_id, start: datetime, end: datetime, limit=5):
        cur = self.conn.execute(
            """SELECT username, user_id, COUNT(*) as msg_count
               FROM messages
               WHERE guild_id=? AND timestamp BETWEEN ? AND ?
               GROUP BY user_id
               ORDER BY msg_count DESC LIMIT ?""",
            (guild_id, start.isoformat(), end.isoformat(), limit),
        )
        return cur.fetchall()

    def get_top_reactions(self, guild_id, start: datetime, end: datetime, limit=5):
        cur = self.conn.execute(
            """SELECT emoji, COUNT(*) as count
               FROM reactions
               WHERE guild_id=? AND timestamp BETWEEN ? AND ?
               GROUP BY emoji
               ORDER BY count DESC LIMIT ?""",
            (guild_id, start.isoformat(), end.isoformat(), limit),
        )
        return cur.fetchall()

    def get_events_in_range(self, guild_id, start: datetime, end: datetime):
        cur = self.conn.execute(
            """SELECT * FROM events
               WHERE guild_id=? AND timestamp BETWEEN ? AND ?""",
            (guild_id, start.isoformat(), end.isoformat()),
        )
        return cur.fetchall()

    def get_active_channels(self, guild_id, start: datetime, end: datetime, limit=5):
        cur = self.conn.execute(
            """SELECT channel_id, COUNT(*) as msg_count
               FROM messages
               WHERE guild_id=? AND timestamp BETWEEN ? AND ?
               GROUP BY channel_id ORDER BY msg_count DESC LIMIT ?""",
            (guild_id, start.isoformat(), end.isoformat(), limit),
        )
        return cur.fetchall()

    def save_recap(self, guild_id, period, summary):
        self.conn.execute(
            "INSERT INTO recaps (guild_id, period, generated_at, summary) VALUES (?,?,?,?)",
            (guild_id, period, datetime.utcnow().isoformat(), summary),
        )
        self.conn.commit()

    def get_last_recap(self, guild_id):
        cur = self.conn.execute(
            "SELECT * FROM recaps WHERE guild_id=? ORDER BY generated_at DESC LIMIT 1",
            (guild_id,),
        )
        return cur.fetchone()