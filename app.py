
from io import BytesIO
from pathlib import Path
import hashlib

import streamlit as st

from main import analyze_expenses
from agent import run_agent


# ==========================================
# PAGE CONFIGURATION
# ==========================================

st.set_page_config(
    page_title="AgentFlow",
    page_icon="🤖",
    layout="wide"
)


# ==========================================
# SESSION STATE
# ==========================================

defaults = {
    "analysis": None,
    "agent_answer": None,
    "pending_tasks": [],
    "pending_notes": [],
    "saved_tasks": [],
    "saved_notes": [],
    "file_signature": None,
}

for key, value in defaults.items():
    if key not in st.session_state:
        st.session_state[key] = value


# ==========================================
# HEADER
# ==========================================

st.title("🤖 AgentFlow")

st.subheader(
    "AI Agent with Function Calling "
    "& Workflow Automation"
)

st.write(
    "Analyze expenses, interact with Gemini AI, "
    "and manage tasks and notes with "
    "human approval."
)

st.link_button(
    "View Source Code on GitHub",
    "https://github.com/caucasianx-99/AgentFlow"
)

st.info(
    "Public portfolio demonstration. "
    "CSV analysis is available without an API key. "
    "Real AI functionality requires your own "
    "Gemini API key."
)

st.warning(
    "Use fictional or non-confidential test data. "
    "AI instructions and tool results are "
    "processed by Gemini when AI is enabled."
)


# ==========================================
# 1. SELECT DATA
# ==========================================

st.divider()

st.header("1. Select Your Data")

use_sample = st.checkbox(
    "Use fictional sample expenses",
    value=True
)

if use_sample:

    sample_path = (
        Path(__file__).parent
        / "sample_expenses.csv"
    )

    csv_bytes = sample_path.read_bytes()

    st.success(
        "Fictional sample dataset loaded."
    )

    st.download_button(
        "Download Sample CSV",
        data=csv_bytes,
        file_name="sample_expenses.csv",
        mime="text/csv"
    )

else:

    uploaded_file = st.file_uploader(
        "Upload your expenses CSV",
        type=["csv"]
    )

    csv_bytes = (
        uploaded_file.getvalue()
        if uploaded_file is not None
        else None
    )

st.caption(
    "Required columns: category, amount. "
    "Maximum file size: 1 MB."
)


# ==========================================
# RESET RESULTS WHEN DATA CHANGES
# ==========================================

if csv_bytes is not None:

    signature = hashlib.sha256(
        csv_bytes
    ).hexdigest()

else:

    signature = None

if signature != st.session_state.file_signature:

    st.session_state.file_signature = signature

    st.session_state.analysis = None
    st.session_state.agent_answer = None
    st.session_state.pending_tasks = []
    st.session_state.pending_notes = []


# ==========================================
# 2. FREE CSV ANALYSIS
# ==========================================

st.divider()

st.header("2. Free CSV Analysis")

st.write(
    "Analyze expenses using Python and pandas. "
    "No Gemini API key is required."
)

if st.button(
    "Analyze CSV",
    type="primary"
):

    if csv_bytes is None:

        st.warning(
            "Please select a CSV file."
        )

    elif len(csv_bytes) > 1_000_000:

        st.error(
            "The maximum file size is 1 MB."
        )

    else:

        try:

            result = analyze_expenses(
                BytesIO(csv_bytes)
            )

            st.session_state.analysis = result

            st.session_state.agent_answer = None
            st.session_state.pending_tasks = []
            st.session_state.pending_notes = []

        except ValueError as error:

            st.error(str(error))

        except Exception:

            st.error(
                "Unable to analyze the CSV."
            )


# ==========================================
# 3. ANALYSIS RESULTS
# ==========================================

if st.session_state.analysis is not None:

    analysis = st.session_state.analysis

    st.divider()

    st.header("3. Analysis Results")

    col1, col2 = st.columns(2)

    with col1:

        st.metric(
            "Total Spending",
            f"{analysis['total_spending']:,.2f}"
        )

    with col2:

        st.metric(
            "Transactions",
            analysis["total_transactions"]
        )

    st.subheader(
        "Highest Spending Category"
    )

    st.success(
        f"{analysis['highest_spending_category']}: "
        f"{analysis['highest_category_amount']:,.2f}"
    )

    st.subheader(
    "Spending by Category"
    )

    for category, amount in analysis[
    "spending_by_category"
    ].items():

     st.write(
        f"**{category}:** {amount:,.2f}"
    )

    st.subheader(
        "Structured Analysis"
    )

    st.json(analysis)


# ==========================================
# EXAMPLE AI WORKFLOW
# ==========================================

st.divider()

with st.expander(
    "See an example AI workflow"
):

    st.write(
        "The following example illustrates "
        "AgentFlow's tool-calling and "
        "approval workflow."
    )

    st.markdown(
        """
        **Example instruction**

        Analyze my expenses, identify the
        highest spending category, and
        propose a task and summary note.

        **Example result**

        Total spending: 408.00

        Highest category: Shopping — 200.00

        **Proposed task**

        Review Shopping expenses.

        **Proposed note**

        September Expenses Summary.

        Both proposals remain pending until
        the user explicitly approves them.
        """
    )

    st.caption(
        "This is a predefined example, "
        "not a live Gemini response."
    )


# ==========================================
# 4. REAL GEMINI CONNECTION
# ==========================================

st.divider()

st.header("4. Connect to Gemini AI")

st.write(
    "Enter your own Gemini API key to use "
    "AgentFlow's real AI capabilities."
)

api_key = st.text_input(
    "Your Gemini API key",
    type="password",
    placeholder="Enter your private Gemini API key"
)

st.caption(
    "Your key is used for Gemini requests "
    "during this session. AgentFlow does not "
    "write it to a file or database. "
    "The key is processed by this hosted "
    "application, so use a separate "
    "restricted test key."
)

st.link_button(
    "Get a Gemini API Key",
    "https://aistudio.google.com/api-keys"
)


# ==========================================
# 5. USER INSTRUCTION
# ==========================================

st.header("5. Give Your Agent an Instruction")

user_instruction = st.text_area(
    "What would you like AgentFlow to do?",
    placeholder=(
        "Analyze my expenses using your tools. "
        "Identify the highest spending category. "
        "Propose a task and a summary note."
    ),
    max_chars=1000
)


# ==========================================
# RUN REAL GEMINI AGENT
# ==========================================

if st.button(
    "Run Real AI Agent"
):

    if csv_bytes is None:

        st.warning(
            "Please select a CSV file."
        )

    elif len(csv_bytes) > 1_000_000:

        st.error(
            "The maximum file size is 1 MB."
        )

    elif not api_key.strip():

        st.warning(
            "Enter your Gemini API key "
            "to use real AI functionality."
        )

    elif not user_instruction.strip():

        st.warning(
            "Please enter an instruction."
        )

    else:

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
                "Unable to analyze the CSV."
            )
            st.stop()

        st.session_state.agent_answer = None
        st.session_state.pending_tasks = []
        st.session_state.pending_notes = []

        try:

            with st.spinner(
                "Gemini is processing "
                "your request..."
            ):

                answer, tasks, notes = run_agent(
                    csv_bytes,
                    user_instruction,
                    api_key=api_key,
                    return_notes=True
                )

            st.session_state.agent_answer = answer
            st.session_state.pending_tasks = tasks
            st.session_state.pending_notes = notes

        except Exception:

            st.error(
                "The Gemini request failed. "
                "Check your API key, available "
                "quota, and model access."
            )


# ==========================================
# 6. AI RESPONSE
# ==========================================

if st.session_state.agent_answer:

    st.divider()

    st.header("6. AI Agent Response")

    st.markdown(
        st.session_state.agent_answer
    )

    st.caption(
        "The response describes the original "
        "proposals. Current approval status "
        "is shown below."
    )


# ==========================================
# 7. TASK APPROVAL
# ==========================================

if st.session_state.pending_tasks:

    st.divider()

    st.header("7. Pending Task Approval")

    st.warning(
        "Nothing has been saved yet."
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

                st.session_state.saved_tasks.append(
                    title
                )

                st.session_state.pending_tasks.pop(
                    index
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

                st.rerun()


# ==========================================
# 8. APPROVED TASKS
# ==========================================

st.divider()

st.header("8. Approved Tasks")

if st.session_state.saved_tasks:

    for index, title in enumerate(
        st.session_state.saved_tasks,
        start=1
    ):

        st.write(
            f"**#{index}** — {title}"
        )

else:

    st.info(
        "No approved tasks in this session."
    )


# ==========================================
# 9. NOTE APPROVAL
# ==========================================

if st.session_state.pending_notes:

    st.divider()

    st.header("9. Pending Note Approval")

    st.warning(
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

                st.session_state.saved_notes.append(
                    note.copy()
                )

                st.session_state.pending_notes.pop(
                    index
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

                st.rerun()


# ==========================================
# 10. APPROVED NOTES
# ==========================================

st.divider()

st.header("10. Approved Notes")

if st.session_state.saved_notes:

    for index, note in enumerate(
        st.session_state.saved_notes,
        start=1
    ):

        st.subheader(
            f"#{index} — {note['title']}"
        )

        st.write(
            note["content"]
        )

else:

    st.info(
        "No approved notes in this session."
    )


# ==========================================
# FOOTER
# ==========================================

st.divider()

st.caption(
    "AgentFlow is an independent portfolio "
    "demonstration of Gemini function calling, "
    "Python tools, and human-approved workflows. "
    "Approved records are temporary and "
    "specific to the current session."
)