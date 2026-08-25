"""
Currency Generator — DimCurrency table.
"""

from __future__ import annotations

import polars as pl

# ─── Static currency catalogue ──────────────────────────────────────────────

_CURRENCIES: list[dict] = [
    {"CurrencyKey": 1, "CurrencyCode": "USD", "CurrencyName": "US Dollar",        "Symbol": "$",  "Language": "en"},
    {"CurrencyKey": 2, "CurrencyCode": "EUR", "CurrencyName": "Euro",             "Symbol": "€",  "Language": "fr"},
    {"CurrencyKey": 3, "CurrencyCode": "GBP", "CurrencyName": "British Pound",    "Symbol": "£",  "Language": "en"},
    {"CurrencyKey": 4, "CurrencyCode": "CAD", "CurrencyName": "Canadian Dollar",  "Symbol": "CA$","Language": "en"},
    {"CurrencyKey": 5, "CurrencyCode": "AUD", "CurrencyName": "Australian Dollar","Symbol": "A$", "Language": "en"},
    {"CurrencyKey": 6, "CurrencyCode": "MXN", "CurrencyName": "Mexican Peso",     "Symbol": "$",  "Language": "es"},
    {"CurrencyKey": 7, "CurrencyCode": "BRL", "CurrencyName": "Brazilian Real",   "Symbol": "R$", "Language": "pt"},
    {"CurrencyKey": 8, "CurrencyCode": "ARS", "CurrencyName": "Argentine Peso",   "Symbol": "$",  "Language": "es"},
    {"CurrencyKey": 9, "CurrencyCode": "COP", "CurrencyName": "Colombian Peso",   "Symbol": "$",  "Language": "es"},
    {"CurrencyKey":10, "CurrencyCode": "CLP", "CurrencyName": "Chilean Peso",     "Symbol": "$",  "Language": "es"},
    {"CurrencyKey":11, "CurrencyCode": "JPY", "CurrencyName": "Japanese Yen",     "Symbol": "¥",  "Language": "ja"},
    {"CurrencyKey":12, "CurrencyCode": "CNY", "CurrencyName": "Chinese Yuan",     "Symbol": "¥",  "Language": "zh"},
    {"CurrencyKey":13, "CurrencyCode": "INR", "CurrencyName": "Indian Rupee",     "Symbol": "₹",  "Language": "hi"},
    {"CurrencyKey":14, "CurrencyCode": "AED", "CurrencyName": "UAE Dirham",       "Symbol": "د.إ","Language": "ar"},
    {"CurrencyKey":15, "CurrencyCode": "SAR", "CurrencyName": "Saudi Riyal",      "Symbol": "ر.س","Language": "ar"},
    {"CurrencyKey":16, "CurrencyCode": "CHF", "CurrencyName": "Swiss Franc",      "Symbol": "CHF","Language": "de"},
    {"CurrencyKey":17, "CurrencyCode": "SEK", "CurrencyName": "Swedish Krona",    "Symbol": "kr", "Language": "sv"},
    {"CurrencyKey":18, "CurrencyCode": "NOK", "CurrencyName": "Norwegian Krone",  "Symbol": "kr", "Language": "no"},
    {"CurrencyKey":19, "CurrencyCode": "DKK", "CurrencyName": "Danish Krone",     "Symbol": "kr", "Language": "da"},
    {"CurrencyKey":20, "CurrencyCode": "PLN", "CurrencyName": "Polish Zloty",     "Symbol": "zł", "Language": "pl"},
    {"CurrencyKey":21, "CurrencyCode": "KRW", "CurrencyName": "South Korean Won", "Symbol": "₩",  "Language": "ko"},
    {"CurrencyKey":22, "CurrencyCode": "SGD", "CurrencyName": "Singapore Dollar", "Symbol": "S$", "Language": "en"},
    {"CurrencyKey":23, "CurrencyCode": "HKD", "CurrencyName": "Hong Kong Dollar", "Symbol": "HK$","Language": "zh"},
    {"CurrencyKey":24, "CurrencyCode": "TRY", "CurrencyName": "Turkish Lira",     "Symbol": "₺",  "Language": "tr"},
    {"CurrencyKey":25, "CurrencyCode": "ZAR", "CurrencyName": "South African Rand","Symbol": "R", "Language": "en"},
]

# Language-to-primary-currency mapping
LANGUAGE_CURRENCY_MAP: dict[str, str] = {
    "en": "USD",
    "es": "MXN",
    "pt": "BRL",
    "fr": "EUR",
    "de": "EUR",
    "zh": "CNY",
    "ja": "JPY",
    "ar": "AED",
}


def generate_dim_currency() -> pl.DataFrame:
    """Return the full DimCurrency static catalogue as a Polars DataFrame."""
    return pl.DataFrame(_CURRENCIES, schema={
        "CurrencyKey":  pl.Int32,
        "CurrencyCode": pl.String,
        "CurrencyName": pl.String,
        "Symbol":       pl.String,
        "Language":     pl.String,
    })


def get_currency_key(language: str) -> int:
    """Return the primary CurrencyKey for a given language."""
    code = LANGUAGE_CURRENCY_MAP.get(language, "USD")
    for c in _CURRENCIES:
        if c["CurrencyCode"] == code:
            return c["CurrencyKey"]
    return 1  # fallback USD
