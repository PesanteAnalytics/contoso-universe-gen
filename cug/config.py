"""
Contoso Universe Generator — Configuration Schema
Pydantic v2 models for parsing and validating TOML configuration files.
"""

from __future__ import annotations

import tomllib
from datetime import date, datetime
from pathlib import Path
from typing import Any

from pydantic import BaseModel, Field, field_validator, model_validator


# Canonical set of supported output formats.
# Defined here (not in writers) to avoid circular imports.
SUPPORTED_FORMATS = {"csv", "parquet", "duckdb", "delta", "json", "excel", "sqlserver"}


# ---------------------------------------------------------------------------
# Sub-models
# ---------------------------------------------------------------------------

class GeneralConfig(BaseModel):
    start_date: str = Field(default="2018-01-01", description="Start date YYYY-MM-DD")
    end_date: str = Field(default="2026-12-31",   description="End date YYYY-MM-DD")
    language: str = Field(default="en",           description="ISO 639-1 language code")
    country: str  = Field(default="US",           description="ISO 3166-1 alpha-2 country for holidays")
    seed: int     = Field(default=42,             description="Master random seed")
    chunk_days: int = Field(default=30, gt=0,     description="Processing chunk size in days")

    @field_validator("language")
    @classmethod
    def validate_language(cls, v: str) -> str:
        supported = {"en", "es", "pt", "fr", "de", "zh", "ja", "ar"}
        if v not in supported:
            raise ValueError(f"Language '{v}' not supported. Choose from: {sorted(supported)}")
        return v

    @model_validator(mode="after")
    def validate_date_range(self) -> "GeneralConfig":
        start = date.fromisoformat(self.start_date)
        end   = date.fromisoformat(self.end_date)
        if start >= end:
            raise ValueError("start_date must be before end_date")
        return self


class FormatOptionsConfig(BaseModel):
    """Per-format options that can be set in the TOML config."""

    # ── Parquet ───────────────────────────────────────────────────────────────
    parquet_compression: str = Field(
        default="zstd",
        description="Parquet compression: zstd, snappy, gzip, lz4, brotli, none",
    )
    parquet_row_group_size: int | None = Field(
        default=None,
        description="Parquet row group size (None = let Polars decide)",
    )

    # ── CSV ────────────────────────────────────────────────────────────────────
    csv_separator: str = Field(default=",", description="CSV field delimiter")
    csv_include_header: bool = Field(default=True, description="Include header row in CSV")
    csv_null_value: str = Field(default="", description="Null representation in CSV")
    csv_date_format: str | None = Field(
        default=None,
        description="Date format for CSV (None = ISO 8601)",
    )

    # ── DuckDB ────────────────────────────────────────────────────────────────
    duckdb_db_name: str = Field(default="contoso.duckdb", description="DuckDB database filename")

    # ── Delta Lake ────────────────────────────────────────────────────────────
    delta_mode: str = Field(
        default="overwrite",
        description="Delta write mode: overwrite, append, error",
    )
    delta_partition_by: list[str] | None = Field(
        default=None,
        description="Columns to partition FactSales by (e.g. ['Year'])",
    )
    delta_name: str = Field(default="contoso", description="Metadata name for Delta log")

    # ── JSON ──────────────────────────────────────────────────────────────────
    json_row_oriented: bool = Field(
        default=False,
        description="True = JSON array of objects; False = NDJSON (default)",
    )
    json_pretty: bool = Field(
        default=False,
        description="Pretty-print JSON (only with row_oriented=True)",
    )

    # ── Excel ─────────────────────────────────────────────────────────────────
    excel_single_workbook: bool = Field(
        default=True,
        description="True = all tables in one workbook; False = one per table",
    )
    excel_workbook_name: str = Field(
        default="contoso.xlsx",
        description="Filename when single_workbook=True",
    )

    # ── SQL Server ────────────────────────────────────────────────────────────
    sqlserver_connection_string: str | None = Field(
        default=None,
        description="Full ODBC connection string (overrides server/database/driver)",
    )
    sqlserver_server: str = Field(
        default="localhost",
        description="SQL Server instance name (e.g. localhost, localhost\\SQLEXPRESS)",
    )
    sqlserver_database: str = Field(
        default="ContosoRetail",
        description="Target database name",
    )
    sqlserver_schema: str = Field(
        default="dbo",
        description="Target schema name",
    )
    sqlserver_driver: str | None = Field(
        default=None,
        description="ODBC driver name (auto-detected if None)",
    )
    sqlserver_trusted: bool = Field(
        default=True,
        description="Use Windows Authentication (True) or SQL Auth (False)",
    )
    sqlserver_username: str | None = Field(
        default=None,
        description="SQL Auth username (only when trusted=False)",
    )
    sqlserver_password: str | None = Field(
        default=None,
        description="SQL Auth password (only when trusted=False)",
    )
    sqlserver_if_exists: str = Field(
        default="replace",
        description="What to do if table exists: replace, append, fail",
    )
    sqlserver_batch_size: int = Field(
        default=5_000,
        description="Rows per batch INSERT (default: 5000)",
    )

    def for_format(self, fmt: str) -> dict[str, Any]:
        """
        Return only the options relevant to a specific format as a flat dict.
        Strips the 'format_' prefix so writers get clean kwargs.

        Example:
            options.for_format("parquet")
            → {"compression": "zstd", "row_group_size": None}
        """
        prefix = f"{fmt}_"
        return {
            key[len(prefix):]: value
            for key, value in self.model_dump().items()
            if key.startswith(prefix)
        }


class OutputConfig(BaseModel):
    output_path: str  = Field(default="./output", description="Directory for generated files")
    formats: list[str] = Field(
        default=["parquet"],
        description="Output formats: parquet (default), csv, duckdb, delta, json, excel",
    )
    target_orders: int = Field(default=100_000, gt=0, description="Approximate total orders")
    compress: bool = Field(default=True)
    format_options: FormatOptionsConfig = Field(
        default_factory=FormatOptionsConfig,
        description="Per-format configuration options",
    )
    integrity_check: bool  = Field(
        default=False,
        description="Run FK integrity validation after generation (before writing output)",
    )
    integrity_strict: bool = Field(
        default=True,
        description=(
            "If integrity_check=true: raise an error on violations (strict=true) "
            "or just print a report (strict=false)"
        ),
    )

    # ── Keep backward-compatible duckdb_db_name at top level ──────────────────
    duckdb_db_name: str | None = Field(
        default=None,
        description="DEPRECATED — use [output.format_options] duckdb_db_name instead",
    )

    @model_validator(mode="after")
    def migrate_duckdb_name(self) -> "OutputConfig":
        """If user sets duckdb_db_name at output level, forward it to format_options."""
        if self.duckdb_db_name is not None:
            self.format_options.duckdb_db_name = self.duckdb_db_name
        return self

    @field_validator("formats", mode="before")
    @classmethod
    def coerce_formats(cls, v: Any) -> list[str]:
        if isinstance(v, str):
            return [f.strip() for f in v.split(",")]
        return v

    @field_validator("formats", mode="after")
    @classmethod
    def validate_formats(cls, v: list[str]) -> list[str]:
        for fmt in v:
            if fmt.strip().lower() not in SUPPORTED_FORMATS:
                raise ValueError(
                    f"Unknown format '{fmt}'. "
                    f"Supported: {', '.join(sorted(SUPPORTED_FORMATS))}"
                )
        return [f.strip().lower() for f in v]


class CustomersConfig(BaseModel):
    pool_size: int        = Field(default=50_000, gt=0)
    active_pct: float     = Field(default=0.30, ge=0.01, le=1.0)
    online_pct_start: float = Field(default=0.05, ge=0.0, le=1.0)
    online_pct_end: float   = Field(default=0.55, ge=0.0, le=1.0)


class CategoriesConfig(BaseModel):
    enabled: list[str]      = Field(default=["electronics", "home", "gaming", "media"])
    custom_paths: list[str] = Field(default_factory=list)


class AnnualEventConfig(BaseModel):
    name: str
    month: int   = Field(ge=1, le=12)
    day: int     = Field(ge=1, le=31)
    factor: float = Field(gt=0.0)


class OneTimeEventConfig(BaseModel):
    name: str
    date_start: str
    date_end: str
    factor: float             = Field(default=1.0, gt=0.0)
    categories: dict[str, float] = Field(default_factory=dict)


class EventsConfig(BaseModel):
    annual:   list[AnnualEventConfig]   = Field(default_factory=list)
    one_time: list[OneTimeEventConfig]  = Field(default_factory=list)


class WeekdayFactorsConfig(BaseModel):
    # 0=Monday … 6=Sunday
    factors: list[float] = Field(
        default=[0.75, 0.85, 0.95, 1.05, 1.20, 1.60, 0.30],
        min_length=7,
        max_length=7,
    )


# ---------------------------------------------------------------------------
# Root Config
# ---------------------------------------------------------------------------

class AppConfig(BaseModel):
    """Root configuration object parsed from a TOML file."""

    general:        GeneralConfig        = Field(default_factory=GeneralConfig)
    output:         OutputConfig         = Field(default_factory=OutputConfig)
    customers:      CustomersConfig      = Field(default_factory=CustomersConfig)
    categories:     CategoriesConfig     = Field(default_factory=CategoriesConfig)
    events:         EventsConfig         = Field(default_factory=EventsConfig)
    weekday_factors: WeekdayFactorsConfig = Field(default_factory=WeekdayFactorsConfig)

    @classmethod
    def from_toml(cls, path: Path | str) -> "AppConfig":
        """Load and validate configuration from a TOML file."""
        path = Path(path)
        if not path.exists():
            raise FileNotFoundError(f"Config file not found: {path}")
        with open(path, "rb") as f:
            raw = tomllib.load(f)
        return cls.model_validate(raw)

    @classmethod
    def defaults(cls) -> "AppConfig":
        """Return an AppConfig instance with all default values."""
        return cls()


# Compatibility alias
Config = AppConfig


def load_config(path: str | Path | None = None) -> AppConfig:
    """
    Load configuration from a TOML file, or return defaults.

    Args:
        path: Optional path to a TOML config file.
              If None, returns the built-in default configuration.

    Returns:
        A validated AppConfig instance.
    """
    if path is None:
        # Try the bundled default.toml
        builtin = Path(__file__).parent.parent / "configs" / "default.toml"
        if builtin.exists():
            return AppConfig.from_toml(builtin)
        return AppConfig.defaults()
    return AppConfig.from_toml(path)
