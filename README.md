# Contoso Universe Generator (`cug`)

> **The Python-native synthetic retail data generator** — multi-language, multi-format, zero .NET required.

[![Python 3.12+](https://img.shields.io/badge/python-3.12%2B-blue.svg)](https://python.org)
[![License: MIT](https://img.shields.io/badge/license-MIT-green.svg)](LICENSE)
[![CI](https://github.com/PesanteAnalytics/contoso-universe-gen/actions/workflows/ci.yml/badge.svg)](https://github.com/PesanteAnalytics/contoso-universe-gen/actions/workflows/ci.yml)
[![Polars](https://img.shields.io/badge/dataframe-Polars-orange)](https://pola.rs)
[![DuckDB](https://img.shields.io/badge/engine-DuckDB-yellow)](https://duckdb.org)
[![Ruff](https://img.shields.io/endpoint?url=https://raw.githubusercontent.com/astral-sh/ruff/main/assets/badge/v2.json)](https://github.com/astral-sh/ruff)

![CUG generating a 50,000-order retail star schema in Spanish, then reporting what each language actually localizes](assets/demo.gif)

*One command: seven tables, foreign keys verified, in about a second. The demo is
a [VHS](https://github.com/charmbracelet/vhs) script — [`assets/demo.tape`](assets/demo.tape) —
so it can be re-rendered whenever the CLI changes rather than going quietly out of date.*

---

## Why CUG?

The [Contoso Data Generator V2](https://github.com/sql-bi/Contoso-Data-Generator-V2) by **SQLBI** (Marco Russo & Alberto Ferrari) is the gold standard for Power BI demo data. Their schema design and temporal realism patterns are simply excellent — CUG would not exist without them.

CUG is a Python-native answer to the same problem: same spirit, different stack, expanded scope. It was built for teams that need offline generation, multi-language localization, or scripted/agent-driven workflows.

> *Standing on the shoulders of giants.*

**Where the two differ:**

| DG V2 | CUG |
| --- | --- |
| .NET SDK required (~75 MB runtime) | 100% Python — no separate runtime to install |
| English-only names and categories | Product catalogue, calendar, names and geography all localized — see [coverage](#language-coverage) for the depth per language |
| Source data fetched from SQLBI servers | Fully offline — nothing is fetched at generation time |
| Fixed product schema (`data.xlsx`) | YAML category plugins — extend without touching code |
| CSV / Parquet / Delta | + DuckDB, JSON, Excel, SQL Server |
| No built-in FK validation | `--verify` + `--strict` for FK-safe datasets |
| No bundled agent integration | Native Antigravity skill (trigger phrases in EN/ES) |

> CUG and DG V2 serve different needs. DG V2 remains the definitive Contoso reference for .NET environments.
> CUG is the Python-native alternative — offline, multi-language, and built to be scripted and automated.

---

## Features

| | Feature | Detail |
| --- | --- | --- |
| 🌍 | **Multi-language** | 8 locales — see [language coverage](#language-coverage) for what each one translates |
| ⚡ | **Polars engine** | Vectorized generation — 5–10× faster than Pandas-based tools |
| 📦 | **7 output formats** | Parquet, CSV, DuckDB, Delta Lake, JSON, Excel, SQL Server |
| 🔌 | **YAML category plugins** | Add any industry vertical without changing a line of code |
| 🎯 | **Deterministic** | Seed-per-day reproducibility — same config = same data, always |
| 🕐 | **Temporal realism** | COVID dip, Black Friday spikes, eCommerce growth, Poisson delivery |
| 👥 | **Customer segments** | Pareto-shaped spend tiers + dormant customers — [details](#customer-segments-and-baskets) |
| 🧺 | **Multi-line orders** | Real baskets: one `OrderKey`, several coherent lines |
| ✅ | **FK integrity checks** | `--verify` catches orphaned rows before you load to Power BI |
| 🤖 | **AI-agent native** | Configure and run via natural language through the bundled Skill |

---

## Quick Start

> **Not on PyPI yet** — install from a clone. A published package is planned;
> until then `pip install contoso-universe-gen` will not find anything.

```bash
# Clone and install (uv recommended)
git clone https://github.com/PesanteAnalytics/contoso-universe-gen.git
cd contoso-universe-gen
uv pip install -e .

# Generate 10,000 retail orders in English (Parquet)
cug generate -n 10000 -f parquet

# Multiple formats + Spanish locale
cug generate -n 50000 -f parquet,csv,duckdb -l es

# Direct to SQL Server
cug generate -n 100000 -f sqlserver \
  --sqlserver-name "localhost\SQLEXPRESS" \
  --sqlserver-db ContosoRetail

# Generate from a TOML config file
cug generate -c configs/retail_1M_es.toml

# Explore the CLI
cug formats          # list all output formats
cug categories       # list product categories
cug categories -l es # categories in Spanish
cug info             # show current config
```

---

## Output Schema

CUG produces a classic **retail star schema**:

```
                    ┌─────────────┐
                    │  FactSales  │
                    └──────┬──────┘
           ┌───────────────┼───────────────┐
           │               │               │
    ┌──────▼──────┐ ┌──────▼──────┐ ┌──────▼──────┐
    │ DimProduct  │ │ DimCustomer │ │  DimStore   │
    └─────────────┘ └─────────────┘ └─────────────┘
           │               │
    ┌──────▼──────┐ ┌──────▼──────────────┐
    │   DimDate   │ │ DimCurrencyExchange  │
    └─────────────┘ └─────────────────────┘
```

| Table | Key columns |
| --- | --- |
| `FactSales` | `OrderKey`, `LineNumber`, `CustomerKey`, `ProductKey`, `StoreKey`, `OrderDate`, `UnitPrice`, `NetPrice`, `UnitCost` |
| `DimProduct` | `ProductKey`, `ProductName`, `Category`, `Subcategory`, `Brand`, `Price`, `Cost` |
| `DimCustomer` | `CustomerKey`, `GivenName`, `Surname`, `Email`, `City`, `CountryCode`, `CustomerSegment` |
| `DimStore` | `StoreKey`, `StoreName`, `Country`, `StoreType` |
| `DimDate` | `DateKey`, `Date`, `Year`, `Month`, `Quarter`, `IsHoliday`, `IsWorkingDay` |
| `DimCurrencyExchange` | `CurrencyKey`, `DateKey`, `Exchange` |

---

## Customer Segments and Baskets

A synthetic fact table gives itself away in two places, and both are about
shape rather than volume.

**Revenue spread evenly over the customer list.** CUG cuts the *active* base
into spend tiers and weights who lands on an order, so a small head of heavy
buyers carries most of the revenue — the way a real customer base behaves. The
tier is written out as `CustomerSegment` on `DimCustomer`, so you can slice by
it directly. `active_pct` decides how much of the pool ever buys at all; the
rest stay registered and dormant, labelled `Inactive`, and never reach
`FactSales`.

```toml
[customers]
active_pct = 0.30          # 70% of the pool is registered but dormant

[[customers.segments]]
name = "Key Account"
share = 0.01               # 1% of the ACTIVE base...
demand_weight = 60.0       # ...ordering 60x as often as the smallest tier
lines_multiplier = 2.2     # with a basket twice the size
quantity_multiplier = 1.8
```

Shares must add up to 1.0. Out of the box the top 20% of active customers place
about 72% of the orders and take about 80% of the revenue.

**Every order having exactly one line.** `avg_lines_per_order` turns orders
into baskets: `OrderKey` repeats across 1..n rows that share the customer,
date, channel and store, with `LineNumber` running 1..n inside each. It
defaults to `1.0`, which keeps the historical one-row-per-order fact table.

```toml
[customers]
avg_lines_per_order = 2.6   # FactSales rows ~= target_orders x 2.6
max_lines_per_order = 12
```

The multipliers are relative: they are normalised against their own
order-weighted mean, so raising one segment's basket does not drag the whole
table's average away from the number you configured.

## Custom Category Plugins

Add any product category with a YAML file — no code changes needed:

```yaml
# my_fashion_category.yaml
name: Fashion
subcategories:
  - name: Footwear
    products:
      - { name: "Running Shoes", price: 120, cost: 55 }
      - { name: "Leather Boots", price: 250, cost: 110 }
```

Register in your TOML config:

```toml
[categories]
custom_paths = ["./my_fashion_category.yaml"]
```

See [`docs/category-plugins.md`](docs/category-plugins.md) for the full YAML schema.

---

## Language coverage

Translation depth is not uniform, and the difference matters when you are
picking a locale for a demo. Run `cug info` to see this table for your install —
it is computed from the data, not maintained by hand.

| Code | Language | Product catalogue | Calendar | People & geography |
| --- | --- | :---: | :---: | :---: |
| `en` | English | ✅ | ✅ | ✅ |
| `es` | Español | ✅ | ✅ | ✅ |
| `pt` | Português | ✅ | ✅ | ✅ |
| `fr` | Français | ✅ | ✅ | ✅ |
| `de` | Deutsch | ✅ | ✅ | → `en` |
| `zh` | 中文 | ✅ | → `en` | → `en` |
| `ja` | 日本語 | ✅ | → `en` | → `en` |
| `ar` | العربية | ✅ | → `en` | → `en` |

- **Product catalogue** — category and subcategory names, from the YAML plugins.
- **Calendar** — `MonthName` and `DayName` in `DimDate`. Holiday names come from
  the [`holidays`](https://pypi.org/project/holidays/) package and follow its own
  language support.
- **People & geography** — customer names, cities, subdivisions, coordinates and
  store locations. A language without its own geography generates a US/European
  customer base; the product catalogue is still translated.

Adding a language means extending `_GEO_BY_LANG` in
[`cug/i18n/geography.py`](cug/i18n/geography.py) and the name pools in
[`cug/generators/customers.py`](cug/generators/customers.py). Contributions
welcome — see [`CONTRIBUTING.md`](CONTRIBUTING.md).

---

## Stack

| Library | Role |
| --- | --- |
| [Polars](https://pola.rs) | DataFrame engine — vectorized, blazing fast |
| [DuckDB](https://duckdb.org) | Embedded analytical SQL engine |
| [NumPy](https://numpy.org) | Vectorized RNG behind customer and sales generation |
| [Pydantic v2](https://docs.pydantic.dev) | Config validation |
| [Typer](https://typer.tiangolo.com) | CLI framework |
| [Rich](https://rich.readthedocs.io) | Terminal UI with progress bars and tables |

---

## Documentation

| Doc | Description |
| --- | --- |
| [`docs/README.md`](docs/README.md) | Documentation index |
| [`docs/installation.md`](docs/installation.md) | Prerequisites and setup guide |
| [`docs/cli-reference.md`](docs/cli-reference.md) | CLI commands and options |
| [`docs/toml-configuration.md`](docs/toml-configuration.md) | TOML configuration reference |
| [`docs/output-formats.md`](docs/output-formats.md) | Format-specific configuration |
| [`docs/data-schema.md`](docs/data-schema.md) | Star schema and table definitions |
| [`docs/category-plugins.md`](docs/category-plugins.md) | YAML plugin authoring guide |
| [`docs/i18n-reference.md`](docs/i18n-reference.md) | Internationalization and locale guide |
| [`docs/agent-skill/SKILL.md`](docs/agent-skill/SKILL.md) | AI agent skill (Antigravity / Gemini) |
| [`CONTRIBUTING.md`](CONTRIBUTING.md) | How to contribute |

---

## 🤖 AI Agent Integration

CUG ships with a native **Agent Skill** for AI coding assistants
(Antigravity, Gemini CLI, and others that support `SKILL.md` files).

Once installed, you can configure and run CUG entirely through natural language:

```text
You: "Generate 50k rows in Spanish and load to SQL Server"
Agent: reads CUG-CONFIG.md → updates config → runs generation → reports results

"Generator 100K orders en parquet para un workshop"
Agent: target_orders=100000, format=parquet, proceeds automatically
```

The skill uses a **persistent `CUG-CONFIG.md`** file as a configuration card
that you can view and edit directly in your IDE — no JSON, no command memorization.

```bash
cug init   # create your local CUG-CONFIG.md configuration card
```

See [`docs/agent-skill/SKILL.md`](docs/agent-skill/SKILL.md) for full installation instructions.

---

## 🏗️ From Pesante Analytics

CUG started as an internal tool at **[Pesante Analytics](https://www.pesanteanalytics.com/?utm_source=github&utm_medium=readme&utm_campaign=cug)** — a Power BI consulting firm
that builds analytics solutions across industries: VMS/workforce staffing, healthcare,
financial services, and retail.

The challenge: every client engagement needs realistic demo data *in their industry,
in their language, at their scale* — and no existing tool could deliver that without
significant manual effort. CUG solves that.

We built it in the open because the problem is universal.
**If you build Power BI solutions for clients, CUG can save you days of work.**

> *We built what we needed. We shared it because you might need it too.*

---

## 🤝 Built with AI Collaboration

CUG was designed and built by **Cristóbal Salcedo** ([@CSalcedoDataBI](https://github.com/CSalcedoDataBI))
in close collaboration with **Antigravity** — Google DeepMind's agentic coding assistant.

This is not a project *generated* by AI. It is a project *architected* by a domain expert
who used AI as a pair programmer. Every design decision, every feature, every test scenario
reflects real-world data modeling experience from the Power BI and analytics space.

**What Cristóbal brought:** Domain expertise in VMS, retail analytics, and Power BI data modeling.
**What AI brought:** Implementation speed, code structure, and iteration velocity.

The result: a production-grade tool built by a solo practitioner in weeks rather than months.
This is the new paradigm of open-source — and CUG is built to inspire others to do the same.

---

## Contributing

See [`CONTRIBUTING.md`](CONTRIBUTING.md) for:
- Setting up a dev environment
- Running the test suite
- Creating YAML category plugins
- Code style and PR process

---

## License

MIT — see [LICENSE](LICENSE). \
See [NOTICE.md](NOTICE.md) for attribution to the original Contoso concept by SQLBI.
