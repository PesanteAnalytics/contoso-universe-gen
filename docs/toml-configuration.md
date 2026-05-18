# TOML Configuration

> Complete structure of the CUG `.toml` configuration file with detailed explanations of each section and variable.

---

## Location

Configuration files are located in `configs/`:

| File | Description |
|------|-------------|
| `configs/default.toml` | Standard configuration, 100K orders |
| `configs/quicktest.toml` | Quick test, ~5K orders |
| `configs/retail_1M_en.toml` | 1M orders in English |
| `configs/retail_1M_es.toml` | 1M orders in Spanish |
| `configs/retail_10M_es.toml` | 10M orders in Spanish |

To create your own configuration:

```bash
cug init ./my_project
# Generates: ./my_project/my_config.toml
```

---

## TOML File Sections

### `[general]` — General Configuration

```toml
[general]
start_date  = "2018-01-01"   # Start of the time range (YYYY-MM-DD)
end_date    = "2026-03-05"   # End of the time range
language    = "en"           # Language: en | es | pt | fr | de | zh | ja | ar
country     = "US"           # Country for data generation (ISO 3166-1)
seed        = 42             # Master seed (same seed = same output)
chunk_days  = 30             # Days processed per chunk (adjusts memory vs. speed)
```

| Variable | Default | Options | Description |
|----------|---------|---------|-------------|
| `start_date` | `2018-01-01` | Any date `YYYY-MM-DD` | Start of the sales time range |
| `end_date` | `2026-03-05` | Any date `YYYY-MM-DD` | End of the sales time range |
| `language` | `en` | `en`, `es`, `pt`, `fr`, `de`, `zh`, `ja`, `ar` | Language for customer names, products, and categories |
| `country` | `US` | ISO 3166-1 code | Country for holidays and data localization |
| `seed` | `42` | Any integer | Master random seed. Same seed = same dataset |
| `chunk_days` | `30` | > 0 | Days per processing chunk. Lower values = less memory, slower |

> [!TIP]
> For very large datasets (>5M orders), reduce `chunk_days` to `15` to avoid memory issues.

---

### `[output]` — Output Configuration

```toml
[output]
output_path      = "./output"       # Output directory
formats          = ["parquet"]      # Formats to write
target_orders    = 100_000          # Target orders (~approximate)
compress         = true             # Gzip compression for CSV
integrity_check  = false            # Enable FK validation
integrity_strict = true             # Abort on violation (vs. report only)
```

| Variable | Default | Options | Description |
|----------|---------|---------|-------------|
| `output_path` | `./output` | Any directory | Directory where generated files are saved |
| `formats` | `["parquet"]` | Combinable list | Output formats (see [Formats](output-formats.md)) |
| `target_orders` | `100,000` | > 0 | Approximate number of orders. Actual result varies ±5% |
| `compress` | `true` | `true` / `false` | Apply Gzip compression to CSV files |
| `integrity_check` | `false` | `true` / `false` | Enable referential integrity (FK) validation |
| `integrity_strict` | `true` | `true` / `false` | If `true`, aborts with error on FK violations |

**Available formats:** `parquet`, `csv`, `duckdb`, `delta`, `json`, `excel`, `sqlserver`

```toml
# Example: multiple simultaneous formats
formats = ["parquet", "csv", "duckdb"]
```

### Integrity Modes

| Mode | Config | CLI Flag | Behavior |
|------|--------|----------|----------|
| **Disabled** | `integrity_check = false` | — | No validation. Maximum speed |
| **Report-only** | `integrity_check = true`, `integrity_strict = false` | `--no-strict` | Prints report and continues |
| **Strict** | `integrity_check = true`, `integrity_strict = true` | `--strict` | Aborts with detailed error |

> [!NOTE]
> CLI flags (`--strict` / `--no-strict`) always override the config value.

---

### `[output.format_options]` — Format-Specific Options

Each format has specific options. All are optional — sensible defaults are used.

```toml
[output.format_options]
```

#### Parquet

```toml
parquet_compression     = "zstd"        # zstd | snappy | gzip | lz4 | brotli | none
# parquet_row_group_size = 100000       # rows per row group (default: auto)
```

| Variable | Default | Options | Description |
|----------|---------|---------|-------------|
| `parquet_compression` | `zstd` | `zstd`, `snappy`, `gzip`, `lz4`, `brotli`, `none` | Compression algorithm |
| `parquet_row_group_size` | `None` (auto) | Positive integer | Rows per row group |

#### CSV

```toml
csv_separator           = ","           # field delimiter
csv_include_header      = true          # include header row
csv_null_value          = ""            # null value representation
# csv_date_format       = "%Y-%m-%d"   # date format (default: ISO 8601)
```

| Variable | Default | Options | Description |
|----------|---------|---------|-------------|
| `csv_separator` | `,` | Any character | Field delimiter |
| `csv_include_header` | `true` | `true` / `false` | Include header row |
| `csv_null_value` | `""` | Any string | NULL value representation |
| `csv_date_format` | `None` (ISO 8601) | Date pattern | Date format in CSV |

#### DuckDB

```toml
duckdb_db_name          = "contoso.duckdb"
```

| Variable | Default | Description |
|----------|---------|-------------|
| `duckdb_db_name` | `contoso.duckdb` | Database file name |

#### Delta Lake

```toml
delta_mode              = "overwrite"   # overwrite | append | error
# delta_partition_by    = ["Year"]      # partition FactSales by column(s)
delta_name              = "contoso"     # name in metadata
```

| Variable | Default | Options | Description |
|----------|---------|---------|-------------|
| `delta_mode` | `overwrite` | `overwrite`, `append`, `error` | Write mode |
| `delta_partition_by` | `None` | List of columns | Columns to partition by (e.g. `["Year"]`) |
| `delta_name` | `contoso` | Any string | Name in Delta metadata |

#### JSON / NDJSON

```toml
json_row_oriented       = false         # false = NDJSON, true = JSON array
json_pretty             = false         # pretty-print (only with row_oriented = true)
```

| Variable | Default | Options | Description |
|----------|---------|---------|-------------|
| `json_row_oriented` | `false` | `true` / `false` | `false` = NDJSON (one record per line), `true` = JSON array |
| `json_pretty` | `false` | `true` / `false` | Human-readable format. Only applies with `row_oriented = true` |

#### Excel

```toml
excel_single_workbook   = true          # true = all in one .xlsx, false = one per table
excel_workbook_name     = "contoso.xlsx"
```

| Variable | Default | Options | Description |
|----------|---------|---------|-------------|
| `excel_single_workbook` | `true` | `true` / `false` | `true` = all tables in a single workbook |
| `excel_workbook_name` | `contoso.xlsx` | File name | Excel workbook name |

#### SQL Server

```toml
# sqlserver_server            = "localhost\\SQLEXPRESS"
# sqlserver_database          = "ContosoRetail"
# sqlserver_schema            = "dbo"
# sqlserver_driver            = "ODBC Driver 17 for SQL Server"  # auto-detected
# sqlserver_trusted           = true           # Windows Auth
# sqlserver_username          = ""             # SQL Auth only
# sqlserver_password          = ""             # SQL Auth only
# sqlserver_if_exists         = "replace"      # replace | append | fail
# sqlserver_batch_size        = 5000           # rows per INSERT batch
# sqlserver_connection_string = ""             # Full ODBC string (override)
```

For complete SQL Server details, see [sqlserver.md](sqlserver.md).

---

### `[customers]` — Customer Configuration

```toml
[customers]
pool_size         = 50_000   # Total unique customers in the universe
active_pct        = 0.30     # Fraction of customers who buy at least once
online_pct_start  = 0.05     # % of online orders at the start of the period
online_pct_end    = 0.55     # % of online orders at the end of the period
```

| Variable | Default | Range | Description |
|----------|---------|-------|-------------|
| `pool_size` | `50,000` | > 0 | Total unique customers generated |
| `active_pct` | `0.30` | 0.01 – 1.0 | % of customers who make at least one purchase |
| `online_pct_start` | `0.05` | 0.0 – 1.0 | % of online sales at the start of the period |
| `online_pct_end` | `0.55` | 0.0 – 1.0 | % of online sales at the end (linear growth) |

> [!TIP]
> The linear growth from `online_pct_start` to `online_pct_end` simulates the progressive digitalization of retail commerce.

---

### `[categories]` — Product Categories

```toml
[categories]
enabled      = ["electronics", "home", "gaming", "media"]
custom_paths = []
```

| Variable | Default | Description |
|----------|---------|-------------|
| `enabled` | `["electronics", "home", "gaming", "media"]` | Active categories for generation |
| `custom_paths` | `[]` | Paths to YAML files with custom categories (plugins) |

---

### `[[events.annual]]` — Annual Recurring Events

Events that occur every year and affect demand.

```toml
[[events.annual]]
name   = "Black Friday"
month  = 11
day    = 25
factor = 2.8    # Sales multiplier for that day (2.8x the base demand)
```

| Variable | Description |
|----------|-------------|
| `name` | Event name |
| `month` | Month (1-12) |
| `day` | Day of the month |
| `factor` | Demand multiplier. 1.0 = no change, 2.0 = double, 0.5 = half |

**Default events included:**

| Event | Month/Day | Factor | Description |
|-------|-----------|--------|-------------|
| Black Friday | 11/25 | 2.8x | Peak retail sales |
| Cyber Monday | 11/28 | 2.5x | Online peak post Black Friday |
| Christmas | 12/25 | 2.0x | Holiday season |
| Back to School | 8/15 | 1.8x | Back to school season |
| Prime Day | 7/12 | 2.5x | Online sales event |

---

### `[[events.one_time]]` — One-Time Historical Events

Events that occur once within a date range.

```toml
[[events.one_time]]
name       = "COVID Lockdown Drop"
date_start = "2020-03-15"
date_end   = "2020-04-30"
factor     = 0.45    # Sales at 45% of base (55% drop)
```

| Variable | Description |
|----------|-------------|
| `name` | Event name |
| `date_start` | Start date (`YYYY-MM-DD`) |
| `date_end` | End date (`YYYY-MM-DD`) |
| `factor` | Demand multiplier during the period |

**Default one-time events included:**

| Event | Period | Factor | Description |
|-------|--------|--------|-------------|
| COVID Lockdown Drop | Mar–Apr 2020 | 0.45x | Lockdown drop |
| COVID eCommerce Surge | May 2020–Mar 2021 | 1.18x | Online commerce boom |
| Post-COVID Recovery | Apr 2021–Jun 2022 | 1.06x | Gradual recovery |
| Inflation Pressure 2022 | Jan–Dec 2022 | 0.92x | Inflationary pressure |
| AI & Electronics Boom | Jun 2023–Dec 2024 | 1.09x | AI boom and tech renewal |

---

### `[weekday_factors]` — Day-of-Week Factors

```toml
[weekday_factors]
# Indices: 0=Mon, 1=Tue, 2=Wed, 3=Thu, 4=Fri, 5=Sat, 6=Sun
factors = [0.75, 0.85, 0.95, 1.05, 1.20, 1.60, 0.30]
```

| Day | Default Factor | Description |
|-----|---------------|-------------|
| Monday | 0.75 | Lowest day (except Sunday) |
| Tuesday | 0.85 | Slightly below average |
| Wednesday | 0.95 | Close to average |
| Thursday | 1.05 | Slightly above |
| Friday | 1.20 | Significant increase |
| **Saturday** | **1.60** | **Peak sales day** |
| Sunday | 0.30 | Lowest day of the week |

---

← [CLI Reference](cli-reference.md) | [Output Formats →](output-formats.md)
