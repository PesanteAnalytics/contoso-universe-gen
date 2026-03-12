"""
cug_eda.py — Contoso Universe Generator · Exploratory Data Analysis
====================================================================
EDA reutilizable para cualquier output generado por CUG.
Trata los datos como un modelo Star Schema (FactSales + Dims).

Uso:
    python analysis/eda.py                              # usa output/quicktest por defecto
    python analysis/eda.py --db output/myjob/contoso.duckdb
    python analysis/eda.py --parquet output/myjob/parquet/

Requisitos: duckdb, polars, rich  (ya en pyproject.toml)
"""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

import duckdb
import polars as pl
from rich import box
from rich.console import Console
from rich.panel import Panel
from rich.table import Table
from rich.rule import Rule
from rich.text import Text

console = Console()

# ── Helpers ──────────────────────────────────────────────────────────────────

def _rich_table(title: str, df: pl.DataFrame, max_rows: int = 20) -> Table:
    """Convierte un Polars DataFrame a Rich Table para display."""
    t = Table(title=title, box=box.ROUNDED, show_header=True,
              header_style="bold cyan", title_style="bold white")
    for col in df.columns:
        t.add_column(col, style="white", overflow="fold")
    for row in df.head(max_rows).iter_rows():
        t.add_row(*[str(v) if v is not None else "[dim]NULL[/dim]" for v in row])
    return t


def _section(title: str) -> None:
    console.print()
    console.print(Rule(f"[bold yellow]{title}[/bold yellow]"))


def _kpi(label: str, value, color: str = "green") -> str:
    return f"[{color}]{value}[/{color}]  [dim]{label}[/dim]"


# ── Conexión ──────────────────────────────────────────────────────────────────

def connect(db_path: Path | None = None, parquet_dir: Path | None = None) -> duckdb.DuckDBPyConnection:
    """
    Conecta al modelo.  Prioridad: DuckDB > Parquet.
    Si se pasa parquet_dir, carga cada .parquet como vista con el nombre de la tabla.
    """
    con = duckdb.connect()

    if db_path and db_path.exists():
        console.print(f"[bold green]✔[/bold green] Conectado a DuckDB: [cyan]{db_path}[/cyan]")
        con = duckdb.connect(str(db_path), read_only=True)

    elif parquet_dir and parquet_dir.exists():
        console.print(f"[bold green]✔[/bold green] Cargando Parquet desde: [cyan]{parquet_dir}[/cyan]")
        for f in sorted(parquet_dir.glob("*.parquet")):
            table_name = f.stem          # DimDate.parquet → DimDate
            con.execute(f"CREATE VIEW {table_name} AS SELECT * FROM read_parquet('{f.as_posix()}')")
            console.print(f"  [dim]→ {table_name}[/dim]")

    else:
        console.print("[red]❌ No se encontró DuckDB ni directorio Parquet.[/red]")
        sys.exit(1)

    return con


# ── 1 · Inventario del modelo ─────────────────────────────────────────────────

def section_model_inventory(con: duckdb.DuckDBPyConnection) -> None:
    _section("1 · Inventario del Modelo")

    tables = con.execute("""
        SELECT table_name
        FROM information_schema.tables
        WHERE table_schema = 'main'
        ORDER BY table_name
    """).fetchdf()

    rows = []
    for tbl in tables["table_name"].tolist():
        cnt = con.execute(f"SELECT COUNT(*) FROM {tbl}").fetchone()[0]
        cols = con.execute(f"""
            SELECT COUNT(*) FROM information_schema.columns
            WHERE table_name = '{tbl}'
        """).fetchone()[0]
        rows.append((tbl, f"{cnt:,}", str(cols)))

    t = Table(title="Tablas del Modelo", box=box.ROUNDED,
              header_style="bold magenta", title_style="bold white")
    t.add_column("Tabla", style="cyan bold")
    t.add_column("Filas", justify="right", style="green")
    t.add_column("Columnas", justify="right")
    for r in rows:
        t.add_row(*r)

    console.print(t)


# ── 2 · Schema por tabla ──────────────────────────────────────────────────────

def section_schema(con: duckdb.DuckDBPyConnection) -> None:
    _section("2 · Schema (tipos de datos)")

    tables = con.execute("""
        SELECT DISTINCT table_name FROM information_schema.columns
        WHERE table_schema = 'main' ORDER BY table_name
    """).fetchdf()["table_name"].tolist()

    for tbl in tables:
        schema_df = pl.from_pandas(con.execute(f"""
            SELECT column_name, data_type
            FROM information_schema.columns
            WHERE table_name = '{tbl}'
            ORDER BY ordinal_position
        """).fetchdf())
        console.print(_rich_table(f"Schema · {tbl}", schema_df))


# ── 3 · KPIs del FactSales ────────────────────────────────────────────────────

def section_fact_kpis(con: duckdb.DuckDBPyConnection) -> None:
    _section("3 · KPIs · FactSales")

    row = con.execute("""
        SELECT
            COUNT(*)                        AS total_orders,
            SUM(Quantity)                   AS total_units,
            ROUND(SUM(SalesAmount), 2)      AS total_revenue,
            ROUND(AVG(SalesAmount), 2)      AS avg_order_value,
            ROUND(SUM(GrossMargin), 2)      AS total_margin,
            ROUND(SUM(GrossMargin)/NULLIF(SUM(SalesAmount),0)*100, 1) AS margin_pct,
            ROUND(AVG(Discount)*100, 1)     AS avg_discount_pct,
            MIN(OrderDateKey)               AS date_min,
            MAX(OrderDateKey)               AS date_max
        FROM FactSales
    """).fetchone()

    keys = ["Orders","Units","Revenue $","AOV $","Margin $","Margin %","Avg Discount %","Date Min","Date Max"]
    text = "  ".join(_kpi(k, v) for k, v in zip(keys, row))

    console.print(Panel(text, title="[bold]FactSales · KPIs Globales[/bold]", expand=False))


# ── 4 · Revenue por Año/Mes ───────────────────────────────────────────────────

def section_revenue_by_period(con: duckdb.DuckDBPyConnection) -> None:
    _section("4 · Revenue por Año y Mes")

    df = pl.from_pandas(con.execute("""
        SELECT
            d.Year,
            d.Month,
            d.MonthName,
            COUNT(f.SalesKey)               AS Orders,
            ROUND(SUM(f.SalesAmount), 2)    AS Revenue,
            ROUND(SUM(f.GrossMargin), 2)    AS Margin,
            ROUND(AVG(f.SalesAmount), 2)    AS AOV
        FROM FactSales f
        JOIN DimDate d ON f.OrderDateKey = d.DateKey
        GROUP BY d.Year, d.Month, d.MonthName
        ORDER BY d.Year, d.Month
    """).fetchdf())

    console.print(_rich_table("Revenue Mensual", df, max_rows=36))


# ── 5 · Top Categorías ────────────────────────────────────────────────────────

def section_top_categories(con: duckdb.DuckDBPyConnection) -> None:
    _section("5 · Revenue por Categoría")

    df = pl.from_pandas(con.execute("""
        SELECT
            p.CategoryName,
            COUNT(f.SalesKey)                                          AS Orders,
            ROUND(SUM(f.SalesAmount), 2)                               AS Revenue,
            ROUND(SUM(f.GrossMargin), 2)                               AS Margin,
            ROUND(SUM(f.GrossMargin)/NULLIF(SUM(f.SalesAmount),0)*100, 1) AS Margin_pct,
            ROUND(AVG(f.Discount)*100, 1)                              AS AvgDiscount_pct
        FROM FactSales f
        JOIN DimProduct p ON f.ProductKey = p.ProductKey
        GROUP BY p.CategoryName
        ORDER BY Revenue DESC
    """).fetchdf())

    console.print(_rich_table("Categorías · Top Revenue", df))


# ── 6 · Top Productos ─────────────────────────────────────────────────────────

def section_top_products(con: duckdb.DuckDBPyConnection) -> None:
    _section("6 · Top 15 Productos")

    df = pl.from_pandas(con.execute("""
        SELECT
            p.ProductName,
            p.CategoryName,
            p.Brand,
            COUNT(f.SalesKey)            AS Orders,
            SUM(f.Quantity)              AS Units,
            ROUND(SUM(f.SalesAmount),2)  AS Revenue
        FROM FactSales f
        JOIN DimProduct p ON f.ProductKey = p.ProductKey
        GROUP BY p.ProductName, p.CategoryName, p.Brand
        ORDER BY Revenue DESC
        LIMIT 15
    """).fetchdf())

    console.print(_rich_table("Top 15 Productos", df))


# ── 7 · Canales de Venta (Stores) ────────────────────────────────────────────

def section_channels(con: duckdb.DuckDBPyConnection) -> None:
    _section("7 · Canales de Venta (Stores)")

    df = pl.from_pandas(con.execute("""
        SELECT
            s.Channel,
            COUNT(DISTINCT s.StoreKey)     AS Stores,
            COUNT(f.SalesKey)              AS Orders,
            ROUND(SUM(f.SalesAmount),2)    AS Revenue,
            ROUND(AVG(f.SalesAmount),2)    AS AOV
        FROM FactSales f
        JOIN DimStore s ON f.StoreKey = s.StoreKey
        GROUP BY s.Channel
        ORDER BY Revenue DESC
    """).fetchdf())

    console.print(_rich_table("Canales de Venta", df))


# ── 8 · Clientes ──────────────────────────────────────────────────────────────

def section_customers(con: duckdb.DuckDBPyConnection) -> None:
    _section("8 · Análisis de Clientes")

    # Segmentación por género
    df_gender = pl.from_pandas(con.execute("""
        SELECT
            c.Gender,
            COUNT(DISTINCT f.CustomerKey)  AS Customers,
            COUNT(f.SalesKey)              AS Orders,
            ROUND(SUM(f.SalesAmount),2)    AS Revenue
        FROM FactSales f
        JOIN DimCustomer c ON f.CustomerKey = c.CustomerKey
        GROUP BY c.Gender
        ORDER BY Revenue DESC
    """).fetchdf())
    console.print(_rich_table("Clientes · por Género", df_gender))

    # Top 10 clientes por revenue
    df_top = pl.from_pandas(con.execute("""
        SELECT
            c.CustomerKey,
            c.FirstName || ' ' || c.LastName AS Customer,
            c.Country,
            COUNT(f.SalesKey)              AS Orders,
            ROUND(SUM(f.SalesAmount),2)    AS Revenue
        FROM FactSales f
        JOIN DimCustomer c ON f.CustomerKey = c.CustomerKey
        GROUP BY c.CustomerKey, Customer, c.Country
        ORDER BY Revenue DESC
        LIMIT 10
    """).fetchdf())
    console.print(_rich_table("Top 10 Clientes", df_top))


# ── 9 · Integridad referencial ────────────────────────────────────────────────

def section_referential_integrity(con: duckdb.DuckDBPyConnection) -> None:
    _section("9 · Integridad Referencial")

    checks = {
        "FactSales → DimDate (OrderDateKey)": """
            SELECT COUNT(*) FROM FactSales f
            LEFT JOIN DimDate d ON f.OrderDateKey = d.DateKey
            WHERE d.DateKey IS NULL
        """,
        "FactSales → DimCustomer": """
            SELECT COUNT(*) FROM FactSales f
            LEFT JOIN DimCustomer c ON f.CustomerKey = c.CustomerKey
            WHERE c.CustomerKey IS NULL
        """,
        "FactSales → DimProduct": """
            SELECT COUNT(*) FROM FactSales f
            LEFT JOIN DimProduct p ON f.ProductKey = p.ProductKey
            WHERE p.ProductKey IS NULL
        """,
        "FactSales → DimStore": """
            SELECT COUNT(*) FROM FactSales f
            LEFT JOIN DimStore s ON f.StoreKey = s.StoreKey
            WHERE s.StoreKey IS NULL
        """,
        "FactSales → DimCurrency": """
            SELECT COUNT(*) FROM FactSales f
            LEFT JOIN DimCurrency c ON f.CurrencyKey = c.CurrencyKey
            WHERE c.CurrencyKey IS NULL
        """,
    }

    t = Table(title="Integridad Referencial", box=box.ROUNDED,
              header_style="bold magenta", title_style="bold white")
    t.add_column("Relación", style="cyan")
    t.add_column("Huérfanos", justify="right")
    t.add_column("Estado", justify="center")

    for label, sql in checks.items():
        orphans = con.execute(sql).fetchone()[0]
        status = "[bold green]✔ OK[/bold green]" if orphans == 0 else f"[bold red]✘ {orphans:,}[/bold red]"
        t.add_row(label, str(orphans), status)

    console.print(t)


# ── 10 · Análisis de NULLs ───────────────────────────────────────────────────

def section_null_analysis(con: duckdb.DuckDBPyConnection) -> None:
    _section("10 · Análisis de NULLs")

    tables = con.execute("""
        SELECT DISTINCT table_name FROM information_schema.columns
        WHERE table_schema = 'main'
          AND table_name NOT LIKE 'v_%'
        ORDER BY table_name
    """).fetchdf()["table_name"].tolist()

    for tbl in tables:
        cols = con.execute(f"""
            SELECT column_name FROM information_schema.columns
            WHERE table_name = '{tbl}' ORDER BY ordinal_position
        """).fetchdf()["column_name"].tolist()

        total = con.execute(f"SELECT COUNT(*) FROM {tbl}").fetchone()[0]
        null_cols = []
        for col in cols:
            nulls = con.execute(f'SELECT COUNT(*) FROM {tbl} WHERE "{col}" IS NULL').fetchone()[0]
            if nulls > 0:
                pct = round(nulls / total * 100, 1)
                null_cols.append((col, f"{nulls:,}", f"{pct}%"))

        if null_cols:
            t = Table(title=f"NULLs · {tbl}", box=box.SIMPLE, header_style="bold yellow")
            t.add_column("Columna", style="cyan")
            t.add_column("NULLs", justify="right", style="red")
            t.add_column("%", justify="right")
            for r in null_cols:
                t.add_row(*r)
            console.print(t)
        else:
            console.print(f"  [green]✔ {tbl}[/green] — sin NULLs")


# ── Main ──────────────────────────────────────────────────────────────────────

def run_eda(db_path: Path | None, parquet_dir: Path | None) -> None:
    console.print(Panel.fit(
        "[bold cyan]Contoso Universe Generator[/bold cyan]\n[dim]Exploratory Data Analysis · Star Schema Model[/dim]",
        border_style="cyan"
    ))

    con = connect(db_path, parquet_dir)

    section_model_inventory(con)
    section_schema(con)
    section_fact_kpis(con)
    section_revenue_by_period(con)
    section_top_categories(con)
    section_top_products(con)
    section_channels(con)
    section_customers(con)
    section_referential_integrity(con)
    section_null_analysis(con)

    console.print()
    console.print(Panel("[bold green]✅ EDA Completo[/bold green]", expand=False))
    con.close()


def main() -> None:
    parser = argparse.ArgumentParser(
        description="CUG EDA — Exploratory Data Analysis para outputs de Contoso Universe Generator"
    )
    parser.add_argument(
        "--db", type=Path, default=None,
        help="Ruta al archivo .duckdb (default: output/quicktest/contoso_test.duckdb)"
    )
    parser.add_argument(
        "--parquet", type=Path, default=None,
        help="Ruta al directorio con archivos .parquet (fallback si no hay --db)"
    )
    args = parser.parse_args()

    # Defaults inteligentes
    project_root = Path(__file__).resolve().parent.parent
    db_path     = args.db     or project_root / "output" / "quicktest" / "contoso_test.duckdb"
    parquet_dir = args.parquet or project_root / "output" / "quicktest" / "parquet"

    run_eda(db_path if db_path.exists() else None,
            parquet_dir if (not db_path or not db_path.exists()) else None)


if __name__ == "__main__":
    main()
