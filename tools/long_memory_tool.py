import sqlite3
from pathlib import Path

DB_PATH = "memory.db"

def get_connection():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn


def create_long_memory_table():
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("""
    CREATE TABLE IF NOT EXISTS long_memory (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    content TEXT NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    )
    """)

    conn.commit()
    conn.close()

def save_long_memory(content: str):
    conn = get_connection()
    cursor = conn.cursor()

    try:
        cursor.execute(
            """
            INSERT INTO long_memory (content)
            VALUES (?, ?)
            """, (content)
        )

        conn.commit()
        return {
            "success" : True,
            "message" : "Long-term Memory에 저장됨."
        }

    except Exception as e:
        conn.rollback()

        return {
            "success" : False,
            "message" : str(e)
        }
    
def get_long_memories():
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute(
        """
        SELECT id, content, created_at, updated_at
        FROM long_memory
        ORDER BY created_at ASC
        """
    )

    memories = [dict(row) for row in cursor.fetchall()]

    conn.close()

    return memories

def delete_long_memory(memory_id: int):
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute(
        """
        DELETE FROM long_memory
        WHERE id = ?
        """,
        (memory_id,)
    )

    conn.commit()
    conn.close()


def update_long_memory(memory_id: int, content: str):
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute(
        """
        UPDATE long_memory
        SET content = ?,
            updated_at = CURRENT_TIMESTAMP
        WHERE id = ?
        """,
        (content, memory_id)
    )

    conn.commit()
    conn.close()