
import pytest

import task_store
import note_store


@pytest.fixture
def isolated_database(tmp_path, monkeypatch):
    """
    Use a temporary database for each test.

    Never modify the real agentflow.db.
    """

    test_db = tmp_path / "test_agentflow.db"

    monkeypatch.setattr(
        task_store,
        "DB_PATH",
        test_db
    )

    monkeypatch.setattr(
        note_store,
        "DB_PATH",
        test_db
    )

    return test_db


def test_database_starts_empty(isolated_database):
    """
    No records should exist before saving.
    """

    assert task_store.list_tasks() == []

    assert note_store.list_notes() == []


def test_save_approved_task(isolated_database):
    """
    Verify task persistence.
    """

    result = task_store.save_approved_task(
        "Review Shopping expenses"
    )

    assert result["status"] == "saved"

    saved_tasks = task_store.list_tasks()

    assert len(saved_tasks) == 1

    assert (
        saved_tasks[0]["title"]
        == "Review Shopping expenses"
    )


def test_empty_task_rejected(isolated_database):
    """
    Invalid tasks must not be saved.
    """

    with pytest.raises(ValueError):

        task_store.save_approved_task("   ")

    assert task_store.list_tasks() == []


def test_save_approved_note(isolated_database):
    """
    Verify note persistence.
    """

    result = note_store.save_approved_note(
        "September Expenses Summary",
        "Total spending was 408."
    )

    assert result["status"] == "saved"

    saved_notes = note_store.list_notes()

    assert len(saved_notes) == 1

    assert (
        saved_notes[0]["title"]
        == "September Expenses Summary"
    )

    assert (
        saved_notes[0]["content"]
        == "Total spending was 408."
    )


def test_empty_note_rejected(isolated_database):
    """
    Invalid notes must not be saved.
    """

    with pytest.raises(ValueError):

        note_store.save_approved_note(
            "September Summary",
            ""
        )

    assert note_store.list_notes() == []