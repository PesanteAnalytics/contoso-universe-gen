# Quick Recipes

> Common scenarios solved with a single command. Copy and paste directly into your terminal.

---

## 🧪 Quick Test

The most basic scenario: verify everything works.

```bash
# ~5K orders, parquet format, quicktest config
cug generate -c configs/quicktest.toml
```

**Output:** `./output/` with `.parquet` files for each table.

---

## 📊 Power BI Dataset (Parquet)

The most common case: generate data for importing into Power BI Desktop.

```bash
# 100K orders in Parquet (optimal format for Power BI)
cug generate -n 100000 -f parquet
```

For Power BI in Spanish:

```bash
cug generate -n 100000 -f parquet -l es
```

---

## 🗄️ Local SQL Server Express

Load data directly into SQL Server Express with Windows Authentication.

```bash
# 100K orders into SQL Server Express
cug generate -n 100000 -f sqlserver \
  --sqlserver-name "localhost\SQLEXPRESS" \
  --sqlserver-db ContosoRetail
```

---

## 🔗 Parquet + SQL Server (simultaneous)

Generate both formats in a single run — local files and database.

```bash
cug generate -n 100000 -f parquet,sqlserver \
  --sqlserver-name "localhost\SQLEXPRESS" \
  --sqlserver-db ContosoRetail
```

---

## 🎓 Workshop / Training

Multi-format so participants can choose their preferred tool.

```bash
# Parquet + CSV + DuckDB, in Spanish, 50K orders
cug generate -n 50000 -f parquet,csv,duckdb -l es
```

---

## 🏭 Production Dataset (1M orders)

For scale testing with integrity validation.

```bash
# Use predefined config (1M, Spanish, strict)
cug generate -c configs/retail_1M_es.toml --strict
```

Or manually:

```bash
cug generate -n 1000000 -f parquet -l es --strict
```

---

## ☁️ Microsoft Fabric / Lakehouse (Delta)

Generate Delta Lake tables ready to upload to OneLake.

```bash
cug generate -n 500000 -f delta --delta-mode overwrite
```

---

## 📤 Export to CSV (compatible with everything)

For sharing data with systems that only accept CSV.

```bash
# Standard CSV (with automatic gzip compression)
cug generate -n 200000 -f csv

# CSV with semicolon (for European locales)
cug generate -n 100000 -f csv --csv-separator ";"
```

---

## 📋 API Test Data (JSON)

Generate data in JSON format for API testing.

```bash
# NDJSON (one record per line, ideal for streaming)
cug generate -n 10000 -f json

# JSON array (ideal for REST payloads)
cug generate -n 5000 -f json --json-rows
```

---

## 📎 Sharing with Excel

For stakeholders who prefer Excel.

```bash
# Everything in a single workbook (one sheet per table)
cug generate -n 20000 -f excel

# One .xlsx file per table
cug generate -n 20000 -f excel --excel-multi
```

> ⚠️ Excel has a limit of ~1M rows per sheet. Use `parquet` for large datasets.

---

## 🔄 Guaranteed Reproducibility

Generate the exact same dataset every time.

```bash
# Same seed = same output
cug generate --seed 42 -n 100000 -f parquet -o ./output/v1

# Another version with a different seed
cug generate --seed 2024 -n 100000 -f parquet -o ./output/v2
```

---

## 🌍 Multi-Language

Generate datasets in different languages.

```bash
# Spanish
cug generate -n 50000 -f parquet -l es

# Portuguese
cug generate -n 50000 -f parquet -l pt

# Chinese
cug generate -n 50000 -f parquet -l zh

# Arabic
cug generate -n 50000 -f parquet -l ar
```

View available languages:

```bash
cug info
```

---

## 🔍 Query Generated DuckDB

After generating in DuckDB format, you can query immediately:

```bash
# Generate
cug generate -n 100000 -f duckdb

# Query with DuckDB CLI
duckdb ./output/contoso.duckdb
```

```sql
-- Sales by year
SELECT d.Year, COUNT(*) as Sales, SUM(f.TotalAmount) as Total
FROM FactSales f
JOIN DimDate d ON f.OrderDateKey = d.DateKey
GROUP BY d.Year
ORDER BY d.Year;

-- Top 10 best-selling products
SELECT p.ProductName, SUM(f.Quantity) as Units
FROM FactSales f
JOIN DimProduct p ON f.ProductKey = p.ProductKey
GROUP BY p.ProductName
ORDER BY Units DESC
LIMIT 10;
```

---

## 🏗️ Full Scenario (all formats)

To generate absolutely everything in a single run:

```bash
cug generate -n 100000 \
  -f parquet,csv,duckdb,delta,json,excel,sqlserver \
  --sqlserver-name "localhost\SQLEXPRESS" \
  --sqlserver-db ContosoRetail \
  -l es \
  --strict
```

---

## ⚡ Performance Guide

| target_orders | Approx. Time | Approx. Memory |
|--------------|-------------|----------------|
| 5,000 | ~5 sec | ~100 MB |
| 100,000 | ~30 sec | ~500 MB |
| 1,000,000 | ~5 min | ~2 GB |
| 10,000,000 | ~45 min | ~8 GB |

> [!TIP]
> For very large datasets (>5M), reduce `chunk_days` in the TOML config to control memory usage.

---

← [SQL Server](sqlserver.md) | [Back to index](README.md)
