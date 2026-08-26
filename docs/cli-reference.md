# CLI Reference

> All commands available in the Contoso Universe Generator command-line interface.

---

## Invocation

```bash
# If installed with pip install -e .
cug <command> [options]

# If using the virtual environment directly
.venv\Scripts\python.exe -m cug <command> [options]
```

---

## Available Commands

| Command | Description |
|---------|-------------|
| `cug generate` | Generates a complete dataset |
| `cug info` | Shows available languages |
| `cug categories` | Shows product categories |
| `cug formats` | Shows available output formats |
| `cug init [DIR]` | Copies the configuration template to a directory |

---

## `cug generate` — Generate Dataset

The main command. Generates a complete retail dataset with dimension and fact tables.

```bash
cug generate [OPTIONS]
```

### General Options

| Option | Shorthand | Default | Description |
|--------|-----------|---------|-------------|
| `--config PATH` | `-c` | `default.toml` (built-in) | Path to `.toml` configuration file |
| `--output DIR` | `-o` | `./output` | Output directory. Overrides config value |
| `--language CODE` | `-l` | `en` | Language: `en`, `es`, `pt`, `fr`, `de`, `zh`, `ja`, `ar` |
| `--orders N` | `-n` | `100,000` | Approximate number of orders to generate |
| `--formats LIST` | `-f` | `parquet` | Comma-separated formats (see [Formats](output-formats.md)) |
| `--seed N` | — | `42` | Random seed for reproducibility |
| `--strict` | — | — | Abort on FK violations |
| `--no-strict` | — | — | Report violations but continue generating |
| `--verbose` | `-v` | `false` | Show detailed progress steps |

### Format-Specific Options

#### Parquet

| Option | Default | Values |
|--------|---------|--------|
| `--parquet-compression CODEC` | `zstd` | `zstd`, `snappy`, `gzip`, `lz4`, `brotli`, `none` |

#### CSV

| Option | Default | Description |
|--------|---------|-------------|
| `--csv-separator SEP` | `,` | Field delimiter |

#### Delta Lake

| Option | Default | Values |
|--------|---------|--------|
| `--delta-mode MODE` | `overwrite` | `overwrite`, `append`, `error` |

#### JSON

| Option | Default | Description |
|--------|---------|-------------|
| `--json-rows` | — | Generate JSON as array of objects |
| `--json-ndjson` | ✓ (default) | Generate NDJSON (one record per line) |

#### Excel

| Option | Default | Description |
|--------|---------|-------------|
| `--excel-single` | ✓ (default) | All tables in a single `.xlsx` |
| `--excel-multi` | — | One `.xlsx` file per table |

#### SQL Server

| Option | Default | Description |
|--------|---------|-------------|
| `--sqlserver-name SERVER` | `localhost` | SQL Server instance (e.g. `localhost\SQLEXPRESS`) |
| `--sqlserver-db DATABASE` | `ContosoRetail` | Target database |
| `--sqlserver-schema SCHEMA` | `dbo` | Target schema |
| `--sqlserver-mode MODE` | `replace` | If table exists: `replace`, `append`, `fail` |

### Examples

```bash
# Quick generation with test config (~5K orders)
cug generate -c configs/quicktest.toml

# Spanish dataset, 500K orders, CSV and Parquet
cug generate -l es -n 500000 -f csv,parquet

# Multi-format: Parquet + DuckDB + Delta Lake
cug generate -n 100000 -f parquet,duckdb,delta

# Direct to local SQL Server Express
cug generate -n 50000 -f sqlserver --sqlserver-name "localhost\SQLEXPRESS" --sqlserver-db MyDatabase

# Force strict mode (validates FK and aborts on errors)
cug generate -c cug/configs/default.toml --strict

# Guaranteed reproducibility with specific seed
cug generate --seed 2024 -o ./output/v1

# Custom Parquet compression
cug generate -f parquet --parquet-compression snappy

# Delta Lake for Microsoft Fabric
cug generate -n 500000 -f delta --delta-mode overwrite
```

---

## `cug info` — View Available Languages

```bash
cug info
```

Displays a table with all supported languages, their code, name, locale tag, and what each one actually localizes (catalogue, calendar, people).

**Supported languages:** `en` (English), `es` (Español), `pt` (Português), `fr` (Français), `de` (Deutsch), `zh` (中文), `ja` (日本語), `ar` (العربية)

---

## `cug categories` — View Product Categories

```bash
cug categories
cug categories --language es
```

| Option | Default | Description |
|--------|---------|-------------|
| `--language CODE` / `-l` | `en` | Language for display names |

Displays all product categories and subcategories with their brands and price ranges.

**Default categories:** `electronics`, `home`, `gaming`, `media`

---

## `cug formats` — View Output Formats

```bash
cug formats
```

Displays a table with all supported formats, their extensions, configurable options, and recommended use cases.

---

## `cug init` — Copy Configuration Template

```bash
cug init [DIR]
```

| Argument | Default | Description |
|----------|---------|-------------|
| `DIR` | `.` (current directory) | Directory where `my_config.toml` will be copied |

Copies `default.toml` as `my_config.toml` to the specified directory for customization.

```bash
# Copy template to current directory
cug init

# Copy template to a specific directory
cug init ./my_project

# Then use the custom config
cug generate -c ./my_project/my_config.toml
```

---

## Configuration Priority

Values are resolved with this priority (highest wins):

1. **CLI Flags** — `--orders 50000` overrides everything
2. **TOML File** — `target_orders = 100000` in config
3. **Internal Defaults** — Hardcoded values in the source code

> [!NOTE]
> The `--strict` / `--no-strict` flags always override the `integrity_strict` value from the TOML file. This allows temporary validation without editing configuration files.

---

← [Back to index](README.md) | [TOML Configuration →](toml-configuration.md)
