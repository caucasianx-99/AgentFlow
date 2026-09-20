
import sqlite3
from pathlib import Path


DB_PATH = Path(__file__).parent / "agentflow.db"


def init_db():
    """
    Initialize the local task database.
    """

    with sqlite3.connect(DB_PATH) as connection:

        connection.execute(
            """
            CREATE TABLE IF NOT EXISTS tasks (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                title TEXT NOT NULL,
                created_at TEXT DEFAULT CURRENT_TIMESTAMP
            )
            """
        )


def list_tasks():
    """
    Return all previously approved tasks.
    """

    init_db()

    with sqlite3.connect(DB_PATH) as connection:

        connection.row_factory = sqlite3.Row

        rows = connection.execute(
            """
            SELECT id, title, created_at
            FROM tasks
            ORDER BY id DESC
            """
        ).fetchall()

    return [dict(row) for row in rows]


def save_approved_task(title):
    """
    Save a task after explicit user approval.

    This function must only be called from
    the application's approval handler.
    """

    title = title.strip()

    if not title:
        raise ValueError(
            "Task title cannot be empty."
        )

    init_db()

    with sqlite3.connect(DB_PATH) as connection:

        cursor = connection.execute(
            """
            INSERT INTO tasks (title)
            VALUES (?)
            """,
            (title,)
        )

        task_id = cursor.lastrowid

    return {
        "id": task_id,
        "title": title,
        "status": "saved"
    }


if __name__ == "__main__":

    init_db()

    print("AgentFlow — Task Database")
    print("-------------------------")
    print("Database initialized successfully.")

    print("\nSaved tasks:")
    print(list_tasks())