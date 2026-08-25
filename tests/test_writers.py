"""
Writer tests — verify that each output format produces valid files.
Uses small datasets generated in-memory to keep tests fast.

Note: Writers create subdirectories per format:
  - write_csv  → output_path/csv/
  - write_parquet → output_path/parquet/
  - write_json → output_path/json/
"""

from datetime import date

import polars as pl

from cug.categories.registry import CategoryRegistry
from cug.generators.calendar import generate_dim_date
from cug.generators.currency import generate_dim_currency
from cug.generators.customers import generate_dim_customer
from cug.generators.products import generate_dim_product
from cug.generators.stores import generate_dim_store
from cug.models import GenerationResult


def _make_result() -> GenerationResult:
    """Build a minimal but valid GenerationResult."""
    reg = CategoryRegistry()
    reg.load_builtins()
    dim_customer = generate_dim_customer(pool_size=20, language="en", seed=7)
    dim_product = generate_dim_product(registry=reg, language="en", seed=7)
    dim_store = generate_dim_store(language="en", seed=7)

    fact_sales = pl.DataFrame({
        "OrderKey":    [1, 2, 3],
        "OrderDate":   ["2024-01-10", "2024-02-15", "2024-03-20"],
        "CustomerKey": dim_customer["CustomerKey"][:3].to_list(),
        "ProductKey":  dim_product["ProductKey"][:3].to_list(),
        "StoreKey":    [dim_store["StoreKey"][0]] * 3,
        "CurrencyKey": [1, 2, 1],
        "Quantity":    [1, 2, 1],
        "UnitPrice":   [100.0, 200.0, 150.0],
        "NetPrice":    [95.0, 190.0, 142.5],
        "UnitCost":    [50.0, 100.0, 75.0],
        "OrderNumber": ["SO-0001", "SO-0002", "SO-0003"],
        "LineNumber":  [1, 1, 1],
        "DeliveryDate": ["2024-01-15", "2024-02-20", "2024-03-25"],
        "ExchangeRate": [1.0, 0.85, 1.12],
    })

    result = GenerationResult()
    result.dim_date = generate_dim_date(date(2024, 1, 1), date(2024, 3, 31))
    result.dim_customer = dim_customer
    result.dim_product = dim_product
    result.dim_store = dim_store
    result.dim_currency = generate_dim_currency()
    result.dim_currency_exchange = pl.DataFrame({
        "Date": ["2024-01-01", "2024-01-02"],
        "FromCurrencyKey": [1, 1],
        "ToCurrencyKey": [2, 3],
        "Rate": [0.85, 1.12],
    })
    result.fact_sales = fact_sales
    return result


# ─── CSV writer ──────────────────────────────────────────────────────────────

def test_csv_writer_creates_files(tmp_path):
    from cug.writers.csv_writer import write_csv
    result = _make_result()
    write_csv(result, tmp_path)
    csvs = list((tmp_path / "csv").glob("*.csv"))
    assert len(csvs) >= 7, f"Expected ≥7 CSV files in csv/, got {len(csvs)}"


def test_csv_sales_row_count(tmp_path):
    from cug.writers.csv_writer import write_csv
    result = _make_result()
    write_csv(result, tmp_path)
    df = pl.read_csv(tmp_path / "csv" / "FactSales.csv")
    assert len(df) == 3


# ─── Parquet writer ──────────────────────────────────────────────────────────

def test_parquet_writer_creates_files(tmp_path):
    from cug.writers.parquet_writer import write_parquet
    result = _make_result()
    write_parquet(result, tmp_path)
    parquets = list((tmp_path / "parquet").glob("*.parquet"))
    assert len(parquets) >= 7, f"Expected ≥7 Parquet files in parquet/, got {len(parquets)}"


def test_parquet_readable(tmp_path):
    from cug.writers.parquet_writer import write_parquet
    result = _make_result()
    write_parquet(result, tmp_path)
    df = pl.read_parquet(tmp_path / "parquet" / "FactSales.parquet")
    assert len(df) == 3
    assert "UnitPrice" in df.columns


# ─── JSON writer ──────────────────────────────────────────────────────────────

def test_json_writer_creates_files(tmp_path):
    from cug.writers.json_writer import write_json
    result = _make_result()
    write_json(result, tmp_path)  # default: NDJSON (.ndjson)
    ndjsons = list((tmp_path / "json").glob("*.ndjson"))
    assert len(ndjsons) >= 7, f"Expected ≥7 NDJSON files in json/, got {len(ndjsons)}"


def test_json_fact_sales_parseable(tmp_path):
    from cug.writers.json_writer import write_json
    result = _make_result()
    write_json(result, tmp_path)  # writes .ndjson by default
    ndjson_file = tmp_path / "json" / "FactSales.ndjson"
    assert ndjson_file.exists(), "FactSales.ndjson not found"
    df = pl.read_ndjson(ndjson_file)
    assert len(df) == 3
    assert "UnitPrice" in df.columns
