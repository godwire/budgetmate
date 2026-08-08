# BudgetMate

An AI-powered personal finance assistant for students. BudgetMate helps you track expenses, automatically categorize them, set spending limits, define savings goals, and get personalized money-saving advice powered by Claude.

## Features

- **Expense tracking** — log your spending as you go
- **Automatic categorization** — expenses are sorted into categories based on keywords
- **Spending limits** — set a budget per category and keep an eye on it
- **Savings goals** — define goals and track your progress toward them
- **AI savings advice** — get personalized tips based on your real spending data, powered by the Claude API

## Getting Started (VS Code)

### 1. Open the project
Open the `budgetmate` folder in VS Code: **File → Open Folder**.

### 2. Create and activate a virtual environment
Open a terminal in VS Code (**Terminal → New Terminal**) and run:

```bash
python -m venv .venv
```

Then activate it:

**Windows**
```bash
.venv\Scripts\activate
```

**macOS / Linux**
```bash
source .venv/bin/activate
```

> If VS Code doesn't automatically detect the virtual environment, click the Python version shown in the bottom-right corner and select the interpreter from `.venv`.

### 3. Install dependencies

```bash
pip install -r requirements.txt
```

### 4. (Optional) Set up the AI Advice tab
To use the AI-powered savings advice tab, create a `.env` file next to `app.py`, based on `.env.example`, and add your Anthropic API key:

```
ANTHROPIC_API_KEY=sk-ant-...
```

Without this key, the rest of the app (expenses, categories, limits, goals) still works normally — the AI Advice tab will simply show a message that no key was found.

### 5. Run the app

```bash
streamlit run app.py
```

Your browser will open automatically at `http://localhost:8501`. A SQLite database file, `budgetmate.db`, is created automatically in the project folder on first run.

## Project Structure

| File | Description |
|---|---|
| `app.py` | Streamlit interface (5 tabs: Add Expense, Overview, Limits, Goals, AI Advice) |
| `database.py` | SQLite database logic (`expenses`, `limits`, `goals` tables) |
| `categorize.py` | Automatic expense categorization based on keywords |
| `ai_advisor.py` | Builds a spending summary and requests advice from the Claude API |

## Ideas for the Future

- Import expenses from a bank CSV statement
- Smarter categorization (ML classifier instead of keyword matching)
- Map view of spending locations
- Price comparison across stores to find the best deals
