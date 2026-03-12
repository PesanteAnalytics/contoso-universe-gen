---
name: contoso-universe-gen
description: >
  Generate synthetic retail datasets using the Contoso Universe Generator (CUG).
  Use this skill whenever the user needs to create demo data, test datasets,
  or populate databases (SQL Server, DuckDB, Parquet, CSV, Delta, JSON, Excel)
  with realistic Contoso-style retail data.
---

# Contoso Universe Generator (CUG) — Agent Skill

A Python CLI tool that generates 100% relational synthetic retail datasets (star schema)
with realistic temporal patterns (COVID, Black Friday, seasonality).

## Trigger Phrases

Activate this skill when the user says phrases like:

**Español:**
- "Crear 1000 filas" / "Generar 5000 registros" / "Dame 100K filas"
- "Crear datos de prueba" / "Dame datos demo" / "Necesito datos sintéticos"
- "Generar dataset Contoso" / "Refrescar el dataset" / "Regenerar los datos"
- "Meter datos en SQL Server" / "Popular la base de datos" / "Llenar la DB"
- "Crear parquet" / "Generar CSV" / "Exportar a Excel"
- "Datos para Power BI" / "Dataset para workshop" / "Datos para Fabric"
- "Crear base de datos de prueba" / "Montar datos de retail"

**English:**
- "Create 1000 rows" / "Generate 5000 records" / "Give me 100K rows"
- "Create test data" / "Generate demo dataset" / "I need synthetic data"
- "Populate SQL Server" / "Fill the database" / "Refresh the dataset"
- "Create Parquet files" / "Generate CSV" / "Export to Excel"
- "Sample data for Power BI" / "Workshop dataset" / "Data for Fabric"

**Implicit triggers** (user may not mention CUG explicitly):
- "Necesito datos de ventas" → use CUG with default retail schema
- "Quiero probar mi modelo de datos" → generate quick test dataset
- "Llena la tabla con datos ficticios" → use CUG with SQL Server format

## Agent Workflow

When this skill is triggered, follow this **file-driven** workflow.

The configuration lives in a **persistent Markdown file** that the user can view and
edit directly in their IDE:

```
📂 Project Root
└── CUG-CONFIG.md    ← tarjeta de configuración persistente
```

**Path**: `d:\PAL-TEMPORAL-REPORSITORIOS\contoso-universe-gen\CUG-CONFIG.md`

---

### Step 1: Ensure CUG-CONFIG.md Exists

Check if `CUG-CONFIG.md` exists at the project root.

- **If it exists** → read it (go to Step 2).
- **If it does NOT exist** → create it from the template embedded below, then tell
  the user: _"He creado tu tarjeta de configuración en `CUG-CONFIG.md`. Puedes
  editarla en cualquier momento."_

The template file contains **ALL** configurable options organized in these sections:

| Section | Contents |
|---------|----------|
| 🔧 General | start_date, end_date, language, country, seed, chunk_days |
| 📤 Output | output_path, formats, target_orders, compress, integrity, strict |
| 📄 Format Options | parquet, csv, duckdb, delta, json, excel, sqlserver |
| 👥 Clientes | pool_size, active_pct, online_pct_start, online_pct_end |
| 📂 Categorías | enabled categories, custom_paths |
| 📅 Eventos Anuales | name, month, day, factor (table rows) |
| 📅 Eventos Históricos | name, date_start, date_end, factor (table rows) |
| 📊 Factores Día de Semana | Monday–Sunday factors |

### Step 2: Read & Parse CUG-CONFIG.md

Use `view_file` to read `CUG-CONFIG.md`. Parse every markdown table to extract
the current values. Each table has a `Variable | Valor | Opciones` structure
(or similar). Extract the **Valor** column for each variable.

**Parsing rules:**

- **Strings**: Use value as-is (e.g. `2018-01-01`, `en`, `./output`)
- **Numbers**: Parse as integer or float (e.g. `100000` → 100000, `0.30` → 0.30)
- **Booleans**: `true` / `false` (case-insensitive)
- **Lists**: Comma-separated values (e.g. `parquet, csv` → ["parquet", "csv"])
- **Empty cell**: Use the CUG default (same as omitting from TOML)
- **`auto`**: Use the CUG default (let the tool decide)
- **Events tables**: Each row is one event entry
- **Weekday factors**: Read the 7 Factor values in order (Lun → Dom)

### Step 3: Detect Intent & Apply User Changes

Parse the user's chat message to extract any requested changes:

- **Row count**: "1000 filas", "100K records" → update `target_orders`
- **Format**: "en parquet", "a SQL Server" → update `formats`
- **Language**: "en español", "in English" → update `language`
- **Any other variable**: "seed 99", "sin compresión" → update accordingly

**If the user specifies changes in the chat:**

1. **Edit `CUG-CONFIG.md`** directly using file editing tools — update the Valor
   column for each changed variable.
2. **Show the user a summary** of what changed:

```
✏️ Cambios aplicados en CUG-CONFIG.md:
  • target_orders: 100000 → 1000
  • formats: parquet → csv
  • language: en → es
```

3. Ask: _"Tu configuración está actualizada. ¿Procedo a generar?"_

**If the user says "genera" / "dale" / "procede" without changes:**

1. Read the file as-is.
2. Show a brief summary of key values:

```
📦 CUG-CONFIG.md — Configuración Actual
  Órdenes: 100,000 │ Formato: parquet │ Idioma: en │ Seed: 42
  ¿Procedo con esta configuración?
```

**If the user says "quiero ver/editar la configuración":**

1. Tell them: _"Tu configuración está en `CUG-CONFIG.md` — ábrela y edita lo que
   necesites. Cuando estés listo, dime 'genera' o 'procede'."_

### Step 4: Translate Config to TOML + CLI Command

Once the user confirms, translate ALL values from `CUG-CONFIG.md` into
execution parameters:

**Always create a session TOML** — this ensures ALL settings are respected,
including those without CLI flags:

1. **Copy** `configs/default.toml` → `configs/_session.toml`
2. **Apply ALL values from CUG-CONFIG.md** to the session TOML:

**Mapping from CUG-CONFIG.md → TOML sections:**

| CUG-CONFIG.md Section | TOML Section |
|------------------------|--------------|
| 🔧 General | `[general]` |
| 📤 Output | `[output]` — **except** `integrity_check` and `integrity_strict` |
| 📄 Format Options | `[output.format_options]` |
| 👥 Clientes | `[customers]` |
| 📂 Categorías | `[categories]` |
| 📅 Eventos Anuales | `[[events.annual]]` (one block per row) |
| 📅 Eventos Históricos | `[[events.one_time]]` (one block per row) |
| 📊 Factores Día Semana | `[weekday_factors]` |

> **⚠️ CLI-only variables** (do NOT write these to TOML):
> - `integrity_check` = `true` → add `--verify` CLI flag
> - `integrity_check` = `false` → omit flag (default)
> - `integrity_strict` = `true` → add `--strict` CLI flag
> - `integrity_strict` = `false` → add `--no-strict` CLI flag

**Event table column mapping** (Markdown header → TOML key):

| Eventos Anuales Header | TOML Key | Eventos Históricos Header | TOML Key |
|------------------------|----------|---------------------------|----------|
| Evento | `name` | Evento | `name` |
| Mes | `month` | Fecha Inicio | `date_start` |
| Día | `day` | Fecha Fin | `date_end` |
| Factor | `factor` | Factor | `factor` |

3. **Build the CLI command** using the session TOML:

```bash
cd d:\PAL-TEMPORAL-REPORSITORIOS\contoso-universe-gen
.venv\Scripts\python.exe -m cug generate -c configs/_session.toml
```

   Optionally add CLI flags that override TOML values for convenience:
   `-n`, `-f`, `-l`, `--seed`, `-o` (these override TOML values).
   Also add integrity flags from `CUG-CONFIG.md` if enabled (see table above).

### Step 5: Execute & Update Footer

1. **Run** the command from Step 4.
2. **After successful execution**, update the footer of `CUG-CONFIG.md`:

```markdown
> **Última ejecución**: _2026-03-11 17:45_
> **Última modificación**: _2026-03-11_
```

3. **Show output summary** to the user:

```
✅ Dataset generado exitosamente
  📁 Directorio: ./output
  📊 Tablas: 7 (star schema)
  📝 Formato: parquet
  🔢 Órdenes: ~100,000
  ⏱️ Tiempo: 12.3s
```

4. **Keep** `configs/_session.toml` for reproducibility. It can be reused
   or referenced later.

---

### CLI Flags Reference (for Step 4 overrides)

| Setting | CLI Flag |
|---------|----------|
| Config file | `-c PATH` |
| Output dir | `-o DIR` |
| Language | `-l CODE` |
| Orders | `-n COUNT` |
| Formats | `-f FORMAT,...` |
| Seed | `--seed N` |
| Strict mode | `--strict` / `--no-strict` |
| Verbose | `-v` |
| Parquet compression | `--parquet-compression CODEC` |
| CSV separator | `--csv-separator SEP` |
| Delta mode | `--delta-mode MODE` |
| JSON format | `--json-rows` / `--json-ndjson` |
| Excel mode | `--excel-single` / `--excel-multi` |
| SQL Server name | `--sqlserver-name SERVER` |
| SQL Server DB | `--sqlserver-db NAME` |
| SQL Server schema | `--sqlserver-schema NAME` |
| SQL Server mode | `--sqlserver-mode MODE` |

> **IMPORTANT**: CLI flags always take priority over TOML values.

---

## Configuration Variables Reference

### 🔧 General (`[general]`)

| Variable     | CLI Flag    | Default        | Opciones                                       | Descripción                        |
| ------------ | ----------- | -------------- | ---------------------------------------------- | ---------------------------------- |
| `start_date` | —           | `2018-01-01`   | Cualquier fecha YYYY-MM-DD                     | Inicio del rango temporal          |
| `end_date`   | —           | `2026-12-31`   | Cualquier fecha YYYY-MM-DD                     | Fin del rango temporal             |
| `language`   | `-l`        | `en`           | `en`, `es`, `pt`, `fr`, `de`, `zh`, `ja`, `ar` | Idioma para nombres y categorías   |
| `country`    | —           | `US`           | Código ISO 3166-1                              | País para días festivos            |
| `seed`       | `--seed`    | `42`           | Cualquier entero                               | Semilla maestra (reproducibilidad) |
| `chunk_days` | —           | `30`           | > 0                                            | Días por chunk (memoria vs velocidad) |

### 📤 Output (`[output]`)

| Variable           | CLI Flag       | Default       | Opciones                                                      | Descripción                    |
| ------------------ | -------------- | ------------- | ------------------------------------------------------------- | ------------------------------ |
| `output_path`      | `-o`           | `./output`    | Cualquier directorio                                          | Directorio de salida           |
| `formats`          | `-f`           | `["parquet"]` | `parquet`, `csv`, `duckdb`, `delta`, `json`, `excel`, `sqlserver` | Formatos (combinables con `,`) |
| `target_orders`    | `-n`           | `100,000`     | > 0                                                           | Órdenes aproximadas            |
| `compress`         | —              | `true`        | `true` / `false`                                              | Compresión Gzip para CSV       |
| `integrity_check`  | —              | `false`       | `true` / `false`                                              | Validar integridad FK          |
| `integrity_strict` | `--strict`     | `true`        | `true` / `false`                                              | Abortar en violaciones FK      |

### 📄 Opciones por Formato (`[output.format_options]`)

#### Parquet

| Variable               | CLI Flag                  | Default  | Opciones                                   |
| ---------------------- | ------------------------- | -------- | ------------------------------------------ |
| `parquet_compression`  | `--parquet-compression`   | `zstd`   | `zstd`, `snappy`, `gzip`, `lz4`, `brotli`, `none` |
| `parquet_row_group_size` | —                       | `None`   | Entero o None (automático)                 |

#### CSV

| Variable             | CLI Flag          | Default | Opciones         |
| -------------------- | ----------------- | ------- | ---------------- |
| `csv_separator`      | `--csv-separator` | `,`     | Cualquier carácter |
| `csv_include_header` | —                 | `true`  | `true` / `false` |
| `csv_null_value`     | —                 | `""`    | Cualquier string |
| `csv_date_format`    | —                 | `None`  | ISO 8601 o patrón personalizado |

#### DuckDB

| Variable        | CLI Flag | Default          | Opciones       |
| --------------- | -------- | ---------------- | -------------- |
| `duckdb_db_name` | —       | `contoso.duckdb` | Nombre archivo |

#### Delta Lake

| Variable             | CLI Flag       | Default     | Opciones                        |
| -------------------- | -------------- | ----------- | ------------------------------- |
| `delta_mode`         | `--delta-mode` | `overwrite` | `overwrite`, `append`, `error`  |
| `delta_partition_by` | —              | `None`      | Lista de columnas (ej: `["Year"]`) |
| `delta_name`         | —              | `contoso`   | Nombre metadata                 |

#### JSON

| Variable            | CLI Flag                        | Default | Opciones         |
| ------------------- | ------------------------------- | ------- | ---------------- |
| `json_row_oriented` | `--json-rows` / `--json-ndjson` | `false` | `true` = JSON array, `false` = NDJSON |
| `json_pretty`       | —                               | `false` | `true` / `false` |

#### Excel

| Variable                | CLI Flag                          | Default         | Opciones         |
| ----------------------- | --------------------------------- | --------------- | ---------------- |
| `excel_single_workbook` | `--excel-single` / `--excel-multi` | `true`         | `true` = uno, `false` = por tabla |
| `excel_workbook_name`   | —                                 | `contoso.xlsx`  | Nombre archivo   |

#### SQL Server

| Variable                       | CLI Flag             | Default          | Opciones                           |
| ------------------------------ | -------------------- | ---------------- | ---------------------------------- |
| `sqlserver_server`             | `--sqlserver-name`   | `localhost`      | Instancia (ej: `localhost\SQLEXPRESS`) |
| `sqlserver_database`           | `--sqlserver-db`     | `ContosoRetail`  | Nombre DB                          |
| `sqlserver_schema`             | `--sqlserver-schema` | `dbo`            | Esquema destino                    |
| `sqlserver_if_exists`          | `--sqlserver-mode`   | `replace`        | `replace`, `append`, `fail`        |
| `sqlserver_batch_size`         | —                    | `5,000`          | Filas por INSERT batch             |
| `sqlserver_driver`             | —                    | Auto-detect      | Nombre driver ODBC                 |
| `sqlserver_trusted`            | —                    | `true`           | Windows Auth (`true`) o SQL Auth   |
| `sqlserver_username`           | —                    | `None`           | Usuario SQL (si trusted=false)     |
| `sqlserver_password`           | —                    | `None`           | Password SQL (si trusted=false)    |
| `sqlserver_connection_string`  | —                    | `None`           | ODBC string completa (override)    |

### 👥 Clientes (`[customers]`)

| Variable           | Default   | Opciones         | Descripción                                 |
| ------------------ | --------- | ---------------- | ------------------------------------------- |
| `pool_size`        | `50,000`  | > 0              | Total de clientes únicos en el universo     |
| `active_pct`       | `0.30`    | 0.01 – 1.0       | % de clientes que compran al menos 1 vez    |
| `online_pct_start` | `0.05`    | 0.0 – 1.0        | % ventas online al inicio del período       |
| `online_pct_end`   | `0.55`    | 0.0 – 1.0        | % ventas online al final (crecimiento)      |

### 📂 Categorías (`[categories]`)

| Variable       | Default                                        | Descripción                   |
| -------------- | ---------------------------------------------- | ----------------------------- |
| `enabled`      | `["electronics", "home", "gaming", "media"]`   | Categorías activas            |
| `custom_paths` | `[]`                                           | Rutas a plugins YAML custom   |

---

## Location & Invocation

- **Project root**: `d:\PAL-TEMPORAL-REPORSITORIOS\contoso-universe-gen`
- **Invoke**: `.venv\Scripts\python.exe -m cug <command>` (from project root)
- **Or globally**: `cug <command>` (if installed via `pip install -e .`)
- **Python**: 3.12+ with `uv` virtual environment

## Commands

| Command          | Purpose                            |
| ---------------- | ---------------------------------- |
| `cug generate`   | Generate a full dataset            |
| `cug formats`    | Show all supported output formats  |
| `cug info`       | Show available languages           |
| `cug categories` | Show product categories            |
| `cug init [DIR]` | Copy default config template       |

## SQL Server Environment (User's Machine)

- **Server**: `localhost\SQLEXPRESS` (SQL Server Express 2019)
- **Auth**: Windows Authentication (Trusted_Connection=yes)
- **ODBC Driver**: ODBC Driver 17 for SQL Server (auto-detected)

### Known Issues (CRITICAL — handled automatically)

1. **Boolean → BIT**: Cast to `1`/`0` for `fast_executemany`
2. **Null type**: Polars `Null` → `NVARCHAR(1) NULL`
3. **Small integers**: Cast to Python `int` for ODBC
4. **Encoding**: Do NOT use `conn.setencoding(encoding="utf-8")` — corrupts NVARCHAR
5. **fast_executemany fallback**: Auto row-by-row on failure
6. **ODBC Driver 18**: Auto `TrustServerCertificate=yes`

## Generated Tables (Star Schema)

| Table                 | Type      | Key Columns                                    |
| --------------------- | --------- | ---------------------------------------------- |
| `DimDate`             | Dimension | DateKey, Year, Month, Quarter, DayName         |
| `DimCustomer`         | Dimension | CustomerKey, CustomerName, City, Country       |
| `DimProduct`          | Dimension | ProductKey, ProductName, Category, Subcategory |
| `DimStore`            | Dimension | StoreKey, StoreName, StoreType, Country        |
| `DimCurrency`         | Dimension | CurrencyKey, CurrencyCode, CurrencyName       |
| `DimCurrencyExchange` | Dimension | CurrencyCode, Date, ExchangeRate               |
| `FactSales`           | Fact      | OrderKey, CustomerKey, ProductKey, StoreKey    |

## Quick Recipes

```bash
# Quick test (~5K orders)
cug generate -c configs/quicktest.toml

# 100K orders to SQL Server
cug generate -n 100000 -f sqlserver --sqlserver-name "localhost\SQLEXPRESS" --sqlserver-db ContosoDemo

# 1M orders, Spanish, Parquet
cug generate -n 1000000 -f parquet -l es --strict

# Multi-format for workshop
cug generate -n 50000 -f parquet,csv,duckdb -l es

# Parquet + SQL Server simultaneously
cug generate -n 100000 -f parquet,sqlserver --sqlserver-name "localhost\SQLEXPRESS" --sqlserver-db ContosoRetail

# Delta Lake for Fabric
cug generate -n 500000 -f delta --delta-mode overwrite

# Reproducible
cug generate --seed 42 -n 100000 -f parquet -o ./output/v1
```

## Configuration Files

| Config                       | Description                |
| ---------------------------- | -------------------------- |
| `configs/default.toml`      | Standard config, 100K      |
| `configs/quicktest.toml`    | Quick test, ~5K orders     |
| `configs/retail_1M_en.toml` | 1M orders, English         |
| `configs/retail_1M_es.toml` | 1M orders, Spanish         |
| `configs/retail_10M_es.toml`| 10M orders, Spanish        |

## Dependencies

Core: `polars`, `duckdb`, `faker`, `pydantic`, `typer`, `rich`, `pyodbc`

---

## YAML Category Plugin System

> **Full guide**: [`docs/category-plugins.md`](../../../docs/category-plugins.md)

CUG uses YAML files to define product categories. The 4 builtins live in
`cug/categories/builtin/` (electronics, gaming, home, media). Users can create
custom categories without touching Python code.

### YAML Schema (Quick Reference)

```yaml
plugin_id: fashion                # Unique snake_case ID (required)
display_names:                    # Localized names (at least "en" required)
  en: Fashion & Apparel
  es: Moda y Ropa
subcategories:                    # At least 1 required
  - id: shoes                    # Unique snake_case ID
    display_names: {en: Shoes, es: Zapatos}
    brands: [Nike, Adidas]        # Available brands
    price_range: [40.0, 350.0]    # [min, max] unit price
    margin_range: [0.15, 0.45]    # [min, max] margin (0-1)
    trend:                        # Annual demand multiplier
      2020: 0.60                  # COVID drop
      2024: 1.20                  # Growth year
    products:                     # Name templates
      - name_template: "{brand} {model} {spec}"
        models: [Air Max, Superstar]
        specs: [Size 8, Size 10]
        brands: []                # [] = inherit from subcategory
```

### How to Register a Custom Plugin

Add to the TOML config:

```toml
[categories]
enabled = ["electronics", "home", "gaming", "media", "fashion"]
custom_paths = ["./my_plugins/fashion.yaml"]
```

> The `plugin_id` in the YAML must match the name in `enabled`.

### Key Defaults

| Field | Default if omitted |
|-------|--------------------|
| `display_names` | `{en: <plugin_id>}` |
| `price_range` | `[99, 999]` |
| `margin_range` | `[0.10, 0.30]` |
| `name_template` | `{brand} {model}` |
| Products per subcategory | 5–15 (random) |

---

## Language (`language`) Impact Reference

> **Full guide**: [`docs/i18n-reference.md`](../../../docs/i18n-reference.md)

### What DOES change per language

| Component | What changes | Scope |
|-----------|-------------|-------|
| `MonthName` / `DayName` | Translated month/day names | DimDate (en/es/pt/fr/de only — zh/ja/ar fallback to English) |
| `CategoryName` | YAML `display_names` | DimProduct |
| `SubCategoryName` | YAML `display_names` | DimProduct |
| Customer cities | Different city pools per lang | DimCustomer (en→US/CA/GB, es→MX/CO/AR, pt→BR/PT) |
| Customer countries | Different geo distributions | DimCustomer |
| Store countries | Different retail footprints | DimStore (en→6 countries, es→7 countries) |
| Primary currency | Language-mapped currency | FactSales (en→USD, es→MXN, pt→BRL, fr/de→EUR) |
| Holidays | Country-specific holidays | DimDate (`IsHoliday`, `HolidayName`) |

### What does NOT change (always English)

| Element | Example | Reason |
|---------|---------|--------|
| **Column headers** | `ProductKey`, `OrderDate` | Fixed schema — NOT localized |
| Product names | `Dell Laptop i7/32GB` | Templates in English |
| Manufacturer / Brand | `Contoso Ltd.`, `Apple` | Global names |
| Color / WeightUnit | `Black`, `kg` | Static English lists |
| CurrencyCode / CurrencyName | `USD`, `US Dollar` | ISO catalogue |
| Store Status | `Online`, `Current` | Fixed enum |

> ⚠️ **Header localization** (e.g., `ProductKey` → `ClaveProducto`) is planned
> as an opt-in feature in a future version (see ROADMAP v0.3+).
