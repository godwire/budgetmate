"""BudgetMate - an AI assistant for managing student finances (Streamlit app)."""
from datetime import date, datetime

import pandas as pd
import streamlit as st
from dotenv import load_dotenv

import database as db
from ai_advisor import get_savings_advice
from categorize import all_categories, categorize

load_dotenv()
db.init_db()

st.set_page_config(page_title="BudgetMate", page_icon="💰", layout="wide")

st.markdown(
    """
    <style>
    .stApp {
        background: linear-gradient(180deg, #f7fbff 0%, #eef4ff 100%);
    }
    .block-container {
        padding-top: 2rem;
        padding-bottom: 2rem;
    }
    div[data-testid="stMetric"] {
        background: rgba(255, 255, 255, 0.82);
        border: 1px solid #d9e7ff;
        border-radius: 18px;
        padding: 1rem;
        box-shadow: 0 8px 24px rgba(17, 54, 132, 0.08);
    }
    div[data-testid="stDataFrame"] {
        border-radius: 18px;
        overflow: hidden;
        box-shadow: 0 8px 24px rgba(17, 54, 132, 0.08);
    }
    </style>
    """,
    unsafe_allow_html=True,
)

st.title("💰 BudgetMate")
st.caption("AI-ассистент для управления финансами студента")

tab_add, tab_overview, tab_limits, tab_goals, tab_advice = st.tabs(
    ["➕ Добавить трату", "📊 Обзор", "🚧 Лимиты", "🎯 Цели", "🤖 AI-советы"]
)

# --- Add expense ---
with tab_add:
    st.subheader("Новая трата")
    with st.form("add_expense_form", clear_on_submit=True):
        col1, col2 = st.columns(2)
        amount = col1.number_input("Сумма (EUR)", min_value=0.0, step=0.5)
        expense_date = col2.date_input("Дата", value=date.today())
        description = st.text_input("Описание (например: 'кофе в Costa', 'Lidl')")

        suggested_category = categorize(description) if description else "Другое"
        categories = all_categories()
        category = st.selectbox(
            "Категория",
            options=categories,
            index=categories.index(suggested_category),
            help="Категория подобрана автоматически по описанию — можно поменять вручную.",
        )

        submitted = st.form_submit_button("Сохранить трату")
        if submitted:
            if amount <= 0:
                st.error("Сумма должна быть больше нуля.")
            else:
                db.add_expense(amount, category, description, expense_date.isoformat())
                st.success(f"Добавлено: {amount:.2f} EUR — {category}")

# --- Overview ---
with tab_overview:
    st.subheader("📊 Обзор расходов")
    expenses = db.get_expenses()

    if not expenses:
        st.info("Пока нет ни одной траты. Добавьте первую во вкладке '➕ Добавить трату'.")
    else:
        df = pd.DataFrame(expenses)
        df["date"] = pd.to_datetime(df["date"])

        category_options = ["Все категории"] + sorted(df["category"].dropna().unique().tolist())
        selected_category = st.selectbox(
            "Фильтр по категории",
            options=category_options,
            index=0,
            help="Выберите категорию, чтобы посмотреть только её траты.",
        )

        sort_mode = st.selectbox(
            "Сортировка списка трат",
            options=[
                "Сначала новые",
                "Сначала старые",
                "По сумме (макс → мин)",
                "По сумме (мин → макс)",
            ],
        )

        filtered_df = df.copy()
        if selected_category != "Все категории":
            filtered_df = filtered_df[filtered_df["category"] == selected_category]

        if sort_mode == "Сначала новые":
            filtered_df = filtered_df.sort_values("date", ascending=False)
        elif sort_mode == "Сначала старые":
            filtered_df = filtered_df.sort_values("date", ascending=True)
        elif sort_mode == "По сумме (макс → мин)":
            filtered_df = filtered_df.sort_values(["amount", "date"], ascending=[False, False])
        else:
            filtered_df = filtered_df.sort_values(["amount", "date"], ascending=[True, False])

        col1, col2, col3 = st.columns(3)
        col1.metric("Всего потрачено", f"{filtered_df['amount'].sum():.2f} EUR")
        col2.metric("Кол-во трат", len(filtered_df))
        col3.metric("Средняя трата", f"{filtered_df['amount'].mean():.2f} EUR")

        st.markdown("### 📈 По категориям")
        by_category = filtered_df.groupby("category")["amount"].sum().sort_values(ascending=False)
        st.bar_chart(by_category)

        st.markdown("### 📅 По времени")
        by_day = filtered_df.groupby(filtered_df["date"].dt.date)["amount"].sum()
        st.line_chart(by_day)

        st.markdown("### 🧾 Траты по выбранным параметрам")
        st.dataframe(
            filtered_df[["date", "amount", "category", "description"]].reset_index(drop=True),
            use_container_width=True,
            hide_index=True,
        )

# --- Limits ---
with tab_limits:
    st.subheader("Лимиты по категориям")

    with st.form("add_limit_form"):
        col1, col2 = st.columns(2)
        limit_category = col1.selectbox("Категория", options=all_categories())
        limit_amount = col2.number_input("Лимит (EUR/месяц)", min_value=0.0, step=5.0)
        if st.form_submit_button("Сохранить лимит"):
            db.add_or_update_limit(limit_category, limit_amount)
            st.success(f"Лимит для '{limit_category}' сохранён: {limit_amount:.2f} EUR/месяц")

    limits = db.get_limits()
    expenses = db.get_expenses()

    if limits:
        df = pd.DataFrame(expenses) if expenses else pd.DataFrame(columns=["amount", "category", "date"])
        st.markdown("**Прогресс по лимитам (текущий месяц)**")

        current_month = datetime.now().strftime("%Y-%m")
        for lim in limits:
            spent = 0.0
            if not df.empty:
                mask = (df["category"] == lim["category"]) & (
                    df["date"].astype(str).str.startswith(current_month)
                )
                spent = df.loc[mask, "amount"].sum()

            ratio = min(spent / lim["limit_amount"], 1.0) if lim["limit_amount"] > 0 else 0
            st.write(f"{lim['category']}: {spent:.2f} / {lim['limit_amount']:.2f} EUR")
            st.progress(ratio)
            if ratio >= 1.0:
                st.warning(f"Лимит по категории '{lim['category']}' превышен!")
    else:
        st.info("Лимиты ещё не заданы.")

# --- Goals ---
with tab_goals:
    st.subheader("Цели накоплений")

    with st.form("add_goal_form"):
        goal_name = st.text_input("Название цели (например: 'Поездка в Прагу')")
        col1, col2 = st.columns(2)
        target_amount = col1.number_input("Целевая сумма (EUR)", min_value=0.0, step=10.0)
        deadline = col2.date_input("Дедлайн")
        if st.form_submit_button("Добавить цель") and goal_name:
            db.add_goal(goal_name, target_amount, deadline.isoformat())
            st.success(f"Цель '{goal_name}' добавлена")

    goals = db.get_goals()
    if goals:
        st.markdown("**Прогресс по целям**")
        for goal in goals:
            days_left = (datetime.fromisoformat(goal["deadline"]).date() - date.today()).days
            ratio = (
                min(goal["saved_amount"] / goal["target_amount"], 1.0)
                if goal["target_amount"] > 0
                else 0
            )

            st.write(f"🎯 {goal['name']}: {goal['saved_amount']:.2f} / {goal['target_amount']:.2f} EUR")
            st.progress(ratio)

            if days_left > 0:
                remaining = max(goal["target_amount"] - goal["saved_amount"], 0)
                weekly_needed = remaining / max(days_left / 7, 1)
                st.caption(f"Осталось {days_left} дней. Нужно откладывать ~{weekly_needed:.2f} EUR в неделю.")
            else:
                st.caption("Дедлайн наступил.")

            new_saved = st.number_input(
                f"Обновить накопленную сумму для '{goal['name']}'",
                min_value=0.0,
                value=float(goal["saved_amount"]),
                step=5.0,
                key=f"goal_{goal['id']}",
            )
            if st.button("Обновить", key=f"update_{goal['id']}"):
                db.update_goal_progress(goal["id"], new_saved)
                st.rerun()
    else:
        st.info("Целей пока нет.")

# --- AI advice ---
with tab_advice:
    st.subheader("AI-советы по экономии")
    st.caption("Требуется ANTHROPIC_API_KEY в файле .env")

    if st.button("Получить совет"):
        expenses = db.get_expenses()
        df = pd.DataFrame(expenses) if expenses else pd.DataFrame(columns=["amount", "category", "date"])
        limits = db.get_limits()
        goals = db.get_goals()

        with st.spinner("Анализирую траты..."):
            advice = get_savings_advice(df, limits, goals)
        st.markdown(advice)
