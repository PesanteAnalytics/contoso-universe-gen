"""
Delta Lake Writer — exports all tables as Delta Lake tables.

Perfect for Microsoft Fabric, Databricks, and Spark-based analytics.
Requires the 'delta' extra: pip install 'contoso-universe-gen[delta]'

Options:
    mode          : str — write mode: "overwrite" | "append" | "error" (default: "overwrite")
    partition_by  : list[str] | None — columns to partition FactSales by (default: None)
    name          : str — name added to delta log metadata (default: "contoso")
    description   : str — description in delta log metadata (default: auto)
"""

from __future__ import annotations

from pathlib import Path
from typing import Any

import polars as pl

from ..models import GenerationResult


def _get_tables(result: GenerationResult) -> dict[str, Any]:
    """Return dict of table name → DataFrame, skipping None."""
    return {
        name: getattr(result, attr)
        for name, attr in [
            ("DimDate",             "dim_date"),
            ("DimCustomer",         "dim_customer"),
            ("DimProduct",          "dim_product"),
            ("DimStore",            "dim_store"),
            ("DimCurrency",         "dim_currency"),
            ("DimCurrencyExchange", "dim_currency_exchange"),
            ("FactSales",           "fact_sales"),
        ]
        if getattr(result, attr) is not None
    }


def write_delta(
    result: GenerationResult,
    output_path: Path,
    *,
    mode: str = "overwrite",
    partition_by: list[str] | None = None,
    name: str = "contoso",
    description: str | None = None,
    **_extra: Any,
) -> None:
    """
    Write all tables as Delta Lake tables into output_path/delta/<TableName>/.

    Each table becomes a separate Delta table that can be read by
    Spark, Fabric, Databricks, or any Delta-compatible reader.
    """
    try:
        from deltalake import write_deltalake  # noqa: F401
    except ImportError as exc:
        raise ImportError(
            "The Delta Lake writer needs 'deltalake', which ships as an extra.\n"
            "  pip install 'contoso-universe-gen[delta]'"
        ) from exc

    dest = output_path / "delta"
    dest.mkdir(parents=True, exist_ok=True)

    for table_name, df in _get_tables(result).items():
        table_path = dest / table_name
        table_path.mkdir(parents=True, exist_ok=True)

        # Cast Null-type columns to String — Delta Lake rejects Null as a type.
        # This happens with small datasets where columns like EndDT/CloseDate
        # are all-null and Polars infers them as pl.Null.
        null_cols = [c for c in df.columns if df[c].dtype == pl.Null]
        if null_cols:
            df = df.with_columns([pl.col(c).cast(pl.Utf8) for c in null_cols])

        # Convert Polars → Arrow for deltalake
        arrow_table = df.to_arrow()

        write_kwargs: dict[str, Any] = {
            "mode": mode,
            "name": f"{name}_{table_name}",
            "description": description or f"Contoso Universe Generator — {table_name}",
        }

        # Only partition FactSales (it's the big one)
        if partition_by and table_name == "FactSales":
            write_kwargs["partition_by"] = partition_by

        write_deltalake(
            str(table_path),
            arrow_table,
            **write_kwargs,
        )
