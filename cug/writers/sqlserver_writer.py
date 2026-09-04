"""
SQL Server Writer — bulk-loads all tables into a SQL Server database.

Uses pyodbc with fast_executemany for high-throughput inserts.
Automatically creates tables with appropriate SQL Server data types
mapped from the Polars schema.

Options:
    connection_string : str  — full ODBC connection string
    server            : str  — server name (alternative to connection_string)
    database          : str  — database name (default: "ContosoRetail")
    schema            : str  — SQL schema name (default: "dbo")
    driver            : str  — ODBC driver (default: auto-detect best available)
    trusted           : bool — use Windows Authentication (default: True)
    if_exists         : str  — "replace" | "append" | "fail" (default: "replace")
    batch_size        : int  — rows per batch insert (default: 5000)
"""

from __future__ import annotations

from pathlib import Path
from typing import Any

import polars as pl
from rich.console import Console

from ..models import GenerationResult

console = Console()


# ── Polars → SQL Server type mapping ──────────────────────────────────────────

_TYPE_MAP: dict[str, str] = {
    # Integers
    "Int8":     "TINYINT",
    "Int16":    "SMALLINT",
    "Int32":    "INT",
    "Int64":    "BIGINT",
    "UInt8":    "SMALLINT",     # SQL Server has no unsigned; bump up
    "UInt16":   "INT",
    "UInt32":   "BIGINT",
    "UInt64":   "BIGINT",
    # Floats
    "Float32":  "REAL",
    "Float64":  "FLOAT",
    # Strings & text
    "Utf8":     "NVARCHAR(400)",
    "String":   "NVARCHAR(400)",
    "Categorical": "NVARCHAR(200)",
    # Boolean
    "Boolean":  "BIT",
    # Dates and times
    "Date":     "DATE",
    "Datetime": "DATETIME2",
    "Time":     "TIME",
    "Duration": "BIGINT",       # store as microseconds
    # Binary
    "Binary":   "VARBINARY(MAX)",
    # Decimal
    "Decimal":  "DECIMAL(19,4)",
    # Null type (Polars columns where all values are None)
    "Null":     "NVARCHAR(1)",
}


def _polars_to_sql_type(dtype: pl.DataType) -> str:
    """Map a Polars dtype to a SQL Server column type."""
    base = str(dtype).split("(")[0]   # e.g. "Datetime(μs, None)" → "Datetime"
    return _TYPE_MAP.get(base, "NVARCHAR(MAX)")


def _detect_best_driver() -> str:
    """Auto-detect the best ODBC driver for SQL Server."""
    try:
        import pyodbc
        drivers = pyodbc.drivers()
    except Exception:
        return "ODBC Driver 17 for SQL Server"

    # Prefer the newest ODBC Driver
    preferred = [
        "ODBC Driver 18 for SQL Server",
        "ODBC Driver 17 for SQL Server",
        "SQL Server Native Client 11.0",
        "SQL Server",
    ]
    for drv in preferred:
        if drv in drivers:
            return drv

    # Fallback: use first SQL-related driver
    for drv in drivers:
        if "SQL" in drv.upper():
            return drv

    return "ODBC Driver 17 for SQL Server"


def _build_connection_string(
    *,
    server: str = "localhost",
    database: str = "ContosoRetail",
    driver: str | None = None,
    trusted: bool = True,
    username: str | None = None,
    password: str | None = None,
) -> str:
    """Build an ODBC connection string from individual parameters."""
    drv = driver or _detect_best_driver()
    parts = [
        f"DRIVER={{{drv}}}",
        f"SERVER={server}",
        f"DATABASE={database}",
    ]
    if trusted:
        parts.append("Trusted_Connection=yes")
    else:
        if username:
            parts.append(f"UID={username}")
        if password:
            parts.append(f"PWD={password}")

    # TrustServerCertificate for local dev with Driver 18+
    if "18" in drv:
        parts.append("TrustServerCertificate=yes")

    return ";".join(parts)


def _get_tables(result: GenerationResult) -> dict[str, pl.DataFrame]:
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


def write_sqlserver(
    result: GenerationResult,
    output_path: Path,                    # unused but kept for consistent writer interface
    *,
    connection_string: str | None = None,
    server: str = "localhost",
    database: str = "ContosoRetail",
    schema: str = "dbo",
    driver: str | None = None,
    trusted: bool = True,
    username: str | None = None,
    password: str | None = None,
    if_exists: str = "replace",
    batch_size: int = 5_000,
    **_extra: Any,
) -> None:
    """
    Write all tables to a SQL Server database.

    The writer will:
      1. Create the database if it doesn't exist
      2. Create/replace tables with correctly-typed columns
      3. Bulk-insert data using fast_executemany in batches

    Args:
        connection_string: Full ODBC connection string (overrides server/database/driver).
        server:       SQL Server instance (default: "localhost").
        database:     Database name (default: "ContosoRetail").
        schema:       Schema name (default: "dbo").
        driver:       ODBC driver name (auto-detected if None).
        trusted:      Use Windows Authentication (default: True).
        username:     SQL auth username (when trusted=False).
        password:     SQL auth password (when trusted=False).
        if_exists:    "replace" (drop+create), "append", or "fail".
        batch_size:   Rows per INSERT batch (default: 5000).
    """
    try:
        import pyodbc
    except ImportError as exc:
        raise ImportError(
            "The SQL Server writer needs 'pyodbc', which ships as an extra.\n"
            "  pip install 'contoso-universe-gen[sqlserver]'"
        ) from exc

    # ── Build connection string ──────────────────────────────────────────────
    if connection_string is None:
        conn_str = _build_connection_string(
            server=server,
            database=database,
            driver=driver,
            trusted=trusted,
            username=username,
            password=password,
        )
    else:
        conn_str = connection_string

    # ── Ensure database exists (connect to master first) ─────────────────────
    master_str = conn_str.replace(f"DATABASE={database}", "DATABASE=master")
    try:
        master_conn = pyodbc.connect(master_str, autocommit=True)
        cursor = master_conn.cursor()
        cursor.execute(
            f"IF NOT EXISTS (SELECT 1 FROM sys.databases WHERE name = ?) "
            f"CREATE DATABASE [{database}]",
            database,
        )
        cursor.close()
        master_conn.close()
        console.print(f"  [dim]Database [{database}] ensured[/dim]")
    except pyodbc.Error as e:
        console.print(
            f"  [yellow]⚠ Could not auto-create database: {e}. "
            f"Make sure [{database}] exists.[/yellow]"
        )

    # ── Connect to target database ───────────────────────────────────────────
    conn = pyodbc.connect(conn_str, autocommit=False)

    cursor = conn.cursor()
    cursor.fast_executemany = True

    tables = _get_tables(result)
    total_rows = 0

    for table_name, df in tables.items():
        fq_name = f"[{schema}].[{table_name}]"

        # ── Handle if_exists ─────────────────────────────────────────────────
        if if_exists == "replace":
            cursor.execute(
                f"IF OBJECT_ID('{schema}.{table_name}', 'U') IS NOT NULL "
                f"DROP TABLE {fq_name}"
            )
            conn.commit()
        elif if_exists == "fail":
            cursor.execute(
                f"SELECT OBJECT_ID('{schema}.{table_name}', 'U')"
            )
            if cursor.fetchone()[0] is not None:
                raise RuntimeError(
                    f"Table {fq_name} already exists and if_exists='fail'"
                )

        # ── Create table (for replace or first-time append) ──────────────────
        if if_exists in ("replace", "append"):
            # Check if table exists (for append, skip create)
            cursor.execute(
                f"SELECT OBJECT_ID('{schema}.{table_name}', 'U')"
            )
            table_exists = cursor.fetchone()[0] is not None

            if not table_exists:
                col_defs = []
                for col_name in df.columns:
                    sql_type = _polars_to_sql_type(df[col_name].dtype)
                    col_defs.append(f"    [{col_name}] {sql_type}")

                create_sql = (
                    f"CREATE TABLE {fq_name} (\n"
                    + ",\n".join(col_defs)
                    + "\n)"
                )
                cursor.execute(create_sql)
                conn.commit()

        # ── Bulk insert data ─────────────────────────────────────────────────
        n_rows = len(df)
        n_cols = len(df.columns)
        placeholders = ", ".join(["?"] * n_cols)
        col_list = ", ".join(f"[{c}]" for c in df.columns)
        insert_sql = f"INSERT INTO {fq_name} ({col_list}) VALUES ({placeholders})"

        # Identify column types for fast conversion
        col_types = [str(df[c].dtype).split("(")[0] for c in df.columns]

        # Convert to Python rows with ODBC-safe types
        rows = df.rows()
        clean_all = []
        for row in rows:
            clean_row = []
            for i, val in enumerate(row):
                if val is None:
                    clean_row.append(None)
                elif col_types[i] == "Boolean":
                    # BIT columns need int, not Python bool
                    clean_row.append(1 if val else 0)
                elif col_types[i] in ("Date", "Datetime"):
                    # DATE/DATETIME2 → string in ISO format
                    clean_row.append(str(val))
                elif col_types[i] == "Duration":
                    if hasattr(val, 'total_seconds'):
                        clean_row.append(int(val.total_seconds() * 1_000_000))
                    else:
                        clean_row.append(int(val))
                elif col_types[i] == "Null":
                    clean_row.append(None)
                elif col_types[i] in ("Int8", "Int16", "UInt8", "UInt16"):
                    # Ensure small ints are plain Python int for ODBC
                    clean_row.append(int(val))
                else:
                    clean_row.append(val)
            clean_all.append(tuple(clean_row))

        # Batch insert with fallback
        for batch_start in range(0, n_rows, batch_size):
            batch = clean_all[batch_start:batch_start + batch_size]

            try:
                cursor.executemany(insert_sql, batch)
                conn.commit()
            except Exception:
                # fast_executemany can fail on mixed/edge types;
                # fall back to row-by-row for this batch
                conn.rollback()
                cursor.fast_executemany = False
                for single_row in batch:
                    cursor.execute(insert_sql, single_row)
                conn.commit()
                cursor.fast_executemany = True

        total_rows += n_rows
        console.print(
            f"  [green]✔[/green] {fq_name}: "
            f"[bold]{n_rows:,}[/bold] rows"
        )

    cursor.close()
    conn.close()

    console.print(
        f"  [bold green]✔ SQL Server:[/bold green] "
        f"{len(tables)} tables, {total_rows:,} total rows → "
        f"[bold]{server}/{database}[/bold]"
    )
