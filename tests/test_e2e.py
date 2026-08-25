"""
End-to-end tests — run a full generation pipeline at small scale.
Verifies that all tables are produced with valid FK relationships.
"""

import pytest
import polars as pl
from pathlib import Path


def _run_generate(tmp_path: Path, n: int = 100, fmt: str = "csv", lang: str = "en") -> Path:
    """Run cug generate via subprocess; writers nest tables under output/<fmt>/."""
    import subprocess, sys
    out = tmp_path / f"out_{n}"
    result = subprocess.run(
        [sys.executable, "-m", "cug", "generate",
         "-n", str(n), "-f", fmt, "-l", lang,
         "-o", str(out), "--seed", "42"],
        capture_output=True, text=True, encoding="utf-8", errors="replace", timeout=120,
    )
    assert result.returncode == 0, f"cug generate failed:\n{result.stderr}"
    return out / fmt


EXPECTED_TABLES = [
    "DimDate", "DimCustomer", "DimProduct",
    "DimStore", "DimCurrency", "DimCurrencyExchange", "FactSales",
]


def test_e2e_generates_all_tables(tmp_path):
    """All 7 tables must be present in the output."""
    out = _run_generate(tmp_path, n=200)
    for table in EXPECTED_TABLES:
        csv_file = out / f"{table}.csv"
        assert csv_file.exists(), f"Missing output file: {table}.csv"


def test_e2e_fact_sales_has_rows(tmp_path):
    """FactSales must have at least 1 row when target_orders > 0."""
    out = _run_generate(tmp_path, n=200)
    df = pl.read_csv(out / "FactSales.csv")
    assert len(df) > 0, "FactSales is empty"


def test_e2e_fk_customer_integrity(tmp_path):
    """Every CustomerKey in FactSales must exist in DimCustomer."""
    out = _run_generate(tmp_path, n=500)
    sales = pl.read_csv(out / "FactSales.csv")
    customers = pl.read_csv(out / "DimCustomer.csv")
    valid_keys = set(customers["CustomerKey"].to_list())
    orphans = [k for k in sales["CustomerKey"].to_list() if k not in valid_keys]
    assert len(orphans) == 0, f"FK violation: {len(orphans)} orphaned CustomerKey(s)"


def test_e2e_fk_product_integrity(tmp_path):
    """Every ProductKey in FactSales must exist in DimProduct."""
    out = _run_generate(tmp_path, n=500)
    sales = pl.read_csv(out / "FactSales.csv")
    products = pl.read_csv(out / "DimProduct.csv")
    valid_keys = set(products["ProductKey"].to_list())
    orphans = [k for k in sales["ProductKey"].to_list() if k not in valid_keys]
    assert len(orphans) == 0, f"FK violation: {len(orphans)} orphaned ProductKey(s)"


def test_e2e_fk_store_integrity(tmp_path):
    """Every StoreKey in FactSales must exist in DimStore."""
    out = _run_generate(tmp_path, n=500)
    sales = pl.read_csv(out / "FactSales.csv")
    stores = pl.read_csv(out / "DimStore.csv")
    valid_keys = set(stores["StoreKey"].to_list())
    orphans = [k for k in sales["StoreKey"].to_list() if k not in valid_keys]
    assert len(orphans) == 0, f"FK violation: {len(orphans)} orphaned StoreKey(s)"


def test_e2e_spanish_locale(tmp_path):
    """Generation in Spanish must succeed and produce the same 7 tables."""
    out = _run_generate(tmp_path, n=100, lang="es")
    for table in EXPECTED_TABLES:
        assert (out / f"{table}.csv").exists(), f"Missing: {table}.csv (es locale)"


def test_e2e_prices_are_positive(tmp_path):
    """UnitPrice, NetPrice, and UnitCost must all be positive."""
    out = _run_generate(tmp_path, n=300)
    df = pl.read_csv(out / "FactSales.csv")
    for col in ("UnitPrice", "NetPrice", "UnitCost"):
        if col in df.columns:
            assert (df[col] > 0).all(), f"{col} has non-positive values"


def test_e2e_city_belongs_to_its_country(tmp_path):
    """Every City / State / Country triple must describe one real place.

    Cities used to be drawn from a flat per-language pool with no regard for the
    country already assigned, which put Buenos Aires in Mexico.
    """
    import polars as pl_

    from cug.i18n.geography import _GEO_BY_LANG

    out = _run_generate(tmp_path, n=2_000, lang="es")
    customers = pl_.read_csv(out / "DimCustomer.csv")

    valid = {
        (country_full, city, state_full)
        for _, country_full, _, cities in _GEO_BY_LANG["es"]
        for city, _, state_full, _, _ in cities
    }
    seen = set(
        customers.select(["CountryFull", "City", "StateFull"]).unique().iter_rows()
    )
    assert seen <= valid, f"impossible places: {sorted(seen - valid)}"


def test_e2e_coordinates_sit_near_the_city(tmp_path):
    """Latitude and longitude must place the customer in their own city."""
    import polars as pl_

    from cug.i18n.geography import _GEO_BY_LANG

    out = _run_generate(tmp_path, n=2_000, lang="es")
    customers = pl_.read_csv(out / "DimCustomer.csv")

    centres = {
        city: (lat, lon)
        for _, _, _, cities in _GEO_BY_LANG["es"]
        for city, _, _, lat, lon in cities
    }
    for city, lat, lon in customers.select(["City", "Latitude", "Longitude"]).iter_rows():
        centre_lat, centre_lon = centres[city]
        assert abs(lat - centre_lat) < 1.0, f"{city}: latitude {lat} is not near {centre_lat}"
        assert abs(lon - centre_lon) < 1.0, f"{city}: longitude {lon} is not near {centre_lon}"


def test_e2e_language_coverage_matches_the_data(tmp_path):
    """What `cug info` claims a language localizes must be what it produces.

    The README used to advertise "8 languages: names, cities and categories
    fully localized" while five of them generated a US customer base.
    """
    import polars as pl_

    from cug.i18n import locale_coverage
    from cug.i18n.geography import _GEO_BY_LANG

    # ja has a translated catalogue but no geography of its own.
    assert locale_coverage("ja") == {"catalog": True, "calendar": False, "people": False}

    out = _run_generate(tmp_path, n=500, lang="ja")
    customers = pl_.read_csv(out / "DimCustomer.csv")
    products = pl_.read_csv(out / "DimProduct.csv")

    fallback_countries = {country for _, country, _, _ in _GEO_BY_LANG["en"]}
    assert set(customers["CountryFull"].unique()) <= fallback_countries, (
        "people coverage is reported False, so the customer base must fall back to en"
    )
    assert not products["CategoryName"].str.contains("Electronics").any(), (
        "catalog coverage is reported True, so categories must be translated"
    )
