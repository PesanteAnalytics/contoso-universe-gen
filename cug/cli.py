"""
CUG — Contoso Universe Generator CLI

Usage:
    cug generate [OPTIONS]
    cug info
    cug categories
    cug formats
    cug init [OUTPUT_DIR]
"""

from __future__ import annotations

import io
import sys

# ── Windows cp1252 → UTF-8 fix ────────────────────────────────────────────────
# Rich box-drawing characters require UTF-8.  When the console script entry
# point is invoked the default Windows codec is cp1252; reconfigure early.
for _stream_name in ("stdout", "stderr"):
    _stream = getattr(sys, _stream_name)
    if hasattr(_stream, "buffer") and getattr(_stream, "encoding", "").lower() != "utf-8":
        setattr(sys, _stream_name, io.TextIOWrapper(_stream.buffer, encoding="utf-8", errors="replace"))
from pathlib import Path

import typer
from rich.console import Console
from rich.progress import BarColumn, Progress, SpinnerColumn, TextColumn, TimeElapsedColumn
from rich.table import Table

from .categories.registry import CategoryRegistry
from .config import SUPPORTED_FORMATS, load_config
from .i18n import list_locales, locale_coverage

console = Console(highlight=True)
app = typer.Typer(
    name="cug",
    help="[bold cyan]Contoso Universe Generator[/bold cyan] — High-performance synthetic data for analytics.",
    rich_markup_mode="rich",
    no_args_is_help=True,
)


# ─── ASCII Banner ──────────────────────────────────────────────────────────────

BANNER = """
[bold cyan]
 ██████╗██╗   ██╗ ██████╗
██╔════╝██║   ██║██╔════╝
██║     ██║   ██║██║  ███╗
██║     ██║   ██║██║   ██║
╚██████╗╚██████╔╝╚██████╔╝
 ╚═════╝ ╚═════╝  ╚═════╝
[/bold cyan][dim]Contoso Universe Generator  •  v0.2.0[/dim]
"""


@app.callback(invoke_without_command=True)
def main(ctx: typer.Context):
    """Show banner when no subcommand given."""
    if ctx.invoked_subcommand is None:
        console.print(BANNER)


# ─── generate ────────────────────────────────────────────────────────────────

@app.command()
def generate(
    config: Path | None = typer.Option(
        None,
        "--config", "-c",
        help="Path to TOML config file. Defaults to built-in default.toml.",
        exists=True,
        file_okay=True,
    ),
    output: Path | None = typer.Option(
        None,
        "--output", "-o",
        help="Output directory. Overrides config.",
    ),
    language: str | None = typer.Option(
        None,
        "--language", "-l",
        help="Language code (en, es, pt, fr, de, zh, ja, ar). Overrides config.",
    ),
    orders: int | None = typer.Option(
        None,
        "--orders", "-n",
        help="Target order count. Overrides config.",
    ),
    formats: str | None = typer.Option(
        None,
        "--formats", "-f",
        help=(
            "Comma-separated output formats. "
            f"Available: {', '.join(sorted(SUPPORTED_FORMATS))}. "
            "Default: parquet"
        ),
    ),
    seed: int | None = typer.Option(
        None,
        "--seed",
        help="Random seed for reproducibility.",
    ),
    # ── Format-specific CLI overrides ─────────────────────────────────────────
    parquet_compression: str | None = typer.Option(
        None,
        "--parquet-compression",
        help="Parquet compression: zstd (default), snappy, gzip, lz4, brotli, none.",
    ),
    csv_separator: str | None = typer.Option(
        None,
        "--csv-separator",
        help="CSV field delimiter (default: comma).",
    ),
    delta_mode: str | None = typer.Option(
        None,
        "--delta-mode",
        help="Delta Lake write mode: overwrite (default), append, error.",
    ),
    json_row_oriented: bool | None = typer.Option(
        None,
        "--json-rows/--json-ndjson",
        help="JSON: array of objects vs NDJSON (default: NDJSON).",
    ),
    excel_single_workbook: bool | None = typer.Option(
        None,
        "--excel-single/--excel-multi",
        help="Excel: one workbook (default) vs one per table.",
    ),
    # ── SQL Server CLI overrides ──────────────────────────────────────────────
    sqlserver_server: str | None = typer.Option(
        None,
        "--sqlserver-name",
        help="SQL Server instance (default: localhost). E.g. localhost\\SQLEXPRESS.",
    ),
    sqlserver_database: str | None = typer.Option(
        None,
        "--sqlserver-db",
        help="Target database name (default: ContosoRetail).",
    ),
    sqlserver_schema: str | None = typer.Option(
        None,
        "--sqlserver-schema",
        help="Target schema (default: dbo).",
    ),
    sqlserver_if_exists: str | None = typer.Option(
        None,
        "--sqlserver-mode",
        help="If table exists: replace (default), append, fail.",
    ),
    verify: bool | None = typer.Option(
        None,
        "--verify/--no-verify",
        help="Run FK integrity validation before writing. Overrides integrity_check.",
    ),
    strict: bool | None = typer.Option(
        None,
        "--strict/--no-strict",
        help="Abort on FK violations instead of reporting them. Implies --verify.",
    ),
    verbose: bool = typer.Option(False, "--verbose", "-v", help="Show detailed progress."),
):
    """
    [bold green]Generate[/bold green] a full Contoso dataset.

    Output format defaults to [bold]parquet[/bold]. Override with --formats.

    Examples:

        cug generate

        cug generate -c configs/retail_1M_es.toml -o ./output -n 500000

        cug generate --formats parquet,csv --parquet-compression snappy

        cug generate --formats delta --delta-mode overwrite

        cug generate --formats json --json-rows

        cug generate --formats parquet,duckdb,delta

        cug generate --formats sqlserver --sqlserver-db ContosoRetail
    """
    from .orchestrator import run_generation

    console.print(BANNER)

    # Load and possibly override config
    cfg = load_config(config)

    if output:
        cfg.output.output_path = str(output)
    if language:
        cfg.general.language = language
    if orders:
        cfg.output.target_orders = orders
    if seed:
        cfg.general.seed = seed
    if formats:
        cfg.output.formats = [f.strip().lower() for f in formats.split(",")]

    # Apply format-specific CLI overrides
    fo = cfg.output.format_options
    if parquet_compression is not None:
        fo.parquet_compression = parquet_compression
    if csv_separator is not None:
        fo.csv_separator = csv_separator
    if delta_mode is not None:
        fo.delta_mode = delta_mode
    if json_row_oriented is not None:
        fo.json_row_oriented = json_row_oriented
    if excel_single_workbook is not None:
        fo.excel_single_workbook = excel_single_workbook
    if sqlserver_server is not None:
        fo.sqlserver_server = sqlserver_server
    if sqlserver_database is not None:
        fo.sqlserver_database = sqlserver_database
    if sqlserver_schema is not None:
        fo.sqlserver_schema = sqlserver_schema
    if sqlserver_if_exists is not None:
        fo.sqlserver_if_exists = sqlserver_if_exists

    # Print job summary
    summary_table = Table(title="Generation Job", show_header=False, border_style="cyan")
    summary_table.add_column("Parameter", style="bold")
    summary_table.add_column("Value", style="green")
    summary_table.add_row("Config",    str(config or "default"))
    summary_table.add_row("Language",  cfg.general.language)
    summary_table.add_row("Date range",f"{cfg.general.start_date} → {cfg.general.end_date}")
    summary_table.add_row("Target orders", f"{cfg.output.target_orders:,}")
    summary_table.add_row("Customers",     f"{cfg.customers.pool_size:,}")
    summary_table.add_row("Formats",       ", ".join(cfg.output.formats))
    summary_table.add_row("Output",        cfg.output.output_path)

    # Show active format options
    for fmt in cfg.output.formats:
        opts = fo.for_format(fmt)
        non_default = {k: v for k, v in opts.items() if v is not None}
        if non_default:
            opts_str = ", ".join(f"{k}={v}" for k, v in non_default.items())
            summary_table.add_row(f"  └ {fmt}", f"[dim]{opts_str}[/dim]")

    # Integrity check summary row — resolved by the same rule the pipeline uses,
    # so the panel cannot claim "disabled" while the check runs.
    from .orchestrator import resolve_integrity_check

    _ic_enabled, _ic_strict = resolve_integrity_check(cfg, verify, strict)
    if _ic_enabled:
        _ic_label = "[bold red]strict[/bold red]" if _ic_strict else "[yellow]report-only[/yellow]"
        summary_table.add_row("Integrity check", _ic_label)
    else:
        summary_table.add_row("Integrity check", "[dim]disabled[/dim]")
    console.print(summary_table)
    console.print()

    steps_done: list[str] = []

    with Progress(
        SpinnerColumn(),
        TextColumn("[progress.description]{task.description}"),
        BarColumn(),
        TimeElapsedColumn(),
        console=console,
        transient=False,
    ) as progress:
        task_id = progress.add_task("Initializing...", total=100)

        def _on_progress(step: str, fraction: float):
            pct = int(fraction * 100)
            progress.update(task_id, completed=pct, description=f"[cyan]{step}[/cyan]")
            if verbose:
                steps_done.append(f"  ✓ {step}")

        result = run_generation(
            config=cfg,
            progress_callback=_on_progress,
            strict_override=strict,
            check_override=verify,
        )

    # Results summary
    console.print()
    res_table = Table(title="[bold green]✅ Generation Complete[/bold green]", border_style="green")
    res_table.add_column("Table",   style="bold cyan")
    res_table.add_column("Rows",    justify="right", style="yellow")

    for name, count in result.summary().items():
        res_table.add_row(name, f"{count:,}")

    console.print(res_table)
    console.print(f"\n[dim]Output saved to:[/dim] [bold]{cfg.output.output_path}[/bold]")
    console.print(f"[dim]Formats written:[/dim] [bold]{', '.join(cfg.output.formats)}[/bold]\n")


# ─── formats ──────────────────────────────────────────────────────────────────

@app.command()
def formats():
    """Show all available output [bold]formats[/bold] and their options."""
    console.print(BANNER)

    fmt_table = Table(
        title="Available Output Formats",
        border_style="cyan",
    )
    fmt_table.add_column("Format",      style="bold cyan")
    fmt_table.add_column("Description", style="green")
    fmt_table.add_column("Options",     style="dim")
    fmt_table.add_column("Best For",    style="yellow")

    fmt_table.add_row(
        "parquet ★",
        "Apache Parquet columnar format",
        "compression, row_group_size",
        "Power BI, Spark, analytical workloads",
    )
    fmt_table.add_row(
        "csv",
        "CSV flat files",
        "separator, header, null_value, date_format",
        "Universal compatibility, Excel import",
    )
    fmt_table.add_row(
        "duckdb",
        "Embedded DuckDB database with views",
        "db_name",
        "SQL analytics, DBeaver, Python notebooks",
    )
    fmt_table.add_row(
        "delta",
        "Delta Lake tables",
        "mode, partition_by, name",
        "Microsoft Fabric, Databricks, Spark",
    )
    fmt_table.add_row(
        "json",
        "JSON / NDJSON files",
        "row_oriented, pretty",
        "APIs, streaming ingestion, web apps",
    )
    fmt_table.add_row(
        "excel",
        "Excel .xlsx workbooks",
        "single_workbook, workbook_name",
        "Business users, quick exploration",
    )
    fmt_table.add_row(
        "sqlserver",
        "Microsoft SQL Server database",
        "server, database, schema, driver, if_exists, batch_size",
        "Enterprise BI, Power BI DirectQuery, SSAS",
    )

    console.print(fmt_table)
    console.print()
    console.print("[dim]★ = default format when none specified[/dim]")
    console.print()
    console.print("[bold]Examples:[/bold]")
    console.print("  cug generate --formats parquet")
    console.print("  cug generate --formats csv,parquet --csv-separator ';'")
    console.print("  cug generate --formats delta --delta-mode overwrite")
    console.print("  cug generate --formats parquet,duckdb,json")
    console.print("  cug generate --formats sqlserver --sqlserver-db ContosoRetail")
    console.print()


# ─── info ─────────────────────────────────────────────────────────────────────

@app.command()
def info():
    """Show available languages and their locale details."""
    console.print(BANNER)

    lang_table = Table(title="Supported Languages", border_style="cyan")
    lang_table.add_column("Code",     style="bold cyan")
    lang_table.add_column("Name",     style="green")
    lang_table.add_column("Locale",   style="dim")
    lang_table.add_column("Country",  style="dim")
    lang_table.add_column("Catalog",  justify="center")
    lang_table.add_column("Calendar", justify="center")
    lang_table.add_column("People",   justify="center")

    def _mark(covered: bool) -> str:
        return "[green]✔[/green]" if covered else "[dim]en[/dim]"

    for loc in list_locales():
        cov = locale_coverage(loc.code)
        lang_table.add_row(
            loc.code, loc.display_name, loc.locale_tag, loc.country_default,
            _mark(cov["catalog"]), _mark(cov["calendar"]), _mark(cov["people"]),
        )

    console.print(lang_table)
    console.print(
        "[dim]Catalog = product categories · Calendar = month and day names · "
        "People = customer names, cities and stores.\n"
        "'en' marks a column that falls back to English for that language.[/dim]"
    )


# ─── categories ──────────────────────────────────────────────────────────────

@app.command()
def categories(
    language: str = typer.Option("en", "--language", "-l", help="Language for display names."),
):
    """List all available product [bold]categories[/bold] and subcategories."""
    console.print(BANNER)

    registry = CategoryRegistry()
    registry.load_builtins()

    cat_table = Table(
        title=f"Product Categories ({language.upper()})",
        border_style="cyan",
    )
    cat_table.add_column("Category",    style="bold cyan")
    cat_table.add_column("Subcategory", style="green")
    cat_table.add_column("Brands",      style="dim")
    cat_table.add_column("Price Range", style="yellow")

    for plugin in registry.all():
        cat_name = plugin.display_name(language)
        for sub in plugin.subcategories:
            sub_name = sub.display_names.get(language) or sub.display_names.get("en", sub.id)
            brands   = ", ".join(sub.brands[:3]) + ("…" if len(sub.brands) > 3 else "")
            price    = f"${sub.price_range[0]:,.0f} – ${sub.price_range[1]:,.0f}"
            cat_table.add_row(cat_name, sub_name, brands, price)

    console.print(cat_table)


# ─── init ────────────────────────────────────────────────────────────────────

@app.command()
def init(
    output_dir: Path = typer.Argument(
        Path("."),
        help="Directory where default.toml will be copied.",
    )
):
    """Copy the default config template to a directory for customization."""
    import shutil
    src = Path(__file__).parent.parent / "configs" / "default.toml"
    dest = Path(output_dir) / "my_config.toml"
    dest.parent.mkdir(parents=True, exist_ok=True)
    shutil.copy(src, dest)
    console.print(f"[green]✅ Config template created:[/green] [bold]{dest}[/bold]")
    console.print("[dim]Edit it, then run:[/dim] [bold]cug generate -c my_config.toml[/bold]")


# ─── Entry-point ──────────────────────────────────────────────────────────────

def entry_point():
    app()


if __name__ == "__main__":
    entry_point()
