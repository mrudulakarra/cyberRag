"""
CyberRAG — Persistent Chat History Database Manager (SQLite)
"""
import sqlite3
import json
import uuid
from datetime import datetime
from pathlib import Path
from typing import List, Dict, Any, Optional

DB_FILE = Path(__file__).parent.parent / "chat_history.sqlite3"

class ChatHistoryDB:
    def __init__(self, db_path: Path = DB_FILE):
        self.db_path = db_path
        self._init_db()

    def _get_connection(self):
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        return conn

    def _init_db(self):
        """Creates chat_sessions and chat_messages tables if they don't exist."""
        with self._get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS chat_sessions (
                    session_id TEXT PRIMARY KEY,
                    title TEXT NOT NULL,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            """)
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS chat_messages (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    session_id TEXT NOT NULL,
                    sender TEXT NOT NULL,
                    data_json TEXT NOT NULL,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY (session_id) REFERENCES chat_sessions(session_id) ON DELETE CASCADE
                )
            """)
            conn.commit()

    def create_session(self, initial_title: str = "New CyberRAG Chat") -> str:
        """Creates a new session and returns its ID."""
        session_id = f"session_{uuid.uuid4().hex[:10]}"
        now = datetime.now().isoformat()
        with self._get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute(
                "INSERT INTO chat_sessions (session_id, title, created_at, updated_at) VALUES (?, ?, ?, ?)",
                (session_id, initial_title[:60], now, now)
            )
            conn.commit()
        return session_id

    def add_message(self, session_id: str, sender: str, data: Dict[str, Any], auto_update_title: bool = False):
        """Adds a message to a chat session."""
        now = datetime.now().isoformat()
        data_json = json.dumps(data)
        
        with self._get_connection() as conn:
            cursor = conn.cursor()
            
            # Check if session exists; if not, create it
            cursor.execute("SELECT session_id, title FROM chat_sessions WHERE session_id = ?", (session_id,))
            session = cursor.fetchone()
            
            if not session:
                title = data.get("question", "Cybersecurity Chat")[:60] if sender == "user" else "CyberRAG Session"
                cursor.execute(
                    "INSERT INTO chat_sessions (session_id, title, created_at, updated_at) VALUES (?, ?, ?, ?)",
                    (session_id, title, now, now)
                )
            elif auto_update_title and sender == "user" and session["title"] == "New CyberRAG Chat":
                # Auto update title to the first user question
                cursor.execute(
                    "UPDATE chat_sessions SET title = ?, updated_at = ? WHERE session_id = ?",
                    (data.get("question", "Cybersecurity Chat")[:60], now, session_id)
                )
            else:
                cursor.execute("UPDATE chat_sessions SET updated_at = ? WHERE session_id = ?", (now, session_id))

            cursor.execute(
                "INSERT INTO chat_messages (session_id, sender, data_json, created_at) VALUES (?, ?, ?, ?)",
                (session_id, sender, data_json, now)
            )
            conn.commit()

    def get_sessions(self) -> List[Dict[str, Any]]:
        """Returns all chat sessions ordered by updated_at desc."""
        with self._get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("""
                SELECT s.session_id, s.title, s.created_at, s.updated_at, COUNT(m.id) as message_count
                FROM chat_sessions s
                LEFT JOIN chat_messages m ON s.session_id = m.session_id
                GROUP BY s.session_id
                ORDER BY s.updated_at DESC
            """)
            rows = cursor.fetchall()
            return [dict(r) for r in rows]

    def get_session_messages(self, session_id: str) -> List[Dict[str, Any]]:
        """Returns all messages for a given session."""
        with self._get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute(
                "SELECT sender, data_json, created_at FROM chat_messages WHERE session_id = ? ORDER BY id ASC",
                (session_id,)
            )
            rows = cursor.fetchall()
            messages = []
            for r in rows:
                msg = dict(r)
                msg["data"] = json.loads(msg["data_json"])
                del msg["data_json"]
                messages.append(msg)
            return messages

    def delete_session(self, session_id: str):
        """Deletes a chat session and all its messages."""
        with self._get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("DELETE FROM chat_messages WHERE session_id = ?", (session_id,))
            cursor.execute("DELETE FROM chat_sessions WHERE session_id = ?", (session_id,))
            conn.commit()

    def clear_all_history(self):
        """Clears all sessions and messages."""
        with self._get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("DELETE FROM chat_messages")
            cursor.execute("DELETE FROM chat_sessions")
            conn.commit()

# Singleton instance
history_db = ChatHistoryDB()
