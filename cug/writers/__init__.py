"""
Writers package — pluggable output format adapters.

Supported formats:
  - csv       : CSV flat files
  - parquet   : Apache Parquet columnar (default)
  - duckdb    : DuckDB embedded database with analytical views
  - delta     : Delta Lake tables (great for Fabric/Spark)
  - json      : JSON/NDJSON files
  - excel     : Excel .xlsx workbooks
  - sqlserver : Microsoft SQL Server database
"""

from __future__ import annotations

from pathlib import Path
from typing import Any

from ..models import GenerationResult

# ── Format registry ──────────────────────────────────────────────────────────
# Maps format name → writer function.  Each writer has signature:
#   (result: GenerationResult, output_path: Path, **options) -> None | Path

from ..config import SUPPORTED_FORMATS


def write_format(
    fmt: str,
    result: GenerationResult,
    output_path: Path,
    **options: Any,
) -> None:
    """
    Dispatch to the appropriate writer for `fmt`.

    Args:
        fmt:         One of SUPPORTED_FORMATS.
        result:      The generated data.
        output_path: Root output directory.
        **options:   Format-specific keyword arguments forwarded to the writer.
    """
    fmt = fmt.strip().lower()
    if fmt not in SUPPORTED_FORMATS:
        raise ValueError(
            f"Unknown output format '{fmt}'. "
            f"Supported: {', '.join(sorted(SUPPORTED_FORMATS))}"
        )

    # Lazy imports to avoid loading unused dependencies
    if fmt == "csv":
        from .csv_writer import write_csv
        write_csv(result, output_path, **options)

    elif fmt == "parquet":
        from .parquet_writer import write_parquet
        write_parquet(result, output_path, **options)

    elif fmt == "duckdb":
        from .duckdb_writer import write_duckdb
        write_duckdb(result, output_path, **options)

    elif fmt == "delta":
        from .delta_writer import write_delta
        write_delta(result, output_path, **options)

    elif fmt == "json":
        from .json_writer import write_json
        write_json(result, output_path, **options)

    elif fmt == "excel":
        from .excel_writer import write_excel
        write_excel(result, output_path, **options)

    elif fmt == "sqlserver":
        from .sqlserver_writer import write_sqlserver
        write_sqlserver(result, output_path, **options)


# Keep individual imports for backward compatibility
from .csv_writer     import write_csv
from .parquet_writer import write_parquet
from .duckdb_writer  import write_duckdb

__all__ = [
    "SUPPORTED_FORMATS",
    "write_format",
    "write_csv",
    "write_parquet",
    "write_duckdb",
]
