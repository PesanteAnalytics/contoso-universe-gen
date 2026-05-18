# SQL Server

> Complete guide for using CUG with SQL Server: prerequisites, authentication, type mapping, and troubleshooting.

---

## Prerequisites

### SQL Server

CUG is compatible with:

- **SQL Server Express** 2017+ (ideal for local development)
- **SQL Server Developer** 2017+
- **SQL Server Standard/Enterprise** 2017+
- **Azure SQL Database**
- **Azure SQL Managed Instance**

### ODBC Driver

CUG needs an ODBC driver to connect to SQL Server. The best available driver is auto-detected.

**Supported drivers (in order of preference):**

| Driver | Notes |
|--------|-------|
| ODBC Driver 18 for SQL Server | Latest version. Requires SSL/TLS (handled automatically) |
| ODBC Driver 17 for SQL Server | Widely available. Recommended |
| SQL Server Native Client 11.0 | Legacy, functional |

### Verify Installed Drivers

```python
import pyodbc
print(pyodbc.drivers())
# Example output: ['ODBC Driver 17 for SQL Server', 'SQL Server']
```

### Install ODBC Driver (if missing)

Download from: [Microsoft ODBC Driver for SQL Server](https://learn.microsoft.com/en-us/sql/connect/odbc/download-odbc-driver-for-sql-server)

---

## Authentication

CUG supports three authentication methods:

### Windows Authentication (recommended for development)

```toml
[output.format_options]
sqlserver_server  = "localhost\\SQLEXPRESS"
sqlserver_trusted = true    # default
```

```bash
cug generate -f sqlserver --sqlserver-name "localhost\SQLEXPRESS"
```

Uses the current Windows user credentials. No username/password needed.

### SQL Authentication

```toml
[output.format_options]
sqlserver_server   = "my-server.database.windows.net"
sqlserver_trusted  = false
sqlserver_username = "my_user"
sqlserver_password = "my_password"
```

For remote servers or Azure SQL.

### Full Connection String

```toml
[output.format_options]
sqlserver_connection_string = "DRIVER={ODBC Driver 17 for SQL Server};SERVER=localhost\\SQLEXPRESS;DATABASE=ContosoRetail;Trusted_Connection=yes"
```

Overrides all other connection options. Useful for advanced configurations.

---

## Configuration Options

### In the TOML File

```toml
[output.format_options]
sqlserver_server            = "localhost\\SQLEXPRESS"  # SQL Server instance
sqlserver_database          = "ContosoRetail"          # Target database
sqlserver_schema            = "dbo"                     # Target schema
sqlserver_driver            = "ODBC Driver 17 for SQL Server"  # Auto-detected if omitted
sqlserver_trusted           = true                      # Windows Auth (default)
sqlserver_username          = ""                        # SQL Auth only
sqlserver_password          = ""                        # SQL Auth only
sqlserver_if_exists         = "replace"                 # replace | append | fail
sqlserver_batch_size        = 5000                      # Rows per INSERT batch
sqlserver_connection_string = ""                        # Full ODBC string (override)
```

### Via CLI

| CLI Flag | TOML Equivalent | Default |
|----------|----------------|---------|
| `--sqlserver-name` | `sqlserver_server` | `localhost` |
| `--sqlserver-db` | `sqlserver_database` | `ContosoRetail` |
| `--sqlserver-schema` | `sqlserver_schema` | `dbo` |
| `--sqlserver-mode` | `sqlserver_if_exists` | `replace` |

---

## Writer Behavior

The SQL Server writer executes the following steps:

1. **Creates the database** automatically if it doesn't exist (connects to `master` first)
2. **Creates/replaces tables** with correctly mapped types
3. **Inserts data in batches** using `pyodbc.fast_executemany` for high performance
4. **Automatic fallback** to row-by-row insertion if `fast_executemany` fails on a table

### `if_exists` Modes

| Mode | Description |
|------|-------------|
| `replace` | Drops the existing table and recreates it (default) |
| `append` | Adds rows to the existing table |
| `fail` | Error if the table already exists |

---

## Type Mapping: Polars → SQL Server

| Polars Type | SQL Server Type | Notes |
|-------------|----------------|-------|
| `Int8` | `TINYINT` | |
| `Int16` | `SMALLINT` | |
| `Int32` | `INT` | |
| `Int64` | `BIGINT` | |
| `UInt8` | `SMALLINT` | SQL Server has no unsigned → promoted |
| `UInt16` | `INT` | SQL Server has no unsigned → promoted |
| `UInt32` | `BIGINT` | SQL Server has no unsigned → promoted |
| `UInt64` | `BIGINT` | SQL Server has no unsigned → promoted |
| `Float32` | `REAL` | |
| `Float64` | `FLOAT` | |
| `String` | `NVARCHAR(400)` | Unicode, 400 characters max |
| `Categorical` | `NVARCHAR(200)` | |
| `Boolean` | `BIT` | Converted to `1`/`0` internally |
| `Date` | `DATE` | |
| `Datetime` | `DATETIME2` | |
| `Time` | `TIME` | |
| `Duration` | `BIGINT` | Stored as microseconds |
| `Binary` | `VARBINARY(MAX)` | |
| `Decimal` | `DECIMAL(19,4)` | |
| `Null` | `NVARCHAR(1) NULL` | Columns where all values are `None` |

---

## Examples

### Case 1: Local SQL Server Express (most common)

```bash
cug generate -n 100000 -f sqlserver \
  --sqlserver-name "localhost\SQLEXPRESS" \
  --sqlserver-db ContosoRetail
```

### Case 2: Parquet + SQL Server simultaneously

```bash
cug generate -n 50000 -f parquet,sqlserver \
  --sqlserver-name "localhost\SQLEXPRESS" \
  --sqlserver-db ContosoDemo
```

### Case 3: Custom schema

```bash
cug generate -n 100000 -f sqlserver \
  --sqlserver-name "localhost\SQLEXPRESS" \
  --sqlserver-db MyDatabase \
  --sqlserver-schema staging
```

### Case 4: Append to existing table

```bash
cug generate -n 50000 -f sqlserver \
  --sqlserver-name "localhost\SQLEXPRESS" \
  --sqlserver-db ContosoRetail \
  --sqlserver-mode append
```

---

## Troubleshooting

### ❌ Error: `DataError` with `fast_executemany`

**Symptom:** Error inserting data in a table with `fast_executemany`.

**Solution:** CUG handles this automatically. If `fast_executemany` fails on a batch, it falls back to row-by-row insertion. You'll see a warning in the console but generation will continue.

**Root cause:** Mixed types or edge cases in certain columns that `fast_executemany` doesn't handle well.

---

### ❌ Corrupted characters (CJK/Unicode) in text columns

**Symptom:** Chinese (中文), Japanese (日本語), or Arabic (العربية) characters appear as `?` or garbled characters in SQL Server.

**Cause:** Manual encoding configuration on the connection.

**Solution:** **Do not** configure `conn.setencoding(encoding="utf-8")` manually. SQL Server uses UTF-16LE internally and `pyodbc` on Windows handles it correctly by default. Forcing UTF-8 **corrupts** `NVARCHAR` data.

> [!CAUTION]
> **Never** use `conn.setencoding(encoding="utf-8")` with pyodbc on Windows. This is the #1 cause of Unicode data corruption in SQL Server.

---

### ❌ Connection error with ODBC Driver 18

**Symptom:** `[Microsoft][ODBC Driver 18 for SQL Server]SSL Provider: The target principal name is incorrect`

**Cause:** Driver 18 requires a valid SSL certificate by default.

**Solution:** CUG automatically adds `TrustServerCertificate=yes` when it detects Driver 18. If you use `sqlserver_connection_string`, add it manually:

```
...;TrustServerCertificate=yes
```

---

### ❌ Boolean → BIT casting

**Symptom:** Error inserting `True`/`False` values into `BIT` columns.

**Solution:** CUG automatically converts `True` → `1` and `False` → `0` before insertion. This is required by `pyodbc.fast_executemany`.

---

### ❌ Small integers (Int8/UInt8) with ODBC

**Symptom:** Type error when inserting `Int8` or `UInt8` values.

**Solution:** CUG automatically converts these types to native Python `int` before insertion. `pyodbc` doesn't handle small NumPy/Polars integers well.

---

### ❌ Cannot auto-create database

**Symptom:** `Could not auto-create database: ...`

**Cause:** The user doesn't have `CREATE DATABASE` permissions on the instance.

**Solution:** Create the database manually:

```sql
CREATE DATABASE ContosoRetail;
```

CUG will print a warning but will continue trying to connect to the database.

---

### ❌ `ImportError: No module named 'pyodbc'`

**Solution:**

```bash
pip install pyodbc
```

If it fails on Windows, install [Visual C++ Build Tools](https://visualstudio.microsoft.com/visual-cpp-build-tools/).

---

## Developer Environment (reference)

This is the SQL Server configuration on the developer machine:

| Element | Value |
|---------|-------|
| **Server** | `localhost\SQLEXPRESS` |
| **Version** | SQL Server Express 2019 |
| **Auth** | Windows Authentication |
| **ODBC Driver** | ODBC Driver 17 for SQL Server |
| **Python** | 3.12+ with `uv` environment |

---

← [Data Schema](data-schema.md) | [Recipes →](recipes.md)
