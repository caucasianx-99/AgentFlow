
from io import BytesIO

from google import genai

from main import analyze_expenses


MODEL = "gemini-3.5-flash-lite"


def run_agent(
    csv_bytes,
    user_instruction,
    *,
    api_key,
    return_proposals=False,
    return_notes=False
):
    """
    Run AgentFlow using the visitor's own
    Gemini API key.

    The API key is never written to a file,
    database, or application log.
    """

    if not api_key or not api_key.strip():
        raise ValueError(
            "A Gemini API key is required."
        )

    proposed_tasks = []
    proposed_notes = []

    # ----------------------------------
    # TOOL 1 — EXPENSE ANALYSIS
    # ----------------------------------

    def get_expense_summary() -> dict:
        """
        Analyze the uploaded expenses CSV.

        Return transaction count, total spending,
        category totals, and highest category.
        """

        csv_file = BytesIO(csv_bytes)

        return analyze_expenses(csv_file)

    # ----------------------------------
    # TOOL 2 — TASK PROPOSAL
    # ----------------------------------

    def propose_task(title: str) -> dict:
        """
        Propose a task for user approval.

        This function never saves tasks.
        """

        title = title.strip()

        if not title or len(title) > 200:
            return {
                "status": "error",
                "message": "Invalid task title."
            }

        proposed_tasks.append(title)

        return {
            "status": "pending_approval",
            "title": title,
            "saved": False
        }

    # ----------------------------------
    # TOOL 3 — NOTE PROPOSAL
    # ----------------------------------

    def propose_note(
        title: str,
        content: str
    ) -> dict:
        """
        Propose a note for user approval.

        This function never saves notes.
        """

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

        return {
            "status": "pending_approval",
            "note": note,
            "saved": False
        }

    # ----------------------------------
    # CONNECT USING VISITOR'S KEY
    # ----------------------------------

    client = genai.Client(
        api_key=api_key.strip()
    )

    chat = client.chats.create(
        model=MODEL,
        config={
            "tools": [
                get_expense_summary,
                propose_task,
                propose_note
            ],
            "system_instruction": (
                "You are AgentFlow, a tool-using "
                "AI assistant. "

                "Use the expense analysis tool "
                "for financial calculations. "

                "Never invent spending figures. "

                "When the user requests a task, "
                "use propose_task. "

                "When the user requests a note, "
                "use propose_note. "

                "Never claim that a proposal "
                "has been saved or approved. "

                "All proposals require explicit "
                "user approval."
            )
        }
    )

    response = chat.send_message(
        user_instruction
    )

    # ----------------------------------
    # RETURN RESULTS
    # ----------------------------------

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