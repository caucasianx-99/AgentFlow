
import os
import hmac

from io import BytesIO

import streamlit as st

from main import analyze_expenses


# ==========================================
# PAGE CONFIGURATION
# ==========================================

st.set_page_config(
    page_title="AgentFlow",
    page_icon="🤖",
    layout="wide"
)


# ==========================================
# PUBLIC DEPLOYMENT SETTINGS
# ==========================================

PUBLIC_MODE = (
    os.getenv(
        "AGENTFLOW_PUBLIC_DEMO", ""
    ).strip().lower() == "true"
)

MAX_DEMO_REQUESTS = 5


# ==========================================
# PUBLIC DEMO ACCESS
# ==========================================

if PUBLIC_MODE:

    demo_password = os.getenv(
        "AGENTFLOW_DEMO_PASSWORD", ""
    )

    if not demo_password:

        st.error(
            "Demo password is not configured."
        )

        st.stop()

    if not os.getenv("GEMINI_API_KEY"):

        st.error(
            "Gemini API is not configured."
        )

        st.stop()

    if "demo_authorized" not in st.session_state:

        st.session_state.demo_authorized = False

    if "demo_requests" not in st.session_state:

        st.session_state.demo_requests = 0

    if not st.session_state.demo_authorized:

        st.title("🤖 AgentFlow")

        st.subheader(
            "AI Agent with Tools & Workflow Automation"
        )

        st.write(
            "Enter the demonstration password "
            "to access AgentFlow."
        )

        entered_password = st.text_input(
            "Demo access password",
            type="password"
        )

        if st.button(
            "Open AgentFlow",
            type="primary"
        ):

            if hmac.compare_digest(
                entered_password,
                demo_password
            ):

                st.session_state.demo_authorized = True

                st.rerun()

            else:

                st.error(
                    "Incorrect demonstration password."
                )

        st.stop()


# ==========================================
# IMPORT THE REAL GEMINI AGENT
# ==========================================

from agent import run_agent


# Local database functions are only used
# outside the public cloud demo.

if not PUBLIC_MODE:

    from task_store import (
        list_tasks,
        save_approved_task
    )

    from note_store import (
        list_notes,
        save_approved_note
    )


# ==========================================
# SESSION STATE
# ==========================================

if "analysis" not in st.session_state:

    st.session_state.analysis = None

if "agent_answer" not in st.session_state:

    st.session_state.agent_answer = None

if "pending_tasks" not in st.session_state:

    st.session_state.pending_tasks = []

if "pending_notes" not in st.session_state:

    st.session_state.pending_notes = []

if "demo_saved_tasks" not in st.session_state:

    st.session_state.demo_saved_tasks = []

if "demo_saved_notes" not in st.session_state:

    st.session_state.demo_saved_notes = []


# ==========================================
# APPLICATION HEADER
# ==========================================

st.title("🤖 AgentFlow")

st.subheader(
    "AI Agent with Tools & Workflow Automation"
)

st.write(
    "Analyze data using Gemini AI, "
    "call Python tools, and manage "
    "tasks and notes with human approval."
)

st.link_button(
    "View Source Code on GitHub",
    "https://github.com/caucasianx-99/AgentFlow"
)


if PUBLIC_MODE:

    st.info(
        "Public portfolio demonstration. "
        "This application uses real Gemini AI. "
        "Approved tasks and notes are temporary "
        "and private to your current session."
    )

    remaining = (
        MAX_DEMO_REQUESTS
        - st.session_state.demo_requests
    )

    st.caption(
        f"AI requests remaining in this session: "
        f"{remaining}"
    )

    st.warning(
        "Use only fictional or non-confidential "
        "data. Do not upload private financial "
        "or personal information."
    )


st.divider()


# ==========================================
# 1. UPLOAD DATA
# ==========================================

st.header("1. Upload Your Data")

uploaded_file = st.file_uploader(
    "Upload an expenses CSV file",
    type=["csv"]
)

st.caption(
    "Required CSV columns: category, amount"
)


# ==========================================
# 2. USER INSTRUCTION
# ==========================================

st.header("2. Give Your Agent an Instruction")

user_instruction = st.text_area(
    "What would you like AgentFlow to do?",
    placeholder=(
        "Analyze my expenses, identify the "
        "highest spending category, and "
        "propose a task and note for approval."
    )
)


# ==========================================
# RUN AGENT
# ==========================================

if st.button(
    "Run Agent",
    type="primary"
):

    if uploaded_file is None:

        st.warning(
            "Please upload a CSV file first."
        )

    elif not user_instruction.strip():

        st.warning(
            "Please enter an instruction."
        )

    elif (
        PUBLIC_MODE
        and st.session_state.demo_requests
        >= MAX_DEMO_REQUESTS
    ):

        st.warning(
            "The demonstration request limit "
            "has been reached for this session."
        )

    else:

        # Clear previous results

        st.session_state.analysis = None

        st.session_state.agent_answer = None

        st.session_state.pending_tasks = []

        st.session_state.pending_notes = []

        csv_bytes = uploaded_file.getvalue()

        # Limit public CSV file size to 1 MB.

        if (
            PUBLIC_MODE
            and len(csv_bytes) > 1_000_000
        ):

            st.error(
                "The public demo accepts CSV "
                "files up to 1 MB."
            )

            st.stop()

        # ----------------------------------
        # ANALYZE CSV
        # ----------------------------------

        try:

            analysis = analyze_expenses(
                BytesIO(csv_bytes)
            )

            st.session_state.analysis = analysis

        except ValueError as error:

            st.error(str(error))

            st.stop()

        except Exception:

            st.error(
                "Unable to analyze the CSV file."
            )

            st.stop()

        # ----------------------------------
        # RUN REAL GEMINI AGENT
        # ----------------------------------

        try:

            if PUBLIC_MODE:

                st.session_state.demo_requests += 1

            with st.spinner(
                "AgentFlow is processing "
                "your request..."
            ):

                answer, tasks, notes = run_agent(
                    csv_bytes,
                    user_instruction,
                    return_notes=True
                )

            st.session_state.agent_answer = answer

            st.session_state.pending_tasks = tasks

            st.session_state.pending_notes = notes

        except Exception as error:

            if PUBLIC_MODE:

                st.error(
                    "The AI request could not "
                    "be completed. Please try "
                    "again later."
                )

            else:

                st.exception(error)


# ==========================================
# 3. ANALYSIS RESULTS
# ==========================================

if st.session_state.analysis is not None:

    analysis = st.session_state.analysis

    st.divider()

    st.header("3. Analysis Results")

    st.success(
        "CSV analysis completed successfully!"
    )

    col1, col2 = st.columns(2)

    with col1:

        st.metric(
            "Total Spending",
            f"{analysis['total_spending']:.2f}"
        )

    with col2:

        st.metric(
            "Total Transactions",
            analysis["total_transactions"]
        )

    st.subheader(
        "Highest Spending Category"
    )

    st.info(
        f"{analysis['highest_spending_category']}: "
        f"{analysis['highest_category_amount']:.2f}"
    )

    st.subheader("Complete Analysis")

    st.json(analysis)


# ==========================================
# 4. AI RESPONSE
# ==========================================

if st.session_state.agent_answer:

    st.divider()

    st.header("4. AI Agent Response")

    st.markdown(
        st.session_state.agent_answer
    )

    st.caption(
        "The AI response describes the "
        "original proposals. Current approval "
        "status is shown below."
    )


# ==========================================
# 5. TASK APPROVAL
# ==========================================

if st.session_state.pending_tasks:

    st.divider()

    st.header("5. Pending Task Approval")

    st.warning(
        "The following tasks were proposed "
        "by AI. Nothing has been saved yet."
    )

    for index, title in enumerate(
        st.session_state.pending_tasks
    ):

        st.write(
            f"**Proposed task:** {title}"
        )

        col1, col2 = st.columns(2)

        with col1:

            if st.button(
                "Approve Task",
                key=f"approve_task_{index}"
            ):

                if PUBLIC_MODE:

                    st.session_state.demo_saved_tasks.append(
                        title
                    )

                else:

                    save_approved_task(title)

                st.session_state.pending_tasks.pop(
                    index
                )

                st.toast(
                    "Task approved!"
                )

                st.rerun()

        with col2:

            if st.button(
                "Reject Task",
                key=f"reject_task_{index}"
            ):

                st.session_state.pending_tasks.pop(
                    index
                )

                st.toast(
                    "Task rejected."
                )

                st.rerun()


# ==========================================
# 6. SAVED TASKS
# ==========================================

st.divider()

st.header(
    "6. Approved Tasks"
    if PUBLIC_MODE
    else "6. Saved Tasks"
)

if PUBLIC_MODE:

    saved_tasks = st.session_state.demo_saved_tasks

    for index, title in enumerate(
        saved_tasks,
        start=1
    ):

        st.write(
            f"**#{index}** — {title}"
        )

else:

    saved_tasks = list_tasks()

    for task in saved_tasks:

        st.write(
            f"**#{task['id']}** — "
            f"{task['title']}"
        )

        st.caption(
            f"Created: {task['created_at']}"
        )


if not saved_tasks:

    st.info(
        "No approved tasks yet."
    )


# ==========================================
# 7. NOTE APPROVAL
# ==========================================

if st.session_state.pending_notes:

    st.divider()

    st.header("7. Pending Note Approval")

    st.warning(
        "The following notes were proposed "
        "by AI. Nothing has been saved yet."
    )

    for index, note in enumerate(
        st.session_state.pending_notes
    ):

        st.subheader(
            note["title"]
        )

        st.write(
            note["content"]
        )

        col1, col2 = st.columns(2)

        with col1:

            if st.button(
                "Approve Note",
                key=f"approve_note_{index}"
            ):

                if PUBLIC_MODE:

                    st.session_state.demo_saved_notes.append(
                        note.copy()
                    )

                else:

                    save_approved_note(
                        note["title"],
                        note["content"]
                    )

                st.session_state.pending_notes.pop(
                    index
                )

                st.toast(
                    "Note approved!"
                )

                st.rerun()

        with col2:

            if st.button(
                "Reject Note",
                key=f"reject_note_{index}"
            ):

                st.session_state.pending_notes.pop(
                    index
                )

                st.toast(
                    "Note rejected."
                )

                st.rerun()


# ==========================================
# 8. SAVED NOTES
# ==========================================

st.divider()

st.header(
    "8. Approved Notes"
    if PUBLIC_MODE
    else "8. Saved Notes"
)

if PUBLIC_MODE:

    saved_notes = st.session_state.demo_saved_notes

else:

    saved_notes = list_notes()


if saved_notes:

    for index, note in enumerate(
        saved_notes,
        start=1
    ):

        note_id = (
            index
            if PUBLIC_MODE
            else note["id"]
        )

        st.subheader(
            f"#{note_id} — {note['title']}"
        )

        st.write(
            note["content"]
        )

        if not PUBLIC_MODE:

            st.caption(
                f"Created: {note['created_at']}"
            )

else:

    st.info(
        "No approved notes yet."
    )


# ==========================================
# FOOTER
# ==========================================

if PUBLIC_MODE:

    st.divider()

    st.caption(
        "AgentFlow portfolio demonstration. "
        "Gemini AI is real. Task and note "
        "approvals are temporary for this "
        "browser session and are not stored "
        "in a permanent cloud database."
    )