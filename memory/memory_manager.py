import sqlite3
from typing import List, Dict

class MemoryManager:
  def __init__(self, db_path: str = "memory.db"):
    self.db_path = db_path
    self._initialize_db()

  def _get_connection(self):
    return sqlite3.connect(self.db_path)
  
  def _initialize_db(self):
    conn = self._get_connection()
    cursor = conn.cursor()

    cursor.execute(
      """
      CREATE TABLE IF NOT EXISTS conversation (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        guild_id INTEGER NOT NULL,
        channel_id INTEGER NOT NULL,
        role TEXT NOT NULL,
        content TEXT NOT NULL,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
      )
      """)
    conn.commit()
    conn.close()

  def add_message(self, guild_id: int, channel_id: int, role: str, content: str):
    conn = self._get_connection()
    cursor = conn.cursor()

    cursor.execute("""
    INSERT INTO conversation (guild_id, channel_id, role, content)
                   VALUES (?, ?, ?, ?)
    """, (guild_id, channel_id, role, content))

    conn.commit()
    conn.close()

  def get_history(self, guild_id: int, channel_id: int, limit: int=20) -> List[Dict]:
    conn = self._get_connection()
    cursor = conn.cursor()

    cursor.execute(
      """
      SELECT role, content
      FROM conversation
      WHERE guild_id = ? AND channel_id = ?
      ORDER BY id DESC
      LIMIT ?
      """, (guild_id, channel_id, limit)
    )

    rows = cursor.fetchall()
    conn.close()

    rows.reverse()

    return [{"role": role, "content": content} for role, content in rows]
  
  def clear_channel(self, guild_id: int, channel_id: int):
    conn = self._get_connection()
    cursor = conn.cursor()

    cursor.execute(
      """
      DELETE FROM conversation WHERE guild_id = ? AND channel_id = ?
      """, (guild_id, channel_id)
    )

    conn.commit()
    conn.close()