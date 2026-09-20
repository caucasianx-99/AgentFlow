
# AgentFlow

### AI Agent with Function Calling & Workflow Automation

AgentFlow is a Python-based AI application that combines natural-language instructions, Gemini function calling, CSV data analysis, and human-approved workflow automation.

The project demonstrates how an AI agent can interact with real Python tools and structured data while keeping users in control of database-changing actions.

## Features

- Natural-language instructions through a Streamlit interface
- CSV upload and expense analysis
- Gemini AI integration
- Python function calling
- Spending calculations using pandas
- AI-generated task proposals
- AI-generated note proposals
- Explicit approval and rejection workflows
- Persistent task and note storage using SQLite
- CSV input validation
- Automated tests using pytest

## Example Workflow

A user uploads an expenses CSV and enters:

"Analyze my expenses, identify the highest spending category, propose a task to review it, and prepare a summary note."

AgentFlow:

1. Interprets the instruction using Gemini.
2. Calls a Python expense-analysis function.
3. Calculates category totals using pandas.
4. Generates an explanation based on the calculated results.
5. Proposes a follow-up task and summary note.
6. Waits for explicit user approval.
7. Saves only approved records to SQLite.

The AI model cannot directly execute the database-writing functions.

## Technology Stack

- Python
- Google Gemini API
- Google Gen AI Python SDK
- Streamlit
- pandas
- SQLite
- python-dotenv
- pytest

## Project Structure

```text
AgentFlow/
|
|-- agent.py
|-- app.py
|-- main.py
|-- task_store.py
|-- note_store.py
|-- manual_gemini.py
|-- sample_expenses.csv
|-- requirements.txt
|-- .env.example
|-- .gitignore
|-- README.md
|
`-- tests/
    |-- test_main.py
    `-- test_stores.py
```

## Installation

The project was developed and tested on Windows using Python 3.14.

Clone the repository and open the project folder.

Create a virtual environment:

```powershell
py -m venv .venv
```

Install dependencies:

```powershell
.\.venv\Scripts\python.exe -m pip install -r requirements.txt
```

Create a local environment file from the example:

```powershell
Copy-Item .env.example .env
```

Add your Gemini API key to `.env`:

```dotenv
GEMINI_API_KEY=your_private_api_key
```

Never commit your real API key to GitHub.

## Run the Application

Start Streamlit:

```powershell
.\.venv\Scripts\python.exe -m streamlit run app.py
```

Open the local URL displayed in the terminal.

Upload `sample_expenses.csv` and enter an instruction.

## Sample Dataset

The repository includes a fictional expenses CSV for demonstration purposes.

Expected results:

| Category | Spending |
|---|---:|
| Shopping | 200.00 |
| Food | 114.00 |
| Utilities | 77.00 |
| Transport | 17.00 |

Total spending: 408.00

Total transactions: 10

Highest spending category: Shopping

The sample dataset does not specify a currency.

## Automated Tests

Run the complete test suite:

```powershell
.\.venv\Scripts\python.exe -m pytest -q
```

The test suite covers:

- Correct expense calculations
- CSV bytes processing
- Invalid CSV input
- Missing required columns
- Missing categories
- Invalid and negative amounts
- SQLite task persistence
- SQLite note persistence
- Invalid task and note rejection

The database tests use temporary SQLite databases and do not modify the local application database.

The AI integration and approval interface were also tested manually.

## Security and Approval

AgentFlow separates AI-generated proposals from database-writing operations.

The AI model can propose tasks and notes, but cannot directly save them.

Only an explicit user approval action triggers a database write.

API credentials are loaded from a private environment file.

The local SQLite database and environment credentials are excluded from version control.

## Project Scope

AgentFlow is a local portfolio demonstration of custom AI-agent development.

It is not a general-purpose autonomous agent, a trained foundation model, or a production-ready financial application.

The application uses an existing Gemini model and custom Python business logic.

The project uses fictional sample data. Real confidential client data should not be submitted without appropriate authorization and privacy arrangements.

Gemini API availability, free-tier limits, and costs depend on the provider and account configuration.

## Freelance Application

AgentFlow demonstrates transferable skills for building client-specific AI applications, including:

- AI agent development
- Function calling and tool integration
- Data analysis workflows
- Human-in-the-loop automation
- Database integration
- Custom Python applications

Client projects can be designed around different authorized datasets, APIs, and workflows rather than using AgentFlow as a fixed product.