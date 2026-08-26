# Contoso Universe Generator — Documentation

> **CUG** generates 100% relational synthetic retail datasets, ready for Power BI, DuckDB, Parquet, SQL Server, and more. Each run produces coherent dimension and fact tables, with realistic historical events (COVID, Black Friday, seasonality).

---

## 📚 Documentation Index

| Document | Description |
|----------|-------------|
| [Installation](installation.md) | Prerequisites, installation with pip/uv, ODBC drivers |
| [CLI Reference](cli-reference.md) | All commands (`generate`, `info`, `categories`, `formats`, `init`) with options and examples |
| [TOML Configuration](toml-configuration.md) | Complete `.toml` file structure with detailed explanations |
| [Output Formats](output-formats.md) | The 7 supported formats (Parquet, CSV, DuckDB, Delta, JSON, Excel, SQL Server) |
| [Data Schema](data-schema.md) | The 7 generated tables, columns, data types, FK relationships |
| [SQL Server](sqlserver.md) | Dedicated guide: ODBC drivers, authentication, type mapping, troubleshooting |
| [Recipes](recipes.md) | Common scenarios solved with a single command |
| [Category Plugins (YAML)](category-plugins.md) | YAML schema, fields, defaults, how to create custom categories |
| [i18n Reference](i18n-reference.md) | What changes and what does NOT change by language — real impact of the `language` setting |

---

## 🚀 Quick Start

```bash
# Installation
pip install -e .

# Generate a test dataset (~5K orders)
cug generate -c configs/quicktest.toml

# Generate 100K orders in Parquet (default)
cug generate -n 100000

# Generate 50K orders in Spanish with multiple formats
cug generate -n 50000 -f parquet,csv,duckdb -l es
```

---

## 🏗️ Architecture

CUG generates a star schema with 7 tables:

```
                    ┌─────────────┐
                    │   DimDate   │
                    └──────┬──────┘
                           │
┌─────────────┐    ┌───────┴───────┐    ┌─────────────┐
│ DimCustomer │────│   FactSales   │────│  DimProduct  │
└─────────────┘    └───────┬───────┘    └─────────────┘
                           │
                    ┌──────┴──────┐
                    │  DimStore   │
                    └──────┬──────┘
                           │
               ┌───────────┴────────────┐
               │     DimCurrency        │
               └───────────┬────────────┘
                           │
               ┌───────────┴────────────┐
               │  DimCurrencyExchange   │
               └────────────────────────┘
```

---

## 📎 Useful Links

- **Project Roadmap:** [`ROADMAP.md`](../ROADMAP.md)

- **Predefined configurations:** [`configs/`](../configs/)

---

_Contoso Universe Generator — see the [releases](https://github.com/PesanteAnalytics/contoso-universe-gen/releases) for the current version._
