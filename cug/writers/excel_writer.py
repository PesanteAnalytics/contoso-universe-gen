"""
Excel Writer — exports all tables as .xlsx workbook(s).

Options:
    single_workbook : bool — True = all tables in one workbook,
                             False = one workbook per table (default: True)
    workbook_name   : str  — filename when single_workbook=True (default: "contoso.xlsx")
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


def write_excel(
    result: GenerationResult,
    output_path: Path,
    *,
    single_workbook: bool = True,
    workbook_name: str = "contoso.xlsx",
    **_extra: Any,
) -> None:
    """
    Write all tables as Excel files into output_path/excel/.

    NOTE: Excel has a 1,048,576 row limit per sheet. For large FactSales
    tables, prefer parquet or delta formats. This writer will truncate
    with a warning if the limit is exceeded.
    """
    try:
        import xlsxwriter
    except ImportError as exc:
        raise ImportError(
            "The Excel writer needs 'xlsxwriter', which ships as an extra.\n"
            "  pip install 'contoso-universe-gen[excel]'"
        ) from exc

    dest = output_path / "excel"
    dest.mkdir(parents=True, exist_ok=True)

    MAX_EXCEL_ROWS = 1_048_576

    tables = _get_tables(result)

    if single_workbook:
        # Write all tables as sheets in a single workbook
        wb_path = dest / workbook_name
        workbook = xlsxwriter.Workbook(str(wb_path))

        for table_name, df in tables.items():
            if len(df) > MAX_EXCEL_ROWS:
                import warnings
                warnings.warn(
                    f"⚠ {table_name} has {len(df):,} rows — "
                    f"truncating to Excel limit ({MAX_EXCEL_ROWS:,}). "
                    f"Use parquet or delta for full data.",
                    stacklevel=2,
                )
                df = df.head(MAX_EXCEL_ROWS - 1)  # -1 for header

            # Write using Polars → Excel via intermediate
            sheet = workbook.add_worksheet(table_name[:31])  # Excel sheet name max 31 chars
            header_fmt = workbook.add_format({"bold": True, "bg_color": "#D9E2F3"})

            # Write header
            for col_idx, col_name in enumerate(df.columns):
                sheet.write(0, col_idx, col_name, header_fmt)

            # Write data row by row
            for row_idx, row in enumerate(df.iter_rows(), start=1):
                for col_idx, value in enumerate(row):
                    if value is None:
                        sheet.write_blank(row_idx, col_idx, None)
                    else:
                        sheet.write(row_idx, col_idx, str(value) if not isinstance(value, (int, float)) else value)

            sheet.autofilter(0, 0, len(df), len(df.columns) - 1)

        workbook.close()

    else:
        # One workbook per table
        for table_name, df in tables.items():
            if len(df) > MAX_EXCEL_ROWS:
                import warnings
                warnings.warn(
                    f"⚠ {table_name} has {len(df):,} rows — "
                    f"truncating to Excel limit ({MAX_EXCEL_ROWS:,}).",
                    stacklevel=2,
                )
                df = df.head(MAX_EXCEL_ROWS - 1)

            df.write_excel(dest / f"{table_name}.xlsx")
