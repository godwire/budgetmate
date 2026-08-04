"""Automatic expense categorization by keywords."""

# Category -> list of keywords (matched in the expense description, Russian
# since that's the language the user will type descriptions in).
CATEGORY_KEYWORDS = {
    "Еда вне дома": ["кофе", "кафе", "ресторан", "starbucks", "mcdonald", "kfc", "бар", "пицц"],
    "Продукты": ["lidl", "kaufland", "tesco", "billa", "coop", "супермаркет", "продукт"],
    "Транспорт": ["такси", "bolt", "uber", "автобус", "метро", "бензин", "парковка", "проездной"],
    "Жильё": ["аренда", "квартир", "коммунал", "интернет", "электричество"],
    "Развлечения": ["кино", "netflix", "spotify", "концерт", "игр", "подписк"],
    "Здоровье": ["аптека", "врач", "стоматолог", "клиник"],
    "Образование": ["книг", "курс", "учебник", "универ"],
    "Одежда": ["zara", "h&m", "reserved", "одежд", "обув"],
}

DEFAULT_CATEGORY = "Другое"


def categorize(description: str) -> str:
    """Guess a category from a free-text expense description.

    Looks for keywords from CATEGORY_KEYWORDS in the description
    (case-insensitive). Returns DEFAULT_CATEGORY if nothing matches.
    """
    if not description:
        return DEFAULT_CATEGORY

    text = description.lower()
    for category, keywords in CATEGORY_KEYWORDS.items():
        for keyword in keywords:
            if keyword in text:
                return category
    return DEFAULT_CATEGORY


def all_categories() -> list[str]:
    """Return every known category plus the default 'Other' bucket."""
    return list(CATEGORY_KEYWORDS.keys()) + [DEFAULT_CATEGORY]
