"""SQLite database access for BudgetMate."""
import sqlite3
from pathlib import Path

DB_PATH = Path(__file__).parent / "budgetmate.db"


def get_connection():
    """Open a connection to the database."""
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn


def init_db():
    """Create tables if they don't exist yet."""
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS expenses (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            amount REAL NOT NULL,
            category TEXT NOT NULL,
            description TEXT,
            date TEXT NOT NULL
        )
    """)

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS limits (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            category TEXT NOT NULL UNIQUE,
            limit_amount REAL NOT NULL,
            period TEXT NOT NULL DEFAULT 'monthly'
        )
    """)

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS goals (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            target_amount REAL NOT NULL,
            deadline TEXT NOT NULL,
            saved_amount REAL NOT NULL DEFAULT 0
        )
    """)

    conn.commit()
    conn.close()


def add_expense(amount, category, description, expense_date):
    """Insert a new expense row."""
    conn = get_connection()
    conn.execute(
        "INSERT INTO expenses (amount, category, description, date) VALUES (?, ?, ?, ?)",
        (amount, category, description, expense_date),
    )
    conn.commit()
    conn.close()


def get_expenses():
    """Return all expenses as a list of dicts, newest first."""
    conn = get_connection()
    rows = conn.execute("SELECT * FROM expenses ORDER BY date DESC").fetchall()
    conn.close()
    return [dict(row) for row in rows]


def add_or_update_limit(category, limit_amount, period="monthly"):
    """Create a limit for a category, or update it if one already exists."""
    conn = get_connection()
    conn.execute(
        """
        INSERT INTO limits (category, limit_amount, period)
        VALUES (?, ?, ?)
        ON CONFLICT(category) DO UPDATE SET
            limit_amount = excluded.limit_amount,
            period = excluded.period
        """,
        (category, limit_amount, period),
    )
    conn.commit()
    conn.close()


def get_limits():
    """Return all category limits."""
    conn = get_connection()
    rows = conn.execute("SELECT * FROM limits").fetchall()
    conn.close()
    return [dict(row) for row in rows]


def add_goal(name, target_amount, deadline):
    """Create a new savings goal."""
    conn = get_connection()
    conn.execute(
        "INSERT INTO goals (name, target_amount, deadline, saved_amount) VALUES (?, ?, ?, 0)",
        (name, target_amount, deadline),
    )
    conn.commit()
    conn.close()


def update_goal_progress(goal_id, saved_amount):
    """Update how much has been saved toward a goal."""
    conn = get_connection()
    conn.execute("UPDATE goals SET saved_amount = ? WHERE id = ?", (saved_amount, goal_id))
    conn.commit()
    conn.close()


def get_goals():
    """Return all savings goals."""
    conn = get_connection()
    rows = conn.execute("SELECT * FROM goals").fetchall()
    conn.close()
    return [dict(row) for row in rows]
