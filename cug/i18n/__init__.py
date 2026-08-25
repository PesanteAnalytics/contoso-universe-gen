"""cug.i18n — Internationalization package."""
from .locales import LocaleInfo, LOCALE_MAP, get_locale, list_locales, locale_coverage

__all__ = ["LocaleInfo", "LOCALE_MAP", "get_locale", "list_locales", "locale_coverage"]
