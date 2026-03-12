"""
Smoke tests — fast checks for all core modules.
Run: pytest tests/ -v
"""

import pytest
import polars as pl
from pathlib import Path


# ─── Config ──────────────────────────────────────────────────────────────────

def test_default_config_loads():
    from cug.config import load_config
    cfg = load_config()
    assert cfg.general.language == "en"
    assert cfg.output.target_orders > 0


def test_config_override():
    from cug.config import load_config, AppConfig
    cfg = load_config()
    cfg.general.language = "es"
    cfg.output.target_orders = 1000
    assert cfg.general.language == "es"
    assert cfg.output.target_orders == 1000


# ─── i18n ────────────────────────────────────────────────────────────────────

def test_locale_map_has_8_languages():
    from cug.i18n import LOCALE_MAP
    assert len(LOCALE_MAP) >= 8


def test_get_locale_en():
    from cug.i18n import get_locale
    loc = get_locale("en")
    assert loc.faker_locale == "en_US"


def test_get_locale_unknown_falls_back():
    from cug.i18n import get_locale
    loc = get_locale("xx")
    assert loc.code == "en"


# ─── Category system ─────────────────────────────────────────────────────────

def test_builtin_categories_load():
    from cug.categories.registry import CategoryRegistry
    reg = CategoryRegistry()
    reg.load_builtins()
    assert len(reg) >= 1


def test_electronics_plugin():
    from cug.categories.registry import CategoryRegistry
    reg = CategoryRegistry()
    reg.load_builtins()
    plugin = reg.get("electronics")
    assert plugin is not None
    assert len(plugin.subcategories) > 0


# ─── Engine ───────────────────────────────────────────────────────────────────

def test_seeder_deterministic():
    from cug.engine.seeder import DeterministicSeeder
    import datetime
    s = DeterministicSeeder(42)
    d = datetime.date(2024, 1, 1)
    seed1 = s.day_seed(d)
    seed2 = s.day_seed(d)
    assert seed1 == seed2


def test_temporal_online_pct():
    from cug.engine.temporal import interpolate_online_pct
    import datetime
    pct_early = interpolate_online_pct(datetime.date(2015, 1, 1), 0.10, 0.55)
    pct_late  = interpolate_online_pct(datetime.date(2026, 1, 1), 0.10, 0.55)
    assert pct_early < pct_late
    assert 0 <= pct_early <= 1
    assert 0 <= pct_late  <= 1


# ─── Generators ──────────────────────────────────────────────────────────────

def test_dim_date_shape():
    from cug.generators.calendar import generate_dim_date
    from datetime import date
    df = generate_dim_date(date(2024, 1, 1), date(2024, 3, 31))
    assert len(df) == 91  # Jan(31) + Feb(29 leap) + Mar(31)
    assert "DateKey" in df.columns
    assert "Date" in df.columns


def test_dim_currency_count():
    from cug.generators.currency import generate_dim_currency
    df = generate_dim_currency()
    assert len(df) >= 25
    assert "CurrencyCode" in df.columns


def test_dim_customer_columns():
    from cug.generators.customers import generate_dim_customer
    df = generate_dim_customer(pool_size=50, language="en", seed=1)
    assert len(df) == 50
    for col in ("CustomerKey", "FirstName", "Email", "Segment"):
        assert col in df.columns


def test_dim_product_has_rows():
    from cug.categories.registry import CategoryRegistry
    from cug.generators.products import generate_dim_product
    reg = CategoryRegistry()
    reg.load_builtins()
    df = generate_dim_product(registry=reg, language="en", seed=1)
    assert len(df) > 0
    assert "UnitPrice" in df.columns


def test_dim_store_has_online_row():
    from cug.generators.stores import generate_dim_store
    df = generate_dim_store(language="en", seed=1)
    online = df.filter(pl.col("Channel") == "Online")
    assert len(online) == 1
    assert online["StoreKey"][0] == 1
