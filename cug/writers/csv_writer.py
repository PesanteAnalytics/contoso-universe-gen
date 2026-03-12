"""
CSV Writer — exports all dimension and fact tables to CSV files.

Options:
    separator     : str  — field delimiter (default: ",")
    include_header: bool — write header row (default: True)
    null_value    : str  — representation for null values (default: "")
    date_format   : str  — strftime format for date columns (default: None = ISO)
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


def write_csv(
    result: GenerationResult,
    output_path: Path,
    *,
    separator: str = ",",
    include_header: bool = True,
    null_value: str = "",
    date_format: str | None = None,
    **_extra: Any,
) -> None:
    """Write all tables as CSV files into output_path/csv/."""
    dest = output_path / "csv"
    dest.mkdir(parents=True, exist_ok=True)

    write_kwargs: dict[str, Any] = {
        "separator": separator,
        "include_header": include_header,
        "null_value": null_value,
    }
    if date_format is not None:
        write_kwargs["date_format"] = date_format

    for name, df in _get_tables(result).items():
        df.write_csv(dest / f"{name}.csv", **write_kwargs)
