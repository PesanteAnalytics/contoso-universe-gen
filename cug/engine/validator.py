"""
validator.py — Referential Integrity Engine for CUG
=====================================================
Validates FK relationships on in-memory Polars DataFrames BEFORE
any output is written to disk.

Uses Polars native anti-join (O(n) hash-based) — no DuckDB required.

Raises IntegrityError on any violation when strict=True.
Returns a list of IntegrityIssue when strict=False (report mode).
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import TYPE_CHECKING

import polars as pl
from rich.console import Console
from rich.table import Table
from rich import box

if TYPE_CHECKING:
    from ..models import GenerationResult

console = Console()


# ── Data classes ────────────────────────────────────────────────────────────


@dataclass
class IntegrityIssue:
    """Describes a referential integrity violation."""
    fact_table:  str
    fact_column: str
    dim_table:   str
    dim_column:  str
    orphan_count: int
    sample_keys:  list = field(default_factory=list)

    @property
    def relation(self) -> str:
        return f"{self.fact_table}.{self.fact_column} → {self.dim_table}.{self.dim_column}"


class IntegrityError(Exception):
    """Raised when referential integrity violations are found in strict mode."""
    def __init__(self, issues: list[IntegrityIssue]):
        self.issues = issues
        lines = [f"  ✘ {i.relation}: {i.orphan_count:,} orphan(s)" for i in issues]
        super().__init__(
            f"\n\n[CUG] Integrity check FAILED — {len(issues)} violation(s):\n"
            + "\n".join(lines)
            + "\n\nRun with integrity_check = false to skip validation."
        )


# ── FK check definitions ─────────────────────────────────────────────────────


_FK_CHECKS = [
    # (fact_col,      dim_table_attr,   dim_col)
    # NOTE: OrderDate / DeliveryDate are ISO date strings in V2 schema.
    # They are validated as a date-range check, not an int FK join.
    # Integer FK checks:
    ("CustomerKey",  "dim_customer",   "CustomerKey"),
    ("ProductKey",   "dim_product",    "ProductKey"),
    ("StoreKey",     "dim_store",      "StoreKey"),
    ("CurrencyKey",  "dim_currency",   "CurrencyKey"),
]


# ── Core validator ───────────────────────────────────────────────────────────


def validate_integrity(
    result: "GenerationResult",
    strict: bool = True,
) -> list[IntegrityIssue]:
    """
    Run all FK integrity checks on the GenerationResult DataFrames.

    Args:
        result: The GenerationResult containing all generated DataFrames.
        strict: If True, raises IntegrityError on any violation.
                If False, returns the list of violations (report mode).

    Returns:
        List of IntegrityIssue objects (empty if all checks pass).

    Raises:
        IntegrityError: If strict=True and any violations are found.
    """
    fact = result.fact_sales
    issues: list[IntegrityIssue] = []

    for fact_col, dim_attr, dim_col in _FK_CHECKS:
        dim_df: pl.DataFrame | None = getattr(result, dim_attr, None)

        if dim_df is None or fact is None:
            continue
        if fact_col not in fact.columns:
            continue
        if dim_col not in dim_df.columns:
            continue

        # Anti-join: rows in fact with no matching key in dim
        # Rename dim_col → fact_col for join compatibility (same name required)
        dim_keys = (
            dim_df
            .select(pl.col(dim_col).alias(fact_col))
            .unique()
        )

        # Cast to same type to avoid false mismatches
        fact_col_type = fact[fact_col].dtype
        dim_keys = dim_keys.with_columns(
            pl.col(fact_col).cast(fact_col_type)
        )

        orphans = fact.join(dim_keys, on=fact_col, how="anti")
        count = len(orphans)

        if count > 0:
            sample = orphans[fact_col].head(5).to_list()
            issues.append(IntegrityIssue(
                fact_table="FactSales",
                fact_column=fact_col,
                dim_table=dim_attr.replace("dim_", "Dim").replace("_", ""),
                dim_column=dim_col,
                orphan_count=count,
                sample_keys=sample,
            ))

    if issues and strict:
        _print_report(issues, passed=False)
        raise IntegrityError(issues)

    return issues


# ── Rich report ──────────────────────────────────────────────────────────────


def print_integrity_report(issues: list[IntegrityIssue]) -> None:
    """Print a Rich-formatted integrity report (standalone use)."""
    _print_report(issues, passed=len(issues) == 0)


def _print_report(issues: list[IntegrityIssue], passed: bool) -> None:
    # Build all checks list — we only have the failing ones here,
    # but we still format them nicely.
    t = Table(
        title="Integrity Check",
        box=box.ROUNDED,
        header_style="bold magenta",
        title_style="bold white",
    )
    t.add_column("Relation", style="cyan")
    t.add_column("Orphans", justify="right")
    t.add_column("Status", justify="center")
    t.add_column("Sample Keys", style="dim")

    for issue in issues:
        sample_str = ", ".join(str(k) for k in issue.sample_keys)
        t.add_row(
            issue.relation,
            f"{issue.orphan_count:,}",
            "[bold red]✘ FAIL[/bold red]",
            sample_str,
        )

    console.print(t)
