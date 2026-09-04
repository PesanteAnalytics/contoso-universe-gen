# 📦 CUG — Active Configuration Card

> **Persistent configuration card** for the Contoso Universe Generator.
> Edit the values in the **Value** column and the agent will apply them automatically.
> The values shown here are the **defaults** — only change what you need.

---

## 🔧 General

| Parameter    | Value      | Options                              |
| ------------ | ---------- | ------------------------------------ |
| start_date   | 2022-01-01 | Date YYYY-MM-DD                      |
| end_date     | 2026-03-17 | Date YYYY-MM-DD                      |
| language     | en         | en, es, pt, fr, de, zh, ja, ar       |
| country      | US         | ISO 3166-1 alpha-2 code              |
| seed         | 42         | Any integer                          |
| chunk_days   | 30         | Integer > 0                          |

## 📤 Output

| Parameter        | Value                             | Options                                                                               |
| ---------------- | --------------------------------- | ------------------------------------------------------------------------------------- |
| output_path      | ./output                          | Directory path                                                                        |
| formats          | parquet, csv, duckdb, delta, json | parquet, csv, duckdb, delta, json, excel, sqlserver — comma-separated for multiple    |
| target_orders    | 1000000                           | Integer > 0 (≈ rows generated)                                                        |
| compress         | true                              | true / false — Gzip compression for CSV                                               |
| integrity_check  | false                             | true / false — validate FK integrity                                                  |
| integrity_strict | true                              | true / false — abort on FK violations                                                 |

## 📄 Format Options

> Only the options for the selected format(s) above apply.

### Parquet

| Parameter              | Value | Options                                |
| ---------------------- | ----- | -------------------------------------- |
| parquet_compression    | zstd  | zstd, snappy, gzip, lz4, brotli, none  |
| parquet_row_group_size | auto  | Integer or auto                        |

### CSV

| Parameter          | Value | Options                                    |
| ------------------ | ----- | ------------------------------------------ |
| csv_separator      | ,     | Any single character                       |
| csv_include_header | true  | true / false                               |
| csv_null_value     |       | Any string (empty = default)               |
| csv_date_format    | auto  | auto = ISO 8601, or pattern like %Y-%m-%d  |

### DuckDB

| Parameter      | Value          | Options                      |
| -------------- | -------------- | ---------------------------- |
| duckdb_db_name | contoso.duckdb | DuckDB output filename       |

### Delta Lake

| Parameter          | Value     | Options                                               |
| ------------------ | --------- | ----------------------------------------------------- |
| delta_mode         | overwrite | overwrite, append, error                              |
| delta_partition_by |           | Column list, e.g. Year (empty = no partitioning)      |
| delta_name         | contoso   | Delta log metadata name                               |

### JSON

| Parameter         | Value | Options                                                       |
| ----------------- | ----- | ------------------------------------------------------------- |
| json_row_oriented | false | false = NDJSON (1 record/line), true = JSON array             |
| json_pretty       | false | true / false — pretty-print (only with row_oriented = true)   |

### Excel

| Parameter             | Value        | Options                                                        |
| --------------------- | ------------ | -------------------------------------------------------------- |
| excel_single_workbook | true         | true = all tables in one .xlsx, false = one .xlsx per table    |
| excel_workbook_name   | contoso.xlsx | Excel filename                                                 |

### SQL Server

| Parameter                   | Value                | Options                                                    |
| --------------------------- | -------------------- | ---------------------------------------------------------- |
| sqlserver_server            | localhost\SQLEXPRESS | Server instance                                            |
| sqlserver_database          | ContosoRetail        | Target database (auto-created if possible)                 |
| sqlserver_schema            | dbo                  | Target schema                                              |
| sqlserver_driver            | auto                 | auto = detect, or exact ODBC driver name                   |
| sqlserver_trusted           | true                 | true = Windows Auth, false = SQL Auth                      |
| sqlserver_username          |                      | Only if trusted = false                                    |
| sqlserver_password          |                      | Only if trusted = false                                    |
| sqlserver_if_exists         | replace              | replace, append, fail                                      |
| sqlserver_batch_size        | 5000                 | Rows per INSERT batch                                      |
| sqlserver_connection_string |                      | Full ODBC string (overrides all settings above)            |

## 👥 Customers

| Parameter           | Value | Options                                            |
| ------------------- | ----- | -------------------------------------------------- |
| pool_size           | 50000 | Integer > 0 — total unique customers               |
| active_pct          | 0.30  | 0.01 – 1.0 — % that make at least 1 purchase       |
| online_pct_start    | 0.05  | 0.0 – 1.0 — % online orders at start_date          |
| online_pct_end      | 0.55  | 0.0 – 1.0 — % online orders at end_date            |
| avg_lines_per_order | 1.0   | 1.0 – 20.0 — 1.0 = one line per order              |
| max_lines_per_order | 8     | 1 – 50 — cap on basket size                        |

> `avg_lines_per_order` sets the basket. At 1.0 the fact table has one row per
> order, as it always did. Raise it and `FactSales` rows ≈ orders × this value.

## 🏷️ Customer Segments

> Cuts the **active** base into spend tiers, written out as `CustomerSegment`
> on `DimCustomer`. `Share` must add up to 1.0. `Demand` is how often a member
> shows up on an order relative to the smallest tier; `Lines` and `Qty` scale
> the basket and the units per line. Dormant customers are labelled `Inactive`
> and never appear in `FactSales`.
>
> The defaults put ~72% of orders — and ~80% of revenue — on the top 20% of the
> active base, which is the concentration real retail reports. To flatten it,
> move the demand weights toward 1.0.

| Segment     | Share | Demand | Lines | Qty  |
| ----------- | ----- | ------ | ----- | ---- |
| Key Account | 0.01  | 60.0   | 2.2   | 1.8  |
| Large       | 0.04  | 18.0   | 1.6   | 1.35 |
| Medium      | 0.15  | 5.0    | 1.2   | 1.1  |
| Small       | 0.80  | 1.0    | 1.0   | 1.0  |

## 📂 Categories

| Parameter    | Value                            | Options                                         |
| ------------ | -------------------------------- | ----------------------------------------------- |
| enabled      | electronics, home, gaming, media | Active categories, comma-separated               |
| custom_paths |                                  | Paths to custom YAML plugins (empty = none)      |

## 📅 Annual Events

> Recurring events that boost or reduce sales volume every year.
> To add: new row. To disable: delete the row or set factor = 1.0.

| Event          | Month | Day | Factor |
| -------------- | ----- | --- | ------ |
| Black Friday   | 11    | 25  | 2.8    |
| Cyber Monday   | 11    | 28  | 2.5    |
| Christmas      | 12    | 25  | 2.0    |
| Back to School | 8     | 15  | 1.8    |
| Prime Day      | 7     | 12  | 2.5    |

## 📅 Historical Events (One-Time)

> One-off events with impact over a specific date range.
> To add: new row. To disable: delete the row or set factor = 1.0.

| Event                          | Start Date | End Date   | Factor |
| ------------------------------ | ---------- | ---------- | ------ |
| COVID Lockdown Drop            | 2020-03-15 | 2020-04-30 | 0.45   |
| COVID eCommerce Surge          | 2020-05-01 | 2021-03-31 | 1.18   |
| Post-COVID Recovery            | 2021-04-01 | 2022-06-30 | 1.06   |
| Inflation Pressure 2022        | 2022-01-01 | 2022-12-31 | 0.92   |
| AI & Electronics Boom 2023-24  | 2023-06-01 | 2024-12-31 | 1.09   |

## 📊 Weekday Sales Factors

> Mon=0 … Sun=6. Factor 1.0 = average. Higher = more sales, lower = fewer.

| Day       | Factor |
| --------- | ------ |
| Monday    | 0.75   |
| Tuesday   | 0.85   |
| Wednesday | 0.95   |
| Thursday  | 1.05   |
| Friday    | 1.20   |
| Saturday  | 1.60   |
| Sunday    | 0.30   |

---

> **Last run**: _2026-03-12 16:15_
> **Last modified**: _2026-03-12 16:14_
