"""
Parquet Writer — exports all tables to columnar Parquet files.

Options:
    compression : str   — compression codec (default: "zstd")
                          Options: zstd, snappy, gzip, lz4, brotli, none
    row_group_size : int — rows per row group (default: let Polars decide)
"""

from __future__ import annotations

from pathlib import Path
from typing import Any

from ..models import GenerationResult

_TABLES = [
    "DimDate", "DimCustomer", "DimProduct", "DimStore",
    "DimCurrency", "DimCurrencyExchange", "FactSales",
]


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


def write_parquet(
    result: GenerationResult,
    output_path: Path,
    *,
    compression: str = "zstd",
    row_group_size: int | None = None,
    **_extra: Any,
) -> None:
    """Write all tables as Parquet files into output_path/parquet/."""
    dest = output_path / "parquet"
    dest.mkdir(parents=True, exist_ok=True)

    write_kwargs: dict[str, Any] = {"compression": compression}
    if row_group_size is not None:
        write_kwargs["row_group_size"] = row_group_size

    for name, df in _get_tables(result).items():
        df.write_parquet(dest / f"{name}.parquet", **write_kwargs)
