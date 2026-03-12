"""
DuckDB Writer — creates an embedded DuckDB database with all tables.

The database can be opened directly by Power BI, DBeaver, or any
DuckDB-compatible client for instant SQL analytics.
"""

from __future__ import annotations

from pathlib import Path

import duckdb
import polars as pl

from ..models import GenerationResult


def write_duckdb(
    result: GenerationResult,
    output_path: Path,
    db_name: str = "contoso.duckdb",
    **_extra,
) -> Path:
    """
    Write all tables into a DuckDB file at output_path/db_name.

    Also creates a set of useful analytical views (V2-aligned schema):
      - v_sales_summary  : daily sales totals
      - v_top_products   : top 20 products by revenue
      - v_category_trend : monthly revenue by category
    """
    dest = output_path / db_name
    dest.parent.mkdir(parents=True, exist_ok=True)

    # Remove existing to avoid conflicts
    if dest.exists():
        dest.unlink()

    con = duckdb.connect(str(dest))

    tables: dict[str, pl.DataFrame | None] = {
        "DimDate":             result.dim_date,
        "DimCustomer":         result.dim_customer,
        "DimProduct":          result.dim_product,
        "DimStore":            result.dim_store,
        "DimCurrency":         result.dim_currency,
        "DimCurrencyExchange": result.dim_currency_exchange,
        "FactSales":           result.fact_sales,
    }

    for name, df in tables.items():
        if df is None:
            continue
        # Register Polars DataFrame as an Arrow table for zero-copy ingestion
        arrow_table = df.to_arrow()
        con.register(f"_arrow_{name}", arrow_table)
        con.execute(f"CREATE TABLE {name} AS SELECT * FROM _arrow_{name}")
        con.unregister(f"_arrow_{name}")

    # ── Analytical views (V2-compatible column names) ─────────────────────────
    #   V2: OrderDate is an ISO date string, DimDate.Date is a DATE column.
    #       We cast OrderDate to DATE for the join.

    con.execute("""
        CREATE VIEW v_sales_summary AS
        SELECT
            d.Date,
            d.Year,
            d.MonthName,
            d.Quarter,
            COUNT(f.OrderKey)                         AS Orders,
            ROUND(SUM(f.NetPrice * f.Quantity), 2)    AS Revenue,
            ROUND(SUM((f.NetPrice - f.UnitCost) * f.Quantity), 2) AS Margin,
            ROUND(AVG(f.NetPrice * f.Quantity), 2)    AS AvgOrderValue
        FROM FactSales f
        JOIN DimDate d ON CAST(f.OrderDate AS DATE) = d.Date
        GROUP BY d.Date, d.Year, d.MonthName, d.Quarter
        ORDER BY d.Date
    """)

    con.execute("""
        CREATE VIEW v_top_products AS
        SELECT
            p.ProductName,
            p.CategoryName,
            p.SubCategoryName,
            ROUND(SUM(f.NetPrice * f.Quantity), 2)  AS Revenue,
            SUM(f.Quantity)                          AS UnitsSold,
            ROUND(AVG(f.UnitPrice - f.NetPrice), 4) AS AvgDiscount
        FROM FactSales f
        JOIN DimProduct p ON f.ProductKey = p.ProductKey
        GROUP BY p.ProductName, p.CategoryName, p.SubCategoryName
        ORDER BY Revenue DESC
        LIMIT 20
    """)

    con.execute("""
        CREATE VIEW v_category_trend AS
        SELECT
            d.Year,
            d.Month,
            d.MonthName,
            p.CategoryName,
            ROUND(SUM(f.NetPrice * f.Quantity), 2) AS Revenue,
            COUNT(f.OrderKey)                       AS Orders
        FROM FactSales f
        JOIN DimDate    d ON CAST(f.OrderDate AS DATE) = d.Date
        JOIN DimProduct p ON f.ProductKey = p.ProductKey
        GROUP BY d.Year, d.Month, d.MonthName, p.CategoryName
        ORDER BY d.Year, d.Month, p.CategoryName
    """)

    con.close()
    return dest
