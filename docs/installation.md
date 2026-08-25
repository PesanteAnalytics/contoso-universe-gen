# Installation

> Installation guide for Contoso Universe Generator (CUG).

---

## Prerequisites

| Requirement | Minimum Version | Notes |
|-------------|----------------|-------|
| **Python** | 3.12+ | Recommended: use `uv` for environment management |
| **pip** or **uv** | Latest stable | `uv` is faster for dependency resolution |
| **ODBC Driver** | Driver 17 or 18 | Only required for `sqlserver` output format |
| **SQL Server** | Express 2019+ | Only required for `sqlserver` output format |

---

## Standard Installation (pip)

```bash
# Clone the repository
git clone https://github.com/PesanteAnalytics/contoso-universe-gen.git
cd contoso-universe-gen

# Create virtual environment
python -m venv .venv

# Activate environment (Windows)
.venv\Scripts\activate

# Install in editable mode
pip install -e .

# Verify installation
cug --help
```

---

## Installation with uv (recommended)

```bash
# Clone the repository
git clone https://github.com/PesanteAnalytics/contoso-universe-gen.git
cd contoso-universe-gen

# Create virtual environment with uv
uv venv .venv --python 3.12

# Activate environment (Windows)
.venv\Scripts\activate

# Install with uv
uv pip install -e .

# Verify installation
cug --help
```

---

## Dependencies

CUG automatically installs the following dependencies:

| Package | Purpose |
|---------|---------|
| `polars` | High-speed DataFrame engine |
| `duckdb` | Embedded analytical database |
| `numpy` | Vectorized RNG behind customer and sales generation |
| `pydantic` | Configuration validation |
| `typer` | CLI framework |
| `rich` | Rich-formatted console output |
| `pyodbc` | SQL Server connection via ODBC |
| `deltalake` | Delta Lake table writing |
| `openpyxl` | Excel file writing (.xlsx) |

---

## ODBC Driver Installation (SQL Server only)

If you plan to export data to SQL Server, you need to install an ODBC driver.

### Windows

1. Download from [Microsoft ODBC Driver for SQL Server](https://learn.microsoft.com/en-us/sql/connect/odbc/download-odbc-driver-for-sql-server)
2. Install **ODBC Driver 17** or **ODBC Driver 18** for SQL Server
3. Verify the installation:

```python
import pyodbc
print(pyodbc.drivers())
# Should include 'ODBC Driver 17 for SQL Server' or similar
```

### Supported Drivers (in order of preference)

1. `ODBC Driver 18 for SQL Server` — Latest version
2. `ODBC Driver 17 for SQL Server` — Widely available
3. `SQL Server Native Client 11.0` — Legacy, functional

> [!NOTE]
> CUG auto-detects the best available driver. No manual configuration is needed unless you have specific requirements.

> [!IMPORTANT]
> ODBC Driver 18 requires SSL by default. For local development, CUG automatically adds `TrustServerCertificate=yes` to the connection string.

---

## Verify the Installation

```bash
# View general help
cug --help

# View available languages
cug info

# View output formats
cug formats

# View product categories
cug categories

# Quick test generation (~5K orders)
cug generate -c configs/quicktest.toml
```

If all commands run successfully, the installation is complete.

---

## Alternative Invocation

If you did not install with `pip install -e .`, you can invoke CUG directly with:

```bash
# From the project root directory
.venv\Scripts\python.exe -m cug generate [OPTIONS]
```

---

## Common Troubleshooting

### `ModuleNotFoundError: No module named 'cug'`

Make sure you installed with `pip install -e .` from the project root directory.

### `ImportError: No module named 'pyodbc'`

```bash
pip install pyodbc
```

If it fails on Windows, verify that Visual C++ Build Tools are installed.

### `UnicodeEncodeError` when running CUG

CUG uses Unicode characters for the Rich interface. Make sure your terminal supports UTF-8:

```powershell
# PowerShell
[Console]::OutputEncoding = [System.Text.Encoding]::UTF8
$env:PYTHONIOENCODING = "utf-8"
```

---

← [Back to index](README.md)
