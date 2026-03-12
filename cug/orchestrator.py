"""
Orchestrator — wires all generators together and produces the final datasets.
"""

from __future__ import annotations

import time
from datetime import date
from pathlib import Path
from typing import Callable

import polars as pl
from rich.console import Console
from rich.progress import Progress, SpinnerColumn, TextColumn, BarColumn, TimeElapsedColumn

from .config import AppConfig, load_config
from .models import GenerationResult
from .categories.registry import CategoryRegistry
from .generators.calendar       import generate_dim_date
from .generators.customers      import generate_dim_customer
from .generators.products       import generate_dim_product
from .generators.stores         import generate_dim_store
from .generators.currency       import generate_dim_currency
from .generators.currency_exchange import generate_dim_currency_exchange
from .generators.sales          import generate_fact_sales
from .writers                   import write_format
from .engine.validator           import validate_integrity, print_integrity_report


console = Console()



def run_generation(
    config_path: str | Path | None = None,
    config: AppConfig | None = None,
    progress_callback: Callable[[str, float], None] | None = None,
    strict_override: bool | None = None,
) -> GenerationResult:
    """
    Execute the full generation pipeline.

    Args:
        config_path:     Path to a TOML config file. Mutually exclusive with `config`.
        config:          Already-loaded AppConfig. Mutually exclusive with `config_path`.
        progress_callback: Optional function(step_name, fraction) for UI updates.
        strict_override: If not None, overrides `output.integrity_strict` from config.
                         Useful for the --strict / --no-strict CLI flags.

    Returns:
        GenerationResult with all generated DataFrames.
    """
    if config is None:
        config = load_config(config_path)

    result = GenerationResult()
    t0 = time.perf_counter()

    def _step(name: str, fraction: float):
        if progress_callback:
            progress_callback(name, fraction)

    # ── 1. Category registry ─────────────────────────────────────────────────
    _step("Loading categories", 0.02)
    registry = CategoryRegistry()
    enabled = config.categories.enabled if config.categories.enabled else None
    registry.load_builtins(enabled)
    for extra in (config.categories.custom_paths or []):
        registry.load_custom([extra])

    # ── 2. Dimension tables ──────────────────────────────────────────────────
    _step("DimDate", 0.10)
    result.dim_date = generate_dim_date(
        start=date.fromisoformat(config.general.start_date),
        end=date.fromisoformat(config.general.end_date),
        language=config.general.language,
    )

    _step("DimCurrency", 0.15)
    result.dim_currency = generate_dim_currency()

    _step("DimCurrencyExchange", 0.18)
    result.dim_currency_exchange = generate_dim_currency_exchange(
        start=date.fromisoformat(config.general.start_date),
        end=date.fromisoformat(config.general.end_date),
        seed=config.general.seed,
    )

    _step("DimCustomer", 0.22)
    result.dim_customer = generate_dim_customer(
        pool_size=config.customers.pool_size,
        language=config.general.language,
        seed=config.general.seed,
    )

    _step("DimProduct", 0.30)
    result.dim_product = generate_dim_product(
        registry=registry,
        language=config.general.language,
        seed=config.general.seed,
    )

    _step("DimStore", 0.35)
    result.dim_store = generate_dim_store(
        language=config.general.language,
        seed=config.general.seed,
    )

    # ── 3. Fact table ────────────────────────────────────────────────────────
    _step("FactSales (this may take a while...)", 0.40)
    result.fact_sales = generate_fact_sales(
        config=config,
        dim_date=result.dim_date,
        dim_customer=result.dim_customer,
        dim_product=result.dim_product,
        dim_store=result.dim_store,
    )

    # ── 4. Integrity validation (pre-write) ──────────────────────────────────
    run_check = config.output.integrity_check or (strict_override is not None)
    if run_check:
        strict = strict_override if strict_override is not None else config.output.integrity_strict
        _step("Integrity check", 0.72)
        issues = validate_integrity(result, strict=strict)
        if not issues:
            console.print("  [bold green]✔[/bold green] Integrity check passed — all FK relations OK")
        elif not strict:
            # Report mode: show findings but continue
            print_integrity_report(issues)
            console.print(
                f"  [bold yellow]⚠[/bold yellow] {len(issues)} integrity issue(s) — "
                "continuing (strict=false)"
            )
        # strict=True raises IntegrityError before reaching here

    # ── 5. Write outputs (pluggable format dispatch) ─────────────────────────
    out_path = Path(config.output.output_path)
    formats  = config.output.formats
    fmt_opts = config.output.format_options

    # Distribute progress evenly across output formats
    write_start = 0.75
    write_end   = 0.98
    n_formats   = len(formats)

    for i, fmt in enumerate(formats):
        fraction = write_start + (write_end - write_start) * (i / max(n_formats, 1))
        _step(f"Writing {fmt.upper()}", fraction)

        # Get format-specific options from config
        options = fmt_opts.for_format(fmt)

        # Special case: duckdb needs db_name as positional-ish arg
        if fmt == "duckdb":
            options["db_name"] = options.pop("db_name", fmt_opts.duckdb_db_name)

        write_format(fmt, result, out_path, **options)

    elapsed = time.perf_counter() - t0
    _step(f"Done in {elapsed:.1f}s", 1.0)
    return result
