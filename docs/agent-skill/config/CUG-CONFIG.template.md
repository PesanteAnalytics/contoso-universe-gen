# CUG Configuration Card — Template

> **Instructions**: Copy this file to your project root as `CUG-CONFIG.md`.
> The agent will read and update this file automatically during every generation session.
> You can edit any value directly in your IDE.

---

## 🔧 General

| Variable | Value | Options |
|---|---|---|
| `start_date` | `2018-01-01` | Any `YYYY-MM-DD` date |
| `end_date` | `2026-12-31` | Any `YYYY-MM-DD` date |
| `language` | `en` | `en`, `es`, `pt`, `fr`, `de`, `zh`, `ja`, `ar` |
| `country` | `US` | ISO 3166-1 code |
| `seed` | `42` | Any integer |
| `chunk_days` | `30` | > 0 |

---

## 📤 Output

| Variable | Value | Options |
|---|---|---|
| `output_path` | `./output` | Any directory |
| `formats` | `parquet` | `parquet`, `csv`, `duckdb`, `delta`, `json`, `excel`, `sqlserver` |
| `target_orders` | `100000` | > 0 |
| `compress` | `true` | `true` / `false` |
| `integrity_check` | `false` | `true` / `false` |
| `integrity_strict` | `true` | `true` / `false` |

---

## 📄 Format Options

### Parquet

| Variable | Value | Options |
|---|---|---|
| `parquet_compression` | `snappy` | `snappy`, `gzip`, `brotli`, `zstd`, `none` |

### CSV

| Variable | Value | Options |
|---|---|---|
| `csv_separator` | `,` | Any single character |

### DuckDB

| Variable | Value | Options |
|---|---|---|
| `duckdb_views` | `true` | `true` / `false` |

### Delta

| Variable | Value | Options |
|---|---|---|
| `delta_mode` | `overwrite` | `overwrite`, `append` |

### JSON

| Variable | Value | Options |
|---|---|---|
| `json_format` | `ndjson` | `rows`, `ndjson` |

### Excel

| Variable | Value | Options |
|---|---|---|
| `excel_mode` | `multi` | `single`, `multi` |

### SQL Server

| Variable | Value | Options |
|---|---|---|
| `sqlserver_name` | `<sql_server_instance>` | Server instance name |
| `sqlserver_db` | `ContosoDemo` | Database name |
| `sqlserver_schema` | `dbo` | Schema name |
| `sqlserver_mode` | `replace` | `replace`, `append` |

---

## 👥 Customers

| Variable | Value | Options |
|---|---|---|
| `pool_size` | `50000` | > 0 |
| `active_pct` | `0.30` | 0.01 – 1.0 |
| `online_pct_start` | `0.05` | 0.0 – 1.0 |
| `online_pct_end` | `0.55` | 0.0 – 1.0 |

---

## 📂 Categories

| Variable | Value | Description |
|---|---|---|
| `enabled` | `electronics, home, gaming, media` | Active categories (comma-separated) |
| `custom_paths` | | Paths to custom YAML plugins (comma-separated) |

---

## 📅 Annual Events

| Name | Month | Day | Factor |
|---|---|---|---|
| Black Friday | 11 | 28 | 4.0 |
| Cyber Monday | 12 | 2 | 3.5 |
| Christmas | 12 | 25 | 2.0 |
| Valentine's Day | 2 | 14 | 1.8 |

---

## 📅 Historical Events

| Name | Date Start | Date End | Factor |
|---|---|---|---|
| COVID Impact | 2020-03-01 | 2021-06-30 | 0.4 |
| Post-COVID Recovery | 2021-07-01 | 2022-12-31 | 1.3 |

---

## 📊 Weekday Factors

| Day | Factor |
|---|---|
| Monday | 0.85 |
| Tuesday | 0.80 |
| Wednesday | 0.90 |
| Thursday | 0.95 |
| Friday | 1.20 |
| Saturday | 1.60 |
| Sunday | 1.40 |

---

> **Last run**: _not yet executed_
> **Last modified**: _2026-03-20_
