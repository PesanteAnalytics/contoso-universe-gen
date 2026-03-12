"""
Contoso Universe Generator — i18n Locale Registry
Maps language codes to Faker locales and metadata.
"""

from dataclasses import dataclass


@dataclass(frozen=True)
class LocaleInfo:
    code: str          # ISO 639-1 (e.g. "en")
    faker_locale: str  # Faker locale string
    display_name: str  # Human-readable
    country_default: str  # Default ISO 3166-1 alpha-2 country for holidays


LOCALE_MAP: dict[str, LocaleInfo] = {
    "en": LocaleInfo("en", "en_US", "English",    "US"),
    "es": LocaleInfo("es", "es_MX", "Español",    "MX"),
    "pt": LocaleInfo("pt", "pt_BR", "Português",  "BR"),
    "fr": LocaleInfo("fr", "fr_FR", "Français",   "FR"),
    "de": LocaleInfo("de", "de_DE", "Deutsch",    "DE"),
    "zh": LocaleInfo("zh", "zh_CN", "中文",        "CN"),
    "ja": LocaleInfo("ja", "ja_JP", "日本語",      "JP"),
    "ar": LocaleInfo("ar", "ar_AA", "العربية",    "SA"),
}


def get_locale(language: str) -> LocaleInfo:
    """Return LocaleInfo for the given language code.
    Falls back to English if the language code is unknown.
    """
    return LOCALE_MAP.get(language, LOCALE_MAP["en"])


def list_locales() -> list[LocaleInfo]:
    """Return all supported locales sorted by code."""
    return sorted(LOCALE_MAP.values(), key=lambda l: l.code)
