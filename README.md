# Contoso Universe Generator (`cug`)

> **God-level synthetic retail data generator** — 100% Python, zero .NET required.

[![Python 3.12+](https://img.shields.io/badge/python-3.12+-blue.svg)](https://python.org)
[![Polars](https://img.shields.io/badge/dataframe-polars-orange)](https://pola.rs)
[![DuckDB](https://img.shields.io/badge/engine-duckdb-yellow)](https://duckdb.org)

## Features

| Feature                 | Description                                                    |
| ----------------------- | -------------------------------------------------------------- |
| 🌍 **Multi-language**   | EN, ES, PT, FR, DE, ZH, JA, AR — names, cities, categories     |
| ⚡ **Polars engine**    | Vectorized generation — 5-10x faster than Pandas-based tools   |
| 📦 **7 output formats** | Parquet, CSV, DuckDB, Delta Lake, JSON, Excel, SQL Server      |
| 🔌 **Category plugins** | Add any industry with a simple YAML file                       |
| 🎯 **Deterministic**    | Seed-per-day reproducibility — same config = same data         |
| 🕐 **Temporal realism** | COVID spikes, Black Friday, eCommerce curves, Poisson delivery |

## Quick Start

```bash
# Install with uv (recommended)
uv pip install -e .

# Generate 100k retail orders in English (Parquet)
cug generate -n 100000 -f parquet

# Generate in multiple formats
cug generate -n 50000 -f parquet,csv,duckdb -l es

# Direct to SQL Server
cug generate -n 100000 -f sqlserver --sqlserver-name "localhost\SQLEXPRESS" --sqlserver-db ContosoRetail

# Generate 1M orders in Spanish using config
cug generate -c configs/retail_1M_es.toml

# See available formats
cug formats

# See available categories
cug categories
```

## Output Schema

### Fact Tables

- `fact_sales` — Order lines with pricing, discounts, delivery dates

### Dimension Tables

- `dim_product` — Products with category/subcategory hierarchy
- `dim_customer` — Customers (real-ish names via Faker, localized)
- `dim_store` — Physical stores + online channel
- `dim_date` — Extended calendar with holidays, working days
- `dim_currency` — Exchange rates over time

## Stack

- **[Polars](https://pola.rs)** — DataFrame engine
- **[DuckDB](https://duckdb.org)** — Embedded analytical SQL
- **[Faker](https://faker.readthedocs.io)** — Synthetic data + locales
- **[Pydantic v2](https://docs.pydantic.dev)** — Config validation
- **[Typer](https://typer.tiangolo.com)** — CLI
- **[Rich](https://rich.readthedocs.io)** — Terminal UI

## Adding Custom Categories

CUG supports custom product categories via YAML plugin files.

1. Create a YAML file following the builtin schema (see `cug/categories/builtin/` for examples)
2. Add the path to your TOML config:

   ```toml
   [categories]
   custom_paths = ["./my_fashion_category.yaml"]
   ```

3. Run generation as normal — your custom categories will be included:

   ```bash
   cug generate -c my_config.toml
   ```

To see all loaded categories:

```bash
cug categories
cug categories -l es   # show in Spanish
```

## License

MIT — See [NOTICE.md](NOTICE.md) for attribution to original Contoso concepts.
