import sqlite3
import uuid
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, List, Optional


class ChatHistoryStore:
    """SQLite-backed conversation and message history."""

    def __init__(self, database_path: Path):
        self.database_path = database_path
        self.database_path.parent.mkdir(parents=True, exist_ok=True)
        self._initialize_database()

    def _connect(self) -> sqlite3.Connection:
        connection = sqlite3.connect(self.database_path)
        connection.row_factory = sqlite3.Row
        connection.execute("PRAGMA foreign_keys = ON")
        return connection

    def _initialize_database(self) -> None:
        with self._connect() as connection:
            connection.executescript(
                """
                CREATE TABLE IF NOT EXISTS conversations (
                    id TEXT PRIMARY KEY,
                    title TEXT NOT NULL,
                    created_at TEXT NOT NULL,
                    updated_at TEXT NOT NULL
                );

                CREATE TABLE IF NOT EXISTS messages (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    conversation_id TEXT NOT NULL,
                    role TEXT NOT NULL CHECK(role IN ('user', 'assistant')),
                    content TEXT NOT NULL,
                    metadata TEXT,
                    created_at TEXT NOT NULL,
                    FOREIGN KEY (conversation_id) REFERENCES conversations(id) ON DELETE CASCADE
                );

                CREATE INDEX IF NOT EXISTS idx_messages_conversation
                ON messages(conversation_id, id);
                """
            )

    @staticmethod
    def _now() -> str:
        return datetime.now(timezone.utc).isoformat()

    def create_conversation(self, title: str) -> Dict[str, Any]:
        conversation_id = str(uuid.uuid4())
        timestamp = self._now()
        with self._connect() as connection:
            connection.execute(
                "INSERT INTO conversations (id, title, created_at, updated_at) VALUES (?, ?, ?, ?)",
                (conversation_id, title, timestamp, timestamp),
            )
        return {
            "id": conversation_id,
            "title": title,
            "created_at": timestamp,
            "updated_at": timestamp,
            "message_count": 0,
        }

    def list_conversations(self) -> List[Dict[str, Any]]:
        with self._connect() as connection:
            rows = connection.execute(
                """
                SELECT c.id, c.title, c.created_at, c.updated_at,
                       COUNT(m.id) AS message_count
                FROM conversations c
                LEFT JOIN messages m ON m.conversation_id = c.id
                GROUP BY c.id
                ORDER BY c.updated_at DESC
                """
            ).fetchall()
        return [dict(row) for row in rows]

    def get_conversation(self, conversation_id: str) -> Optional[Dict[str, Any]]:
        with self._connect() as connection:
            conversation = connection.execute(
                "SELECT id, title, created_at, updated_at FROM conversations WHERE id = ?",
                (conversation_id,),
            ).fetchone()
            if conversation is None:
                return None

            messages = connection.execute(
                """
                SELECT id, role, content, metadata, created_at
                FROM messages
                WHERE conversation_id = ?
                ORDER BY id ASC
                """,
                (conversation_id,),
            ).fetchall()

        result = dict(conversation)
        result["messages"] = [dict(message) for message in messages]
        return result

    def add_message(
        self,
        conversation_id: str,
        role: str,
        content: str,
        metadata: Optional[str] = None,
    ) -> None:
        timestamp = self._now()
        with self._connect() as connection:
            exists = connection.execute(
                "SELECT 1 FROM conversations WHERE id = ?", (conversation_id,)
            ).fetchone()
            if exists is None:
                raise ValueError("Conversation not found")

            connection.execute(
                """
                INSERT INTO messages (conversation_id, role, content, metadata, created_at)
                VALUES (?, ?, ?, ?, ?)
                """,
                (conversation_id, role, content, metadata, timestamp),
            )
            connection.execute(
                "UPDATE conversations SET updated_at = ? WHERE id = ?",
                (timestamp, conversation_id),
            )

    def delete_conversation(self, conversation_id: str) -> bool:
        with self._connect() as connection:
            result = connection.execute(
                "DELETE FROM conversations WHERE id = ?", (conversation_id,)
            )
        return result.rowcount > 0
