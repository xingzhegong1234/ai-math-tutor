"""SQLite database for storing conversation history and bookmarks."""

import json
import sqlite3
from datetime import datetime
from typing import Optional
from contextlib import contextmanager

from ..config import DB_PATH


@contextmanager
def get_db():
    conn = sqlite3.connect(str(DB_PATH))
    conn.row_factory = sqlite3.Row
    try:
        yield conn
    finally:
        conn.close()


def init_db():
    with get_db() as db:
        db.executescript("""
            CREATE TABLE IF NOT EXISTS conversations (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                title TEXT NOT NULL DEFAULT '新对话',
                created_at TEXT NOT NULL DEFAULT (datetime('now','localtime')),
                updated_at TEXT NOT NULL DEFAULT (datetime('now','localtime')),
                bookmarked INTEGER NOT NULL DEFAULT 0
            );

            CREATE TABLE IF NOT EXISTS messages (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                conversation_id INTEGER NOT NULL,
                role TEXT NOT NULL CHECK(role IN ('user','assistant','system')),
                content TEXT NOT NULL,
                image_path TEXT,
                created_at TEXT NOT NULL DEFAULT (datetime('now','localtime')),
                FOREIGN KEY (conversation_id) REFERENCES conversations(id) ON DELETE CASCADE
            );

            CREATE INDEX IF NOT EXISTS idx_messages_conv ON messages(conversation_id);
            CREATE INDEX IF NOT EXISTS idx_conversations_updated ON conversations(updated_at DESC);
        """)


# --- Conversation CRUD ---

def create_conversation(title: str = "新对话") -> int:
    with get_db() as db:
        cur = db.execute(
            "INSERT INTO conversations (title) VALUES (?)", (title,)
        )
        db.commit()
        return cur.lastrowid


def get_conversations(bookmarked_only: bool = False) -> list[dict]:
    with get_db() as db:
        if bookmarked_only:
            rows = db.execute(
                "SELECT * FROM conversations WHERE bookmarked = 1 ORDER BY updated_at DESC"
            ).fetchall()
        else:
            rows = db.execute(
                "SELECT * FROM conversations ORDER BY updated_at DESC"
            ).fetchall()
        return [dict(r) for r in rows]


def get_conversation(conv_id: int) -> Optional[dict]:
    with get_db() as db:
        row = db.execute(
            "SELECT * FROM conversations WHERE id = ?", (conv_id,)
        ).fetchone()
        return dict(row) if row else None


def update_conversation_title(conv_id: int, title: str):
    with get_db() as db:
        db.execute(
            "UPDATE conversations SET title = ?, updated_at = datetime('now','localtime') WHERE id = ?",
            (title, conv_id),
        )
        db.commit()


def toggle_bookmark(conv_id: int) -> bool:
    with get_db() as db:
        db.execute(
            """UPDATE conversations
               SET bookmarked = CASE WHEN bookmarked = 0 THEN 1 ELSE 0 END,
                   updated_at = datetime('now','localtime')
               WHERE id = ?""",
            (conv_id,),
        )
        db.commit()
        row = db.execute("SELECT bookmarked FROM conversations WHERE id = ?", (conv_id,)).fetchone()
        return bool(row["bookmarked"]) if row else False


def delete_conversation(conv_id: int):
    with get_db() as db:
        db.execute("DELETE FROM messages WHERE conversation_id = ?", (conv_id,))
        db.execute("DELETE FROM conversations WHERE id = ?", (conv_id,))
        db.commit()


# --- Messages CRUD ---

def add_message(conv_id: int, role: str, content: str, image_path: str = "") -> int:
    with get_db() as db:
        cur = db.execute(
            "INSERT INTO messages (conversation_id, role, content, image_path) VALUES (?, ?, ?, ?)",
            (conv_id, role, content, image_path),
        )
        db.execute(
            "UPDATE conversations SET updated_at = datetime('now','localtime') WHERE id = ?",
            (conv_id,),
        )
        db.commit()
        return cur.lastrowid


def get_messages(conv_id: int) -> list[dict]:
    with get_db() as db:
        rows = db.execute(
            "SELECT * FROM messages WHERE conversation_id = ? ORDER BY id",
            (conv_id,),
        ).fetchall()
        return [dict(r) for r in rows]
