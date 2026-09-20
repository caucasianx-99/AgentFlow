
from io import BytesIO

import streamlit as st

from main import analyze_expenses
from agent import run_agent

from task_store import (
    list_tasks,
    save_approved_task
)

from note_store import (
    list_notes,
    save_approved_note
)


# --------------------------------------------------
# PAGE CONFIGURATION
# --------------------------------------------------

st.set_page_config(
    page_title="AgentFlow",
    page_icon="🤖",
    layout="wide"
)


# --------------------------------------------------
# SESSION STATE
# --------------------------------------------------

if "analysis" not in st.session_state:
    st.session_state.analysis = None

if "agent_answer" not in st.session_state:
    st.session_state.agent_answer = None

if "pending_tasks" not in st.session_state:
    st.session_state.pending_tasks = []

if "pending_notes" not in st.session_state:
    st.session_state.pending_notes = []


# --------------------------------------------------
# APPLICATION HEADER
# --------------------------------------------------

st.title("AgentFlow")

st.subheader(
    "AI Agent with Tools & Workflow Automation"
)

st.write(
    "Analyze data, interact with AI tools, "
    "and manage tasks and notes with human approval."
)

st.divider()


# --------------------------------------------------
# 1. CSV UPLOAD
# --------------------------------------------------

st.header("1. Upload Your Data")

uploaded_file = st.file_uploader(
    "Upload an expenses CSV file",
    type=["csv"]
)


# --------------------------------------------------
# 2. USER INSTRUCTION
# --------------------------------------------------

st.header("2. Give Your Agent an Instruction")

user_instruction = st.text_area(
    "What would you like AgentFlow to do?",
    placeholder=(
        "Analyze my expenses, identify the highest "
        "spending category, and propose a task "
        "and note for my approval."
    )
)


# --------------------------------------------------
# RUN THE AI AGENT
# --------------------------------------------------

if st.button("Run Agent", type="primary"):

    if uploaded_file is None:

        st.warning(
            "Please upload a CSV file first."
        )

    elif not user_instruction.strip():

        st.warning(
            "Please enter an instruction."
        )

    else:

        # Clear previous results and proposals

        st.session_state.analysis = None
        st.session_state.agent_answer = None
        st.session_state.pending_tasks = []
        st.session_state.pending_notes = []

        csv_bytes = uploaded_file.getvalue()

        # Analyze the uploaded CSV

        try:

            analysis = analyze_expenses(
                BytesIO(csv_bytes)
            )

            st.session_state.analysis = analysis

        except Exception as error:

            st.error(
                "Unable to analyze the CSV file."
            )

            st.exception(error)

            st.stop()

        # Run Gemini with Python tools

        try:

            with st.spinner(
                "AgentFlow is processing your request..."
            ):

                answer, proposals, notes = run_agent(
                    csv_bytes,
                    user_instruction,
                    return_notes=True
                )

            st.session_state.agent_answer = answer

            st.session_state.pending_tasks = proposals

            st.session_state.pending_notes = notes

        except Exception as error:

            st.error(
                "The AI request failed."
            )

            st.exception(error)


# --------------------------------------------------
# 3. ANALYSIS RESULTS
# --------------------------------------------------

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


# --------------------------------------------------
# 4. AI AGENT RESPONSE
# --------------------------------------------------

if st.session_state.agent_answer:

    st.divider()

    st.header("4. AI Agent Response")

    st.markdown(
        st.session_state.agent_answer
    )


# --------------------------------------------------
# 5. PENDING TASK APPROVAL
# --------------------------------------------------

if st.session_state.pending_tasks:

    st.divider()

    st.header("5. Pending Task Approval")

    st.warning(
        "The following tasks were proposed by AI. "
        "Nothing has been saved yet."
    )

    for index, task_title in enumerate(
        st.session_state.pending_tasks
    ):

        st.write(
            f"**Proposed task:** {task_title}"
        )

        col1, col2 = st.columns(2)

        with col1:

            if st.button(
                "Approve",
                key=f"approve_task_{index}"
            ):

                result = save_approved_task(
                    task_title
                )

                st.session_state.pending_tasks.pop(
                    index
                )

                st.toast(
                    f"Task #{result['id']} saved!"
                )

                st.rerun()

        with col2:

            if st.button(
                "Reject",
                key=f"reject_task_{index}"
            ):

                st.session_state.pending_tasks.pop(
                    index
                )

                st.toast(
                    "Task rejected. Nothing was saved."
                )

                st.rerun()


# --------------------------------------------------
# 6. SAVED TASKS
# --------------------------------------------------

st.divider()

st.header("6. Saved Tasks")

saved_tasks = list_tasks()

if saved_tasks:

    for task in saved_tasks:

        st.write(
            f"**#{task['id']}** — "
            f"{task['title']}"
        )

        st.caption(
            f"Created: {task['created_at']}"
        )

else:

    st.info(
        "No approved tasks have been saved yet."
    )


# --------------------------------------------------
# 7. PENDING NOTE APPROVAL
# --------------------------------------------------

if st.session_state.pending_notes:

    st.divider()

    st.header("7. Pending Note Approval")

    st.warning(
        "The following notes were proposed by AI. "
        "Nothing has been saved yet."
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

                result = save_approved_note(
                    note["title"],
                    note["content"]
                )

                st.session_state.pending_notes.pop(
                    index
                )

                st.toast(
                    f"Note #{result['id']} saved!"
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
                    "Note rejected. Nothing was saved."
                )

                st.rerun()


# --------------------------------------------------
# 8. SAVED NOTES
# --------------------------------------------------

st.divider()

st.header("8. Saved Notes")

saved_notes = list_notes()

if saved_notes:

    for note in saved_notes:

        st.subheader(
            f"#{note['id']} — {note['title']}"
        )

        st.write(
            note["content"]
        )

        st.caption(
            f"Created: {note['created_at']}"
        )

else:

    st.info(
        "No approved notes have been saved yet."
    )