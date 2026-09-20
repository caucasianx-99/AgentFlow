
import sqlite3

from task_store import DB_PATH


def init_notes_db():
    """
    Initialize the notes table.
    """

    with sqlite3.connect(DB_PATH) as connection:

        connection.execute(
            """
            CREATE TABLE IF NOT EXISTS notes (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                title TEXT NOT NULL,
                content TEXT NOT NULL,
                created_at TEXT DEFAULT CURRENT_TIMESTAMP
            )
            """
        )


def list_notes():
    """
    Return all saved notes.
    """

    init_notes_db()

    with sqlite3.connect(DB_PATH) as connection:

        connection.row_factory = sqlite3.Row

        rows = connection.execute(
            """
            SELECT id, title, content, created_at
            FROM notes
            ORDER BY id DESC
            """
        ).fetchall()

    return [dict(row) for row in rows]


def save_approved_note(title, content):
    """
    Save a note after explicit user approval.

    This function must only be called from
    the application's approval handler.
    """

    title = title.strip()
    content = content.strip()

    if not title:
        raise ValueError(
            "Note title cannot be empty."
        )

    if not content:
        raise ValueError(
            "Note content cannot be empty."
        )

    if len(title) > 200:
        raise ValueError(
            "Note title is too long."
        )

    if len(content) > 5000:
        raise ValueError(
            "Note content is too long."
        )

    init_notes_db()

    with sqlite3.connect(DB_PATH) as connection:

        cursor = connection.execute(
            """
            INSERT INTO notes (title, content)
            VALUES (?, ?)
            """,
            (title, content)
        )

        note_id = cursor.lastrowid

    return {
        "id": note_id,
        "title": title,
        "content": content,
        "status": "saved"
    }


if __name__ == "__main__":

    init_notes_db()

    print("AgentFlow — Notes Database")
    print("--------------------------")

    print("Notes table initialized successfully.")

    print("\nSaved notes:")
    print(list_notes())