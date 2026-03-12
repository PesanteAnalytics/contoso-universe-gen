"""
JSON Writer — exports all tables as JSON or NDJSON files.

Options:
    row_oriented : bool — True = array of objects, False = NDJSON one-per-line (default: False)
    pretty       : bool — pretty-print JSON (only when row_oriented=True, default: False)
"""

from __future__ import annotations

from pathlib import Path
from typing import Any

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


def write_json(
    result: GenerationResult,
    output_path: Path,
    *,
    row_oriented: bool = False,
    pretty: bool = False,
    **_extra: Any,
) -> None:
    """
    Write all tables as JSON files into output_path/json/.

    By default writes NDJSON (newline-delimited JSON) which is ideal for
    streaming ingestion. Set row_oriented=True for standard JSON arrays.
    """
    dest = output_path / "json"
    dest.mkdir(parents=True, exist_ok=True)

    for table_name, df in _get_tables(result).items():
        if row_oriented:
            ext = ".json"
            df.write_json(dest / f"{table_name}{ext}", pretty=pretty, row_oriented=True)
        else:
            ext = ".ndjson"
            df.write_ndjson(dest / f"{table_name}{ext}")
