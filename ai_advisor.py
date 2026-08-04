"""Generate savings advice using the Claude API."""
import os

import pandas as pd

try:
    import anthropic
except ImportError:
    anthropic = None

MODEL = "claude-sonnet-5"


def _build_summary(expenses_df: pd.DataFrame, limits: list[dict], goals: list[dict]) -> str:
    """Build a plain-text summary of expenses, limits and goals for the prompt."""
    if expenses_df.empty:
        return "No expenses recorded yet."

    by_category = (
        expenses_df.groupby("category")["amount"]
        .sum()
        .sort_values(ascending=False)
    )

    lines = ["Spending by category (all time):"]
    for category, total in by_category.items():
        lines.append(f"- {category}: {total:.2f} EUR")

    if limits:
        lines.append("\nLimits:")
        for lim in limits:
            spent = expenses_df.loc[expenses_df["category"] == lim["category"], "amount"].sum()
            lines.append(
                f"- {lim['category']}: limit {lim['limit_amount']:.2f} EUR "
                f"({lim['period']}), spent {spent:.2f} EUR"
            )

    if goals:
        lines.append("\nSavings goals:")
        for goal in goals:
            lines.append(
                f"- {goal['name']}: target {goal['target_amount']:.2f} EUR by {goal['deadline']}, "
                f"saved so far {goal['saved_amount']:.2f} EUR"
            )

    return "\n".join(lines)


def get_savings_advice(expenses_df: pd.DataFrame, limits: list[dict], goals: list[dict]) -> str:
    """Ask Claude for 2-3 concrete savings tips based on the user's expense data.

    Requires the ANTHROPIC_API_KEY environment variable to be set.
    """
    if anthropic is None:
        return "Пакет 'anthropic' не установлен. Выполните: pip install anthropic"

    api_key = os.environ.get("ANTHROPIC_API_KEY")
    if not api_key:
        return "Не найден ANTHROPIC_API_KEY. Добавьте его в файл .env, чтобы получать AI-советы."

    summary = _build_summary(expenses_df, limits, goals)

    client = anthropic.Anthropic(api_key=api_key)
    message = client.messages.create(
        model=MODEL,
        max_tokens=500,
        messages=[
            {
                "role": "user",
                "content": (
                    "Ты — финансовый ассистент для студента. Вот сводка его трат, "
                    "лимитов и целей накоплений:\n\n"
                    f"{summary}\n\n"
                    "Дай 2-3 конкретных, практичных совета по экономии на основе "
                    "этих данных. Используй реальные цифры из сводки в каждом совете. "
                    "Пиши коротко, по делу, без общих фраз вроде 'трать меньше'. "
                    "Отвечай на русском языке."
                ),
            }
        ],
    )

    return message.content[0].text
