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
    assert loc.locale_tag == "en_US"


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
    for col in ("CustomerKey", "GivenName", "Surname", "Company"):
        assert col in df.columns


def test_dim_product_has_rows():
    from cug.categories.registry import CategoryRegistry
    from cug.generators.products import generate_dim_product
    reg = CategoryRegistry()
    reg.load_builtins()
    df = generate_dim_product(registry=reg, language="en", seed=1)
    assert len(df) > 0
    assert "Price" in df.columns


def test_dim_store_has_online_row():
    from cug.generators.stores import generate_dim_store
    df = generate_dim_store(language="en", seed=1)
    online = df.filter(pl.col("Status") == "Online")
    assert len(online) == 1
    assert online["StoreKey"][0] == 1


# ─── Writers ─────────────────────────────────────────────────────────────────

def test_delta_null_column_cast():
    """Null-type columns must be cast to Utf8 before Delta write."""
    df = pl.DataFrame({
        "id": [1, 2, 3],
        "name": ["a", "b", "c"],
        "empty_col": [None, None, None],       # inferred as Null
    })
    assert df["empty_col"].dtype == pl.Null
    # Apply the same fix as delta_writer.py
    null_cols = [c for c in df.columns if df[c].dtype == pl.Null]
    df_fixed = df.with_columns([pl.col(c).cast(pl.Utf8) for c in null_cols])
    assert df_fixed["empty_col"].dtype == pl.Utf8
    assert df_fixed["empty_col"].null_count() == 3  # still all null
    # Arrow conversion should work without error
    arrow = df_fixed.to_arrow()
    assert arrow.num_rows == 3


def test_duckdb_writer_creates_views(tmp_path):
    """DuckDB writer must create 3 analytical views."""
    import duckdb
    from datetime import date
    from cug.generators.calendar import generate_dim_date
    from cug.generators.currency import generate_dim_currency
    from cug.generators.customers import generate_dim_customer
    from cug.generators.stores import generate_dim_store
    from cug.categories.registry import CategoryRegistry
    from cug.generators.products import generate_dim_product
    from cug.models import GenerationResult
    from cug.writers.duckdb_writer import write_duckdb

    # Minimal dataset
    dim_date = generate_dim_date(date(2024, 1, 1), date(2024, 1, 10))
    dim_currency = generate_dim_currency()
    dim_customer = generate_dim_customer(pool_size=10, language="en", seed=1)
    dim_store = generate_dim_store(language="en", seed=1)
    reg = CategoryRegistry()
    reg.load_builtins()
    dim_product = generate_dim_product(registry=reg, language="en", seed=1)

    # Create a minimal FactSales
    fact_sales = pl.DataFrame({
        "OrderKey": [1],
        "OrderDate": ["2024-01-01"],
        "CustomerKey": [dim_customer["CustomerKey"][0]],
        "ProductKey": [dim_product["ProductKey"][0]],
        "StoreKey": [dim_store["StoreKey"][0]],
        "CurrencyKey": [1],
        "Quantity": [1],
        "UnitPrice": [100.0],
        "NetPrice": [95.0],
        "UnitCost": [50.0],
        "OrderNumber": ["SO-0001"],
        "LineNumber": [1],
        "DeliveryDate": ["2024-01-05"],
        "ExchangeRate": [1.0],
    })

    result = GenerationResult()
    result.dim_date = dim_date
    result.dim_customer = dim_customer
    result.dim_product = dim_product
    result.dim_store = dim_store
    result.dim_currency = dim_currency
    result.dim_currency_exchange = pl.DataFrame({
        "Date": ["2024-01-01"], "FromCurrencyKey": [1],
        "ToCurrencyKey": [2], "Rate": [0.85]
    })
    result.fact_sales = fact_sales

    db_path = write_duckdb(result, tmp_path)
    con = duckdb.connect(str(db_path), read_only=True)
    tables = [r[0] for r in con.execute("SHOW TABLES").fetchall()]
    con.close()

    # Must include the 3 analytical views
    for view in ("v_sales_summary", "v_top_products", "v_category_trend"):
        assert view in tables, f"Missing view: {view}"
