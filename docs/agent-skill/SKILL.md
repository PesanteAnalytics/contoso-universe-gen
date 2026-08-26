---
name: contoso-universe-gen
description: >
  Generate synthetic retail datasets using the Contoso Universe Generator (CUG).
  Use this skill whenever the user needs to create demo data, test datasets,
  or populate databases (SQL Server, DuckDB, Parquet, CSV, Delta, JSON, Excel)
  with realistic Contoso-style retail data.

  Triggers (English): "generate test data", "create demo dataset", "populate SQL Server",
  "generate parquet", "synthetic retail data", "workshop dataset", "data for Power BI"

  Triggers (Español): "crear datos de prueba", "generar dataset Contoso", "poblar SQL Server",
  "datos sintéticos", "generar parquet", "datos para Power BI", "llenar la base de datos"
---

# Contoso Universe Generator (CUG) — Agent Skill

A Python CLI tool that generates 100% relational synthetic retail datasets (star schema)
with realistic temporal patterns (COVID, Black Friday, seasonality).

---

## Installation

Copy this file to your agent's skills directory:

```text
# For Antigravity / Gemini agents:
<your_agent_skills_dir>/contoso-universe-gen/SKILL.md

# Example (Windows):
.agent/skills/contoso-universe-gen/SKILL.md
```

After copying, update the three placeholders in the **Location & Invocation** section below:
- `<project_root>` → absolute path to your CUG installation
- `<python>` → path to your Python executable (e.g. `.venv/Scripts/python`)
- `<sql_server_instance>` → your SQL Server instance name (if using SQL output)

---

## Trigger Phrases

Activate this skill when the user says phrases like:

**Español:**

- "Crear 1000 filas" / "Generar 5000 registros" / "Dame 100K filas"
- "Crear datos de prueba" / "Dame datos demo" / "Necesito datos sintéticos"
- "Generar dataset Contoso" / "Refrescar el dataset" / "Regenerar los datos"
- "Meter datos en SQL Server" / "Popular la base de datos" / "Llenar la DB"
- "Crear parquet" / "Generar CSV" / "Exportar a Excel"
- "Datos para Power BI" / "Dataset para workshop" / "Datos para Fabric"

**English:**

- "Create 1000 rows" / "Generate 5000 records" / "Give me 100K rows"
- "Create test data" / "Generate demo dataset" / "I need synthetic data"
- "Populate SQL Server" / "Fill the database" / "Refresh the dataset"
- "Create Parquet files" / "Generate CSV" / "Export to Excel"
- "Sample data for Power BI" / "Workshop dataset" / "Data for Fabric"

**Implicit triggers:**

- "I need sales data" → use CUG with default retail schema
- "I want to test my data model" → generate quick test dataset
- "Fill the table with dummy data" → use CUG with SQL Server format

---

## Agent Workflow

When this skill is triggered, follow this **file-driven** workflow.

The configuration lives in a **persistent Markdown file** the user can view and
edit directly in their IDE:

```text
📂 <project_root>
└── CUG-CONFIG.md    ← persistent configuration card
```

### Step 1: Ensure CUG-CONFIG.md Exists

Check if `CUG-CONFIG.md` exists at the project root.

- **If it exists** → read it (go to Step 2).
- **If it does NOT exist** → create it from the template embedded below, then tell
  the user: *"I've created your configuration card at `CUG-CONFIG.md`. You can edit it anytime."*

The template contains **ALL** configurable options organized in these sections:

| Section                   | Contents                                                         |
| ------------------------- | ---------------------------------------------------------------- |
| 🔧 General                | start_date, end_date, language, country, seed, chunk_days        |
| 📤 Output                 | output_path, formats, target_orders, compress, integrity, strict |
| 📄 Format Options         | parquet, csv, duckdb, delta, json, excel, sqlserver              |
| 👥 Customers              | pool_size, active_pct, online_pct_start, online_pct_end          |
| 📂 Categories             | enabled categories, custom_paths                                 |
| 📅 Annual Events          | name, month, day, factor                                         |
| 📅 Historical Events      | name, date_start, date_end, factor                               |
| 📊 Weekday Factors        | Monday–Sunday demand multipliers                                 |

### Step 2: Read & Parse CUG-CONFIG.md

Use `view_file` to read `CUG-CONFIG.md`. Parse every markdown table to extract
the current values. Each table has a `Variable | Value | Options` structure.
Extract the **Value** column for each variable.

**Parsing rules:**

- **Strings**: Use value as-is (e.g. `2018-01-01`, `en`, `./output`)
- **Numbers**: Parse as integer or float (e.g. `100000` → 100000)
- **Booleans**: `true` / `false` (case-insensitive)
- **Lists**: Comma-separated values (e.g. `parquet, csv` → `["parquet", "csv"]`)
- **Empty cell**: Use the CUG default (same as omitting from TOML)
- **`auto`**: Let the tool decide

### Step 3: Detect Intent & Apply User Changes

Parse the user's message to extract any requested changes:

- **Row count**: "1000 rows", "100K records" → update `target_orders`
- **Format**: "in parquet", "to SQL Server" → update `formats`
- **Language**: "in Spanish", "en inglés" → update `language`
- **Any other variable**: "seed 99", "no compression" → update accordingly

> **⚠️ EXCEL EXCLUSION RULE (MANDATORY)**
>
> Excel has a **hard limit of 1,048,576 rows** per sheet. Datasets exceeding
> this limit will be **silently truncated**.
>
> **Agent behavior:**
>
> 1. **"All formats"** → use `parquet, csv, duckdb, delta, json` — **NEVER include `excel` automatically**.
> 2. **Only add `excel`** if the user **explicitly** requests it.
> 3. If the user requests Excel **and** `target_orders > 800,000`, warn them before proceeding.
> 4. The default `formats` in `CUG-CONFIG.md` should **never** include `excel`.

**If the user specifies changes:**

1. Edit `CUG-CONFIG.md` — update the Value column for each changed variable.
2. Show the user a change summary:

```text
✏️ Changes applied in CUG-CONFIG.md:
  • target_orders: 100000 → 1000
  • formats: parquet → csv
  • language: en → es
```

3. Ask: *"Your configuration is updated. Shall I proceed with generation?"*

**If the user says "go" / "generate" / "dale" / "procede" without changes:**

1. Read the file as-is.
2. Show a brief summary:

```text
📦 CUG-CONFIG.md — Current Configuration
  Orders: 100,000 │ Format: parquet │ Language: en │ Seed: 42
  Proceed with this configuration?
```

### Step 4: Translate Config to TOML + CLI Command

Once the user confirms, translate all values from `CUG-CONFIG.md`:

1. **Copy** `cug/configs/default.toml` → `configs/_session.toml`
2. **Apply ALL values** from `CUG-CONFIG.md` to the session TOML:

**Mapping from CUG-CONFIG.md → TOML sections:**

| CUG-CONFIG.md Section  | TOML Section                                                     |
| ---------------------- | ---------------------------------------------------------------- |
| 🔧 General             | `[general]`                                                      |
| 📤 Output              | `[output]` — **except** `integrity_check` and `integrity_strict` |
| 📄 Format Options      | `[output.format_options]`                                        |
| 👥 Customers           | `[customers]`                                                    |
| 📂 Categories          | `[categories]`                                                   |
| 📅 Annual Events       | `[[events.annual]]` (one block per row)                          |
| 📅 Historical Events   | `[[events.one_time]]` (one block per row)                        |
| 📊 Weekday Factors     | `[weekday_factors]`                                              |

> **⚠️ CLI-only variables** (do NOT write these to TOML):
>
> - `integrity_check = true` → add `--verify` CLI flag
> - `integrity_strict = true` → add `--strict` CLI flag

3. **Build the CLI command:**

```bash
cd <project_root>
<python> -m cug generate -c configs/_session.toml
```

### Step 5: Execute & Update Footer

1. **Run** the command from Step 4.
2. **After successful execution**, update the footer of `CUG-CONFIG.md`:

```markdown
> **Last run**: _2026-03-20 15:00_
> **Last modified**: _2026-03-20_
```

3. **Show output summary:**

```text
✅ Dataset generated successfully
  📁 Directory: ./output
  📊 Tables: 7 (star schema)
  📝 Format: parquet
  🔢 Orders: ~100,000
  ⏱️ Time: 12.3s
```

---

## Location & Invocation

> **Before using this skill, update these three values for your environment:**

| Placeholder | Replace with | Example |
| --- | --- | --- |
| `<project_root>` | Absolute path to your CUG installation | `C:\projects\contoso-universe-gen` |
| `<python>` | Python executable in your venv | `.venv/Scripts/python` (Windows) or `.venv/bin/python` (Mac/Linux) |
| `<sql_server_instance>` | Your SQL Server instance | `localhost\SQLEXPRESS` |

- **Invoke**: `<python> -m cug <command>` (from project root)
- **Or globally**: `cug <command>` (available once CUG is installed with `pip install -e .` from a clone; it is not on PyPI yet)
- **Python**: 3.12+ with a virtual environment (uv recommended)

---

## Commands

| Command          | Purpose                           |
| ---------------- | --------------------------------- |
| `cug generate`   | Generate a full dataset           |
| `cug formats`    | Show all supported output formats |
| `cug info`       | Show available languages          |
| `cug categories` | Show product categories           |
| `cug init [DIR]` | Copy default config template      |

---

## CLI Flags Reference

| Setting             | CLI Flag                           |
| ------------------- | ---------------------------------- |
| Config file         | `-c PATH`                          |
| Output dir          | `-o DIR`                           |
| Language            | `-l CODE`                          |
| Orders              | `-n COUNT`                         |
| Formats             | `-f FORMAT,...`                    |
| Seed                | `--seed N`                         |
| Strict mode         | `--strict` / `--no-strict`         |
| Verbose             | `-v`                               |
| Parquet compression | `--parquet-compression CODEC`      |
| CSV separator       | `--csv-separator SEP`              |
| Delta mode          | `--delta-mode MODE`                |
| JSON format         | `--json-rows` / `--json-ndjson`    |
| Excel mode          | `--excel-single` / `--excel-multi` |
| SQL Server name     | `--sqlserver-name SERVER`          |
| SQL Server DB       | `--sqlserver-db NAME`              |
| SQL Server schema   | `--sqlserver-schema NAME`          |
| SQL Server mode     | `--sqlserver-mode MODE`            |

> **IMPORTANT**: CLI flags take priority over TOML values.

---

## Format-Specific Notes

### DuckDB — Analytical Views

The DuckDB writer auto-creates **3 analytical views** alongside the 7 data tables:

| View | Description |
| ---- | ----------- |
| `v_sales_summary` | Daily sales totals (date, year, month, orders, revenue, margin) |
| `v_top_products` | Top 20 products by revenue (product, category, revenue, units) |
| `v_category_trend` | Monthly revenue by category (year, month, category, revenue) |

### JSON — NDJSON Format

JSON output uses **NDJSON** (Newline-Delimited JSON) with `.ndjson` extension.
Each line is a self-contained JSON object.

### Delta Lake — Null Column Handling

The Delta writer automatically casts `Null`-type columns to `String` before writing.

### Excel — Row Limit (CRITICAL)

Excel has a **hard limit of 1,048,576 rows** per sheet. The CUG writer will
automatically **truncate** FactSales if it exceeds this limit.

---

## Configuration Variables Reference

### 🔧 General (`[general]`)

| Variable     | Default      | Options                                        | Description                     |
| ------------ | ------------ | ---------------------------------------------- | ------------------------------- |
| `start_date` | `2018-01-01` | Any YYYY-MM-DD date                            | Start of temporal range         |
| `end_date`   | `2026-12-31` | Any YYYY-MM-DD date                            | End of temporal range           |
| `language`   | `en`         | `en`, `es`, `pt`, `fr`, `de`, `zh`, `ja`, `ar` | Language for names & categories |
| `country`    | `US`         | ISO 3166-1 code                                | Country for holidays            |
| `seed`       | `42`         | Any integer                                    | Master seed (reproducibility)   |
| `chunk_days` | `30`         | > 0                                            | Days per chunk (memory control) |

### 📤 Output (`[output]`)

| Variable           | Default       | Options                                                           | Description                   |
| ------------------ | ------------- | ----------------------------------------------------------------- | ----------------------------- |
| `output_path`      | `./output`    | Any directory                                                     | Output directory              |
| `formats`          | `["parquet"]` | `parquet`, `csv`, `duckdb`, `delta`, `json`, `excel`, `sqlserver` | Output formats (combinable)   |
| `target_orders`    | `100,000`     | > 0                                                               | Approximate order count       |
| `compress`         | `true`        | `true` / `false`                                                  | Gzip compression for CSV      |
| `integrity_check`  | `false`       | `true` / `false`                                                  | Validate FK integrity         |
| `integrity_strict` | `true`        | `true` / `false`                                                  | Abort on FK violations        |

### 👥 Customers (`[customers]`)

| Variable           | Default  | Options    | Description                           |
| ------------------ | -------- | ---------- | ------------------------------------- |
| `pool_size`        | `50,000` | > 0        | Total unique customers in the universe |
| `active_pct`       | `0.30`   | 0.01 – 1.0 | % of customers who buy at least once  |
| `online_pct_start` | `0.05`   | 0.0 – 1.0  | % online sales at start of period     |
| `online_pct_end`   | `0.55`   | 0.0 – 1.0  | % online sales at end (growth curve)  |

### 📂 Categories (`[categories]`)

| Variable       | Default                                      | Description              |
| -------------- | -------------------------------------------- | ------------------------ |
| `enabled`      | `["electronics", "home", "gaming", "media"]` | Active categories        |
| `custom_paths` | `[]`                                         | Paths to custom YAML plugins |

---

## Quick Recipes

```bash
# Quick test (~5K orders)
cug generate -c configs/quicktest.toml

# 100K orders to SQL Server
cug generate -n 100000 -f sqlserver \
  --sqlserver-name "<sql_server_instance>" --sqlserver-db ContosoDemo

# 1M orders, Spanish, Parquet
cug generate -n 1000000 -f parquet -l es --strict

# Multi-format for workshop
cug generate -n 50000 -f parquet,csv,duckdb -l es

# Delta Lake for Fabric
cug generate -n 500000 -f delta --delta-mode overwrite

# Reproducible dataset
cug generate --seed 42 -n 100000 -f parquet -o ./output/v1
```

---

## YAML Category Plugin System

> **Full guide**: [`docs/category-plugins.md`](../category-plugins.md)

CUG uses YAML files to define product categories. The 4 builtins are:
`electronics`, `gaming`, `home`, `media`.

### YAML Schema (Quick Reference)

```yaml
plugin_id: fashion                    # Unique snake_case ID (required)
display_names:                        # Localized names (at least "en" required)
  en: Fashion & Apparel
  es: Moda y Ropa
subcategories:
  - id: shoes
    display_names: { en: Shoes, es: Zapatos }
    brands: [Nike, Adidas]
    price_range: [40.0, 350.0]        # [min, max] unit price
    margin_range: [0.15, 0.45]        # [min, max] margin (0–1)
    trend:
      2020: 0.60                      # COVID drop
      2024: 1.20                      # Growth year
    products:
      - name_template: "{brand} {model} {spec}"
        models: [Air Max, Superstar]
        specs: [Size 8, Size 10]
```

Register in TOML:

```toml
[categories]
enabled = ["electronics", "home", "gaming", "media", "fashion"]
custom_paths = ["./my_plugins/fashion.yaml"]
```

---

## Language Impact Reference

> **Full guide**: [`docs/i18n-reference.md`](../i18n-reference.md)

### What DOES change per language

| Component               | What changes                  |
| ----------------------- | ----------------------------- |
| `MonthName` / `DayName` | Translated month/day names    |
| `CategoryName`          | YAML `display_names`          |
| Customer cities / countries | Locale-appropriate pools  |
| Store countries         | Locale-appropriate retail footprint |
| Primary currency        | en→USD, es→MXN, pt→BRL, fr/de→EUR |
| Holidays                | Country-specific holidays      |

### What does NOT change (always English)

Column headers (`ProductKey`, `OrderDate`), product names, brand names,
currency codes, store status values.

---

## Generated Tables (Star Schema)

| Table                 | Type      | Key Columns                                    |
| --------------------- | --------- | ---------------------------------------------- |
| `DimDate`             | Dimension | DateKey, Year, Month, Quarter, DayName         |
| `DimCustomer`         | Dimension | CustomerKey, GivenName, Surname, City, Country |
| `DimProduct`          | Dimension | ProductKey, ProductName, Category, Subcategory |
| `DimStore`            | Dimension | StoreKey, StoreName, StoreType, Country        |
| `DimCurrency`         | Dimension | CurrencyKey, CurrencyCode, CurrencyName        |
| `DimCurrencyExchange` | Dimension | CurrencyKey, DateKey, Exchange                 |
| `FactSales`           | Fact      | OrderKey, CustomerKey, ProductKey, StoreKey    |

---

## Configuration Files (Bundled)

| Config                       | Description            |
| ---------------------------- | ---------------------- |
| `cug/configs/default.toml`       | Standard config, 100K  |
| `configs/quicktest.toml`     | Quick test, ~5K orders |
| `configs/retail_1M_en.toml`  | 1M orders, English     |
| `configs/retail_1M_es.toml`  | 1M orders, Spanish     |
| `configs/retail_10M_es.toml` | 10M orders, Spanish    |
