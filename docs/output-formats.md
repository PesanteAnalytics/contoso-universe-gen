# Output Formats

> The 7 formats supported by CUG, with format-specific options and usage recommendations.

---

## Format Summary

| Format | Extension / Target | Description | Primary Use Case |
|--------|-------------------|-------------|-----------------|
| **parquet** ★ | `.parquet` | Compressed columnar with native types | Power BI, Spark, Fabric Direct Lake |
| **csv** | `.csv` / `.csv.gz` | Plain text, optionally compressed | Universal compatibility |
| **duckdb** | `.duckdb` | Embedded analytical database | Immediate SQL queries |
| **delta** | Delta Lake | Delta tables with versioning | Fabric, Databricks, Lakehouse |
| **json** | `.json` / `.ndjson` | JSON array or NDJSON | APIs, web integration, debugging |
| **excel** | `.xlsx` | Excel workbook | Sharing with non-technical users |
| **sqlserver** | SQL Server DB | Tables in SQL Server database | Power BI DirectQuery, dashboards |

> ★ = default format when none is specified.

---

## Combining Formats

CUG can generate multiple formats in a single run:

```bash
# Single format (default)
cug generate -f parquet

# Two formats
cug generate -f parquet,csv

# Three formats
cug generate -f parquet,duckdb,delta

# As many as you need
cug generate -f parquet,csv,duckdb,sqlserver
```

---

## Parquet

**The recommended format for most analytical use cases.**

Generates one `.parquet` file per table (e.g. `FactSales.parquet`, `DimCustomer.parquet`).

### Options

| TOML Option | CLI Flag | Default | Values |
|-------------|----------|---------|--------|
| `parquet_compression` | `--parquet-compression` | `zstd` | `zstd`, `snappy`, `gzip`, `lz4`, `brotli`, `none` |
| `parquet_row_group_size` | — | Auto | Positive integer |

### Example

```bash
# Parquet with snappy compression (faster, less compression)
cug generate -n 100000 -f parquet --parquet-compression snappy

# Default Parquet (zstd, best compression/speed ratio)
cug generate -n 500000 -f parquet
```

### When to Use Parquet

- **Power BI Import mode** — Fast data loading
- **Spark / Databricks** — Efficient columnar reads
- **Microsoft Fabric Direct Lake** — Native format
- **Archival** — Excellent compression

---

## CSV

Generates `.csv` (or `.csv.gz` if `compress = true`) files — one per table.

### Options

| TOML Option | CLI Flag | Default | Description |
|-------------|----------|---------|-------------|
| `csv_separator` | `--csv-separator` | `,` | Field delimiter |
| `csv_include_header` | — | `true` | Include header row |
| `csv_null_value` | — | `""` | NULL value representation |
| `csv_date_format` | — | ISO 8601 | Date format |

### Example

```bash
# CSV with semicolon (for locales that use comma as decimal separator)
cug generate -n 50000 -f csv --csv-separator ";"

# Standard CSV
cug generate -n 100000 -f csv
```

### When to Use CSV

- **Manual Excel import**
- **Universal compatibility** with any tool
- **ETL pipelines** expecting plain text
- **Data exchange** between heterogeneous systems

---

## DuckDB

Generates an embedded DuckDB database (`.duckdb`) with all tables loaded.

### Options

| TOML Option | CLI Flag | Default | Description |
|-------------|----------|---------|-------------|
| `duckdb_db_name` | — | `contoso.duckdb` | Database file name |

### Example

```bash
cug generate -n 100000 -f duckdb
```

### Querying the Generated DuckDB

```sql
-- With DuckDB CLI
.open ./output/contoso.duckdb
SELECT COUNT(*) FROM FactSales;
SELECT Year, SUM(Quantity) FROM FactSales f JOIN DimDate d ON f.OrderDateKey = d.DateKey GROUP BY Year;

-- With Python
import duckdb
conn = duckdb.connect("./output/contoso.duckdb")
df = conn.sql("SELECT * FROM FactSales LIMIT 10").pl()
```

### When to Use DuckDB

- **Immediate SQL queries** without a server
- **Python Notebooks** — Direct integration with Polars/Pandas
- **Rapid prototyping** — Analytical database with zero infrastructure
- **DBeaver / DataGrip** — Exploration with GUI tools

---

## Delta Lake

Generates tables in Delta Lake format, ideal for lakehouses.

### Options

| TOML Option | CLI Flag | Default | Values |
|-------------|----------|---------|--------|
| `delta_mode` | `--delta-mode` | `overwrite` | `overwrite`, `append`, `error` |
| `delta_partition_by` | — | `None` | List of columns (e.g. `["Year"]`) |
| `delta_name` | — | `contoso` | Name in metadata |

### Example

```bash
# Delta Lake with overwrite
cug generate -n 500000 -f delta --delta-mode overwrite

# Delta Lake with year partitioning
# (configure in TOML: delta_partition_by = ["Year"])
cug generate -n 1000000 -f delta
```

### When to Use Delta

- **Microsoft Fabric** — Lakehouses and Warehouses
- **Databricks** — Native format
- **Apache Spark** — Versioning and ACID transactions
- **Time travel** — Version history

---

## JSON / NDJSON

Generates JSON files — either as a full JSON array or as NDJSON (one record per line).

### Options

| TOML Option | CLI Flag | Default | Description |
|-------------|----------|---------|-------------|
| `json_row_oriented` | `--json-rows` / `--json-ndjson` | `false` (NDJSON) | `true` = JSON array, `false` = NDJSON |
| `json_pretty` | — | `false` | Pretty-print (only with `row_oriented = true`) |

### Example

```bash
# NDJSON (default, one record per line)
cug generate -n 50000 -f json

# JSON array
cug generate -n 10000 -f json --json-rows
```

### When to Use JSON

- **REST APIs** — Test payloads
- **Streaming** — NDJSON for line-by-line ingestion
- **Debugging** — Human inspection of data
- **Web apps** — Test data for frontends

---

## Excel

Generates Excel `.xlsx` files — all tables in a single workbook or one per table.

### Options

| TOML Option | CLI Flag | Default | Description |
|-------------|----------|---------|-------------|
| `excel_single_workbook` | `--excel-single` / `--excel-multi` | `true` | `true` = one workbook, `false` = one per table |
| `excel_workbook_name` | — | `contoso.xlsx` | Excel file name |

### Example

```bash
# Single workbook with all tables as sheets
cug generate -n 20000 -f excel

# One .xlsx file per table
cug generate -n 20000 -f excel --excel-multi
```

> [!WARNING]
> Excel has a limit of ~1 million rows per sheet. For large datasets, use another format.

### When to Use Excel

- **Sharing with non-technical stakeholders**
- **Quick data exploration**
- **Presentations** and ad-hoc reports

---

## SQL Server

Writes directly to a SQL Server database via ODBC.

For detailed documentation, see [sqlserver.md](sqlserver.md).

### Main Options

| TOML Option | CLI Flag | Default | Description |
|-------------|----------|---------|-------------|
| `sqlserver_server` | `--sqlserver-name` | `localhost` | SQL Server instance |
| `sqlserver_database` | `--sqlserver-db` | `ContosoRetail` | Target database |
| `sqlserver_schema` | `--sqlserver-schema` | `dbo` | Target schema |
| `sqlserver_if_exists` | `--sqlserver-mode` | `replace` | `replace`, `append`, `fail` |
| `sqlserver_batch_size` | — | `5,000` | Rows per INSERT batch |
| `sqlserver_trusted` | — | `true` | Windows Authentication |

### Example

```bash
# Local SQL Server Express (Windows Auth)
cug generate -n 100000 -f sqlserver \
  --sqlserver-name "localhost\SQLEXPRESS" \
  --sqlserver-db ContosoRetail

# Parquet + SQL Server simultaneously
cug generate -n 50000 -f parquet,sqlserver \
  --sqlserver-name "localhost\SQLEXPRESS" \
  --sqlserver-db ContosoDemo
```

### When to Use SQL Server

- **Power BI DirectQuery** — Real-time queries
- **Enterprise dashboards** — Centralized data
- **SSAS Tabular** — Semantic model
- **Application integration** using SQL Server

---

← [TOML Configuration](toml-configuration.md) | [Data Schema →](data-schema.md)
