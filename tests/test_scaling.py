"""
Scaling tests — verify that pool sizes and row counts scale proportionally
with target_orders, and that DimCurrencyExchange is constant (date-range based).
"""

import subprocess
import sys
import polars as pl
from pathlib import Path
import pytest


def _generate_csv(tmp_path: Path, n: int) -> Path:
    """Generate at scale n; the CSV writer nests its tables under output/csv/."""
    out = tmp_path / f"scale_{n}"
    result = subprocess.run(
        [sys.executable, "-m", "cug", "generate",
         "-n", str(n), "-f", "csv", "-o", str(out), "--seed", "42"],
        capture_output=True, text=True, encoding="utf-8", errors="replace", timeout=120,
    )
    assert result.returncode == 0, f"Generation failed for n={n}:\n{result.stderr}"
    return out / "csv"


@pytest.mark.parametrize("n_orders", [100, 1000, 5000])
def test_fact_sales_rows_scale_with_orders(tmp_path, n_orders):
    """FactSales row count should be roughly proportional to target_orders."""
    out = _generate_csv(tmp_path, n_orders)
    df = pl.read_csv(out / "FactSales.csv")
    # FactSales rows should be at least 50% of target_orders (Poisson sampling)
    assert len(df) >= n_orders * 0.5, (
        f"FactSales has {len(df)} rows for n_orders={n_orders} "
        f"(expected ≥ {n_orders * 0.5:.0f})"
    )


@pytest.mark.parametrize("n_orders", [100, 1000, 5000])
def test_dim_customer_scales_with_orders(tmp_path, n_orders):
    """DimCustomer pool should scale with target_orders, never exceed 50k default."""
    out = _generate_csv(tmp_path, n_orders)
    df = pl.read_csv(out / "DimCustomer.csv")
    # Pool should be at most 50k and at least proportional to orders
    assert len(df) <= 50_000, f"DimCustomer too large: {len(df)}"
    assert len(df) >= 100, f"DimCustomer too small: {len(df)}"


def test_dim_currency_exchange_is_constant(tmp_path):
    """DimCurrencyExchange size should be the same regardless of target_orders
    because it depends on date range × currency count, not on order volume."""
    out_100 = _generate_csv(tmp_path, 100)
    out_5000 = _generate_csv(tmp_path, 5000)
    df_100 = pl.read_csv(out_100 / "DimCurrencyExchange.csv")
    df_5000 = pl.read_csv(out_5000 / "DimCurrencyExchange.csv")
    assert len(df_100) == len(df_5000), (
        f"DimCurrencyExchange should be constant: "
        f"n=100 → {len(df_100)} rows, n=5000 → {len(df_5000)} rows"
    )


def test_no_negative_prices(tmp_path):
    """At no scale should UnitCost exceed UnitPrice (negative margin check).

    Runs at 5,000 orders on purpose. Thin-margin subcategories (gaming hardware
    starts at a 2% margin) only collide with the quarterly COGS noise in roughly
    one row in 1,300, so a 500-order sample clears this by luck rather than by
    correctness.
    """
    out = _generate_csv(tmp_path, 5_000)
    df = pl.read_csv(out / "FactSales.csv")
    assert {"UnitPrice", "UnitCost"} <= set(df.columns)
    negative_margin = df.filter(pl.col("UnitCost") > pl.col("UnitPrice"))
    assert len(negative_margin) == 0, (
        f"{len(negative_margin)} of {len(df)} rows have UnitCost > UnitPrice"
    )
