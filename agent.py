
import os
from io import BytesIO
from pathlib import Path

from dotenv import load_dotenv
from google import genai

from main import analyze_expenses
from task_store import list_tasks


# ----------------------------------------
# GEMINI CONFIGURATION
# ----------------------------------------

load_dotenv()

api_key = os.getenv("GEMINI_API_KEY")

if not api_key:
    raise ValueError(
        "GEMINI_API_KEY was not found in .env"
    )

client = genai.Client(api_key=api_key)


# ----------------------------------------
# AI AGENT
# ----------------------------------------

def run_agent(
    csv_bytes,
    user_instruction,
    return_proposals=False,
    return_notes=False
):

    proposed_tasks = []
    proposed_notes = []

    # ------------------------------------
    # TOOL 1 — EXPENSE ANALYSIS
    # ------------------------------------

    def get_expense_summary() -> dict:
        """
        Analyze the uploaded expenses CSV.

        Return total spending, transaction count,
        category totals, and highest spending category.
        """

        print("\n[TOOL CALLED] get_expense_summary")

        csv_file = BytesIO(csv_bytes)

        result = analyze_expenses(csv_file)

        print("[TOOL RESULT]", result)

        return result

    # ------------------------------------
    # TOOL 2 — TASK PROPOSAL
    # ------------------------------------

    def propose_task(title: str) -> dict:
        """
        Propose a follow-up task for user approval.

        This tool does not save the task.
        """

        print("\n[TOOL CALLED] propose_task")

        title = title.strip()

        if not title:
            return {
                "status": "error",
                "message": "Task title cannot be empty."
            }

        if len(title) > 200:
            return {
                "status": "error",
                "message": "Task title is too long."
            }

        proposed_tasks.append(title)

        result = {
            "status": "pending_approval",
            "title": title,
            "saved": False
        }

        print("[TASK PROPOSED]", result)

        return result

    # ------------------------------------
    # TOOL 3 — NOTE PROPOSAL
    # ------------------------------------

    def propose_note(
        title: str,
        content: str
    ) -> dict:
        """
        Propose a note for user approval.

        This tool does not save the note.
        """

        print("\n[TOOL CALLED] propose_note")

        title = title.strip()
        content = content.strip()

        if not title or not content:
            return {
                "status": "error",
                "message": "Title and content are required."
            }

        if len(title) > 200:
            return {
                "status": "error",
                "message": "Note title is too long."
            }

        if len(content) > 5000:
            return {
                "status": "error",
                "message": "Note content is too long."
            }

        note = {
            "title": title,
            "content": content
        }

        proposed_notes.append(note)

        result = {
            "status": "pending_approval",
            "note": note,
            "saved": False
        }

        print("[NOTE PROPOSED]", result)

        return result

    # ------------------------------------
    # CREATE GEMINI AGENT
    # ------------------------------------

    chat = client.chats.create(
        model="gemini-3.5-flash-lite",
        config={
            "tools": [
                get_expense_summary,
                propose_task,
                propose_note
            ],

            "system_instruction": (
                "You are AgentFlow, a tool-using AI assistant. "

                "Use the expense analysis tool for "
                "financial calculations. "

                "Never invent spending figures. "

                "When the user requests a follow-up "
                "task, use propose_task. "

                "When the user requests a note, "
                "use propose_note. "

                "A proposal is not a saved record. "

                "Never claim a task or note was "
                "saved or approved. "

                "All task and note proposals require "
                "explicit user approval before saving. "
            )
        }
    )

    # ------------------------------------
    # PROCESS USER REQUEST
    # ------------------------------------

    response = chat.send_message(
        user_instruction
    )

    print("\nPending task proposals:")
    print(proposed_tasks)

    print("\nPending note proposals:")
    print(proposed_notes)

    # ------------------------------------
    # RETURN RESULTS TO STREAMLIT
    # ------------------------------------

    if return_notes:
        return (
            response.text,
            proposed_tasks,
            proposed_notes
        )

    if return_proposals:
        return (
            response.text,
            proposed_tasks
        )

    return response.text


# ----------------------------------------
# TERMINAL TEST
# ----------------------------------------

if __name__ == "__main__":

    sample_path = (
        Path(__file__).parent / "sample_expenses.csv"
    )

    csv_bytes = sample_path.read_bytes()

    instruction = (
        "Analyze my expenses using your tools. "
        "Identify the highest spending category. "
        "Propose a task to review that category. "
        "Also propose a note summarizing the "
        "expense analysis. "
        "Do not save anything."
    )

    tasks_before = list_tasks()

    answer, tasks, notes = run_agent(
        csv_bytes,
        instruction,
        return_notes=True
    )

    tasks_after = list_tasks()

    print("\nAgentFlow — AI Agent Response")
    print("-----------------------------")
    print(answer)

    print("\nProposed tasks:")
    print(tasks)

    print("\nProposed notes:")
    print(notes)

    print("\nTask database unchanged:")
    print(tasks_before == tasks_after)