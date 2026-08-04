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

CATEGORY_ICONS = {
    "Еда вне дома": "🍔",
    "Продукты": "🛒",
    "Транспорт": "🚌",
    "Жильё": "🏠",
    "Развлечения": "🎬",
    "Здоровье": "💊",
    "Образование": "📚",
    "Одежда": "👕",
    "Другое": "🧾",
}


def icon_for(category: str) -> str:
    """Return the emoji icon for a category, falling back to a generic receipt."""
    return CATEGORY_ICONS.get(category, "🧾")


st.markdown(
    """
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700;800&display=swap');

    html, body, [class*="css"] {
        font-family: 'Inter', -apple-system, BlinkMacSystemFont, 'Segoe UI', sans-serif;
    }

    :root {
        --bm-primary: #6C5CE7;
        --bm-primary-dark: #4834d4;
        --bm-success: #00b894;
        --bm-warning: #e1a100;
        --bm-danger: #e74c3c;
        --bm-text: #1e1b3a;
        --bm-muted: #6b7280;
    }

    .stApp {
        background: radial-gradient(circle at 0% 0%, #f1ecff 0%, #f7fbff 35%, #eef4ff 100%);
    }

    .block-container {
        padding-top: 1.5rem;
        padding-bottom: 3rem;
        max-width: 1200px;
    }

    /* Hero header */
    .bm-hero {
        display: flex;
        align-items: center;
        gap: 1rem;
        padding: 1.5rem 2rem;
        margin-bottom: 1.5rem;
        border-radius: 24px;
        background: linear-gradient(120deg, #6C5CE7 0%, #a29bfe 100%);
        box-shadow: 0 16px 40px rgba(108, 92, 231, 0.35);
        color: white;
    }
    .bm-hero-icon { font-size: 2.6rem; line-height: 1; }
    .bm-hero-title { font-size: 1.9rem; font-weight: 800; margin: 0; letter-spacing: -0.02em; }
    .bm-hero-caption { margin: 0.2rem 0 0 0; opacity: 0.92; font-size: 0.98rem; }

    /* Tabs as pills */
    .stTabs [data-baseweb="tab-list"] {
        gap: 6px;
        background: rgba(255,255,255,0.6);
        padding: 6px;
        border-radius: 16px;
        border: 1px solid #e3e8f5;
    }
    .stTabs [data-baseweb="tab"] {
        border-radius: 12px;
        padding: 8px 16px;
        font-weight: 600;
        color: var(--bm-muted);
    }
    .stTabs [aria-selected="true"] {
        background: var(--bm-primary) !important;
        color: white !important;
        box-shadow: 0 6px 14px rgba(108, 92, 231, 0.35);
    }

    /* Metrics */
    div[data-testid="stMetric"] {
        background: rgba(255, 255, 255, 0.85);
        border: 1px solid #e3e8f5;
        border-radius: 18px;
        padding: 1.1rem 1.2rem;
        box-shadow: 0 8px 24px rgba(17, 54, 132, 0.06);
    }
    div[data-testid="stMetricLabel"] { font-weight: 600; color: var(--bm-muted); }
    div[data-testid="stMetricValue"] { color: var(--bm-text); }

    /* Dataframe */
    div[data-testid="stDataFrame"] {
        border-radius: 18px;
        overflow: hidden;
        border: 1px solid #e3e8f5;
        box-shadow: 0 8px 24px rgba(17, 54, 132, 0.06);
    }

    /* Cards */
    .bm-card {
        background: rgba(255, 255, 255, 0.9);
        border: 1px solid #e3e8f5;
        border-radius: 18px;
        padding: 1.1rem 1.3rem;
        margin-bottom: 0.9rem;
        box-shadow: 0 8px 24px rgba(17, 54, 132, 0.06);
    }
    .bm-card-title { font-weight: 700; font-size: 1.02rem; color: var(--bm-text); margin-bottom: 0.15rem; }
    .bm-card-row { display: flex; justify-content: space-between; align-items: baseline; }
    .bm-card-amount { font-weight: 600; color: var(--bm-muted); font-size: 0.92rem; }
    .bm-card-sub { color: var(--bm-muted); font-size: 0.85rem; margin-top: 0.4rem; }
    .bm-card-warning { color: var(--bm-danger); font-weight: 600; font-size: 0.88rem; margin-top: 0.4rem; }

    /* Progress bar */
    .bm-progress-track {
        width: 100%;
        height: 12px;
        border-radius: 999px;
        background: #eef0f7;
        overflow: hidden;
        margin-top: 0.5rem;
    }
    .bm-progress-fill { height: 100%; border-radius: 999px; transition: width 0.4s ease; }

    /* Buttons */
    .stButton > button, .stFormSubmitButton > button {
        border-radius: 12px;
        font-weight: 600;
        border: none;
        background: linear-gradient(120deg, #6C5CE7 0%, #4834d4 100%);
        color: white;
        box-shadow: 0 6px 16px rgba(108, 92, 231, 0.3);
        transition: transform 0.15s ease;
    }
    .stButton > button:hover, .stFormSubmitButton > button:hover {
        transform: translateY(-1px);
        color: white;
    }

    /* Sidebar */
    section[data-testid="stSidebar"] {
        background: linear-gradient(180deg, #1e1b3a 0%, #2d2467 100%);
    }
    section[data-testid="stSidebar"] * { color: #f1ecff !important; }
    section[data-testid="stSidebar"] div[data-testid="stMetric"] {
        background: rgba(255,255,255,0.08);
        border: 1px solid rgba(255,255,255,0.12);
    }
    </style>
    """,
    unsafe_allow_html=True,
)


def render_progress_bar(ratio: float) -> str:
    """Build an HTML progress bar, colored by how close ratio is to 1.0."""
    pct = max(0.0, min(ratio, 1.0)) * 100
    if ratio >= 1.0:
        color = "var(--bm-danger)"
    elif ratio >= 0.75:
        color = "var(--bm-warning)"
    else:
        color = "var(--bm-success)"
    return (
        f'<div class="bm-progress-track">'
        f'<div class="bm-progress-fill" style="width:{pct:.1f}%; background:{color};"></div>'
        f"</div>"
    )


# --- Sidebar: quick stats ---
with st.sidebar:
    st.markdown("## 💰 BudgetMate")
    st.caption("AI-ассистент для управления финансами")
    st.markdown("---")

    all_expenses = db.get_expenses()
    if all_expenses:
        sidebar_df = pd.DataFrame(all_expenses)
        sidebar_df["date"] = pd.to_datetime(sidebar_df["date"])
        current_month_str = datetime.now().strftime("%Y-%m")
        month_mask = sidebar_df["date"].dt.strftime("%Y-%m") == current_month_str
        month_total = sidebar_df.loc[month_mask, "amount"].sum()
        st.metric("Потрачено в этом месяце", f"{month_total:.2f} EUR")
        st.metric("Всего записей", len(sidebar_df))
    else:
        st.info("Пока нет данных о тратах.")

    st.markdown("---")
    st.markdown(f"🎯 Активных целей: **{len(db.get_goals())}**")
    st.markdown(f"🚧 Заданных лимитов: **{len(db.get_limits())}**")

# --- Hero header ---
st.markdown(
    """
    <div class="bm-hero">
        <div class="bm-hero-icon">💰</div>
        <div>
            <p class="bm-hero-title">BudgetMate</p>
            <p class="bm-hero-caption">AI-ассистент для управления финансами студента</p>
        </div>
    </div>
    """,
    unsafe_allow_html=True,
)

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
            format_func=lambda c: f"{icon_for(c)} {c}",
            help="Категория подобрана автоматически по описанию — можно поменять вручную.",
        )

        submitted = st.form_submit_button("💾 Сохранить трату")
        if submitted:
            if amount <= 0:
                st.error("Сумма должна быть больше нуля.")
            else:
                db.add_expense(amount, category, description, expense_date.isoformat())
                st.success(f"{icon_for(category)} Добавлено: {amount:.2f} EUR — {category}")

# --- Overview ---
with tab_overview:
    st.subheader("📊 Обзор расходов")
    expenses = db.get_expenses()

    if not expenses:
        st.info("Пока нет ни одной траты. Добавьте первую во вкладке '➕ Добавить трату'.")
    else:
        df = pd.DataFrame(expenses)
        df["date"] = pd.to_datetime(df["date"])

        search_col, category_col, sort_col = st.columns([1.3, 1, 1])
        search_query = search_col.text_input(
            "🔍 Поиск по транзакциям",
            placeholder="Например: 'кофе' или 'Lidl'",
            help="Ищет совпадения в описании и категории траты.",
        )

        category_options = ["Все категории"] + sorted(df["category"].dropna().unique().tolist())
        selected_category = category_col.selectbox(
            "Фильтр по категории",
            options=category_options,
            index=0,
            format_func=lambda c: c if c == "Все категории" else f"{icon_for(c)} {c}",
            help="Выберите категорию, чтобы посмотреть только её траты.",
        )

        sort_mode = sort_col.selectbox(
            "Сортировка списка трат",
            options=[
                "Сначала новые",
                "Сначала старые",
                "По сумме (макс → мин)",
                "По сумме (мин → макс)",
                "По алфавиту (А → Я)",
                "По алфавиту (Я → А)",
            ],
        )

        filtered_df = df.copy()
        if selected_category != "Все категории":
            filtered_df = filtered_df[filtered_df["category"] == selected_category]

        if search_query:
            query = search_query.strip().lower()
            match_mask = (
                filtered_df["description"].fillna("").str.lower().str.contains(query, regex=False)
                | filtered_df["category"].fillna("").str.lower().str.contains(query, regex=False)
            )
            filtered_df = filtered_df[match_mask]

        if sort_mode == "Сначала новые":
            filtered_df = filtered_df.sort_values("date", ascending=False)
        elif sort_mode == "Сначала старые":
            filtered_df = filtered_df.sort_values("date", ascending=True)
        elif sort_mode == "По сумме (макс → мин)":
            filtered_df = filtered_df.sort_values(["amount", "date"], ascending=[False, False])
        elif sort_mode == "По сумме (мин → макс)":
            filtered_df = filtered_df.sort_values(["amount", "date"], ascending=[True, False])
        elif sort_mode == "По алфавиту (А → Я)":
            filtered_df = filtered_df.sort_values(
                "description", key=lambda col: col.fillna("").str.lower(), ascending=True
            )
        else:
            filtered_df = filtered_df.sort_values(
                "description", key=lambda col: col.fillna("").str.lower(), ascending=False
            )

        if filtered_df.empty:
            st.warning("Ничего не найдено. Попробуйте изменить поиск или фильтр по категории.")
        else:
            col1, col2, col3 = st.columns(3)
            col1.metric("💶 Всего потрачено", f"{filtered_df['amount'].sum():.2f} EUR")
            col2.metric("🧾 Кол-во трат", len(filtered_df))
            col3.metric("📐 Средняя трата", f"{filtered_df['amount'].mean():.2f} EUR")

            st.markdown("### 📈 По категориям")
            by_category = filtered_df.groupby("category")["amount"].sum().sort_values(ascending=False)
            st.bar_chart(by_category, color="#6C5CE7")

            st.markdown("### 📅 По времени")
            by_day = filtered_df.groupby(filtered_df["date"].dt.date)["amount"].sum()
            st.line_chart(by_day, color="#6C5CE7")

            st.markdown("### 🧾 Траты по выбранным параметрам")
            table_df = filtered_df[["date", "amount", "category", "description"]].reset_index(drop=True)
            table_df["category"] = table_df["category"].apply(lambda c: f"{icon_for(c)} {c}")
            st.dataframe(
                table_df,
                use_container_width=True,
                hide_index=True,
                column_config={
                    "date": st.column_config.DateColumn("Дата", format="DD.MM.YYYY"),
                    "amount": st.column_config.NumberColumn("Сумма", format="%.2f EUR"),
                    "category": st.column_config.TextColumn("Категория"),
                    "description": st.column_config.TextColumn("Описание"),
                },
            )

# --- Limits ---
with tab_limits:
    st.subheader("Лимиты по категориям")

    with st.form("add_limit_form"):
        col1, col2 = st.columns(2)
        limit_category = col1.selectbox(
            "Категория", options=all_categories(), format_func=lambda c: f"{icon_for(c)} {c}"
        )
        limit_amount = col2.number_input("Лимит (EUR/месяц)", min_value=0.0, step=5.0)
        if st.form_submit_button("💾 Сохранить лимит"):
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
            warning_html = (
                f'<div class="bm-card-warning">⚠️ Лимит по категории «{lim["category"]}» превышен!</div>'
                if ratio >= 1.0
                else ""
            )
            st.markdown(
                f"""
                <div class="bm-card">
                    <div class="bm-card-row">
                        <div class="bm-card-title">{icon_for(lim['category'])} {lim['category']}</div>
                        <div class="bm-card-amount">{spent:.2f} / {lim['limit_amount']:.2f} EUR</div>
                    </div>
                    {render_progress_bar(ratio)}
                    {warning_html}
                </div>
                """,
                unsafe_allow_html=True,
            )
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
        if st.form_submit_button("🎯 Добавить цель") and goal_name:
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

            if days_left > 0:
                remaining = max(goal["target_amount"] - goal["saved_amount"], 0)
                weekly_needed = remaining / max(days_left / 7, 1)
                deadline_note = f"Осталось {days_left} дней. Нужно откладывать ~{weekly_needed:.2f} EUR в неделю."
            else:
                deadline_note = "Дедлайн наступил."

            st.markdown(
                f"""
                <div class="bm-card">
                    <div class="bm-card-row">
                        <div class="bm-card-title">🎯 {goal['name']}</div>
                        <div class="bm-card-amount">{goal['saved_amount']:.2f} / {goal['target_amount']:.2f} EUR</div>
                    </div>
                    {render_progress_bar(ratio)}
                    <div class="bm-card-sub">{deadline_note}</div>
                </div>
                """,
                unsafe_allow_html=True,
            )

            gcol1, gcol2 = st.columns([3, 1])
            new_saved = gcol1.number_input(
                f"Обновить накопленную сумму для '{goal['name']}'",
                min_value=0.0,
                value=float(goal["saved_amount"]),
                step=5.0,
                key=f"goal_{goal['id']}",
                label_visibility="collapsed",
            )
            if gcol2.button("Обновить", key=f"update_{goal['id']}"):
                db.update_goal_progress(goal["id"], new_saved)
                st.rerun()
    else:
        st.info("Целей пока нет.")

# --- AI advice ---
with tab_advice:
    st.subheader("🤖 AI-советы по экономии")
    st.caption("Требуется ANTHROPIC_API_KEY в файле .env")

    if st.button("✨ Получить совет"):
        expenses = db.get_expenses()
        df = pd.DataFrame(expenses) if expenses else pd.DataFrame(columns=["amount", "category", "date"])
        limits = db.get_limits()
        goals = db.get_goals()

        with st.spinner("Анализирую траты..."):
            advice = get_savings_advice(df, limits, goals)

        st.markdown(f'<div class="bm-card">{advice}</div>', unsafe_allow_html=True)
