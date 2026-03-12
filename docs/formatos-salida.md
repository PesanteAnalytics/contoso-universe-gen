# Formatos de Salida

> Los 7 formatos soportados por CUG, con opciones específicas de cada uno y recomendaciones de uso.

---

## Resumen de Formatos

| Formato | Extensión / Destino | Descripción | Caso de Uso Principal |
|---------|-------------------|-------------|----------------------|
| **parquet** ★ | `.parquet` | Columnar comprimido con tipos nativos | Power BI, Spark, Fabric Direct Lake |
| **csv** | `.csv` / `.csv.gz` | Texto plano, opcionalmente comprimido | Compatibilidad universal |
| **duckdb** | `.duckdb` | Base de datos analítica embebida | Consultas SQL inmediatas |
| **delta** | Delta Lake | Tablas delta con versionado | Fabric, Databricks, Lakehouse |
| **json** | `.json` / `.ndjson` | JSON array o NDJSON | APIs, integración web, debugging |
| **excel** | `.xlsx` | Workbook Excel | Compartir con usuarios no-técnicos |
| **sqlserver** | SQL Server DB | Tablas en base de datos SQL Server | Power BI DirectQuery, dashboards |

> ★ = formato por defecto cuando no se especifica ninguno.

---

## Combinar Formatos

CUG puede generar múltiples formatos en una sola ejecución:

```bash
# Un solo formato (default)
cug generate -f parquet

# Dos formatos
cug generate -f parquet,csv

# Tres formatos
cug generate -f parquet,duckdb,delta

# Todos los que necesites
cug generate -f parquet,csv,duckdb,sqlserver
```

---

## Parquet

**El formato recomendado para la mayoría de casos analíticos.**

Genera un archivo `.parquet` por tabla (e.g. `FactSales.parquet`, `DimCustomer.parquet`).

### Opciones

| Opción TOML | CLI Flag | Default | Valores |
|-------------|----------|---------|---------|
| `parquet_compression` | `--parquet-compression` | `zstd` | `zstd`, `snappy`, `gzip`, `lz4`, `brotli`, `none` |
| `parquet_row_group_size` | — | Auto | Entero positivo |

### Ejemplo

```bash
# Parquet con compresión snappy (más rápido, menos compresión)
cug generate -n 100000 -f parquet --parquet-compression snappy

# Parquet default (zstd, mejor ratio compresión/velocidad)
cug generate -n 500000 -f parquet
```

### Cuándo usar Parquet

- **Power BI Import mode** — Carga rápida de datos
- **Spark / Databricks** — Lectura eficiente columnar
- **Microsoft Fabric Direct Lake** — Formato nativo
- **Archivado** — Excelente compresión

---

## CSV

Genera archivos `.csv` (o `.csv.gz` si `compress = true`) — uno por tabla.

### Opciones

| Opción TOML | CLI Flag | Default | Descripción |
|-------------|----------|---------|-------------|
| `csv_separator` | `--csv-separator` | `,` | Delimitador de campos |
| `csv_include_header` | — | `true` | Incluir fila de encabezados |
| `csv_null_value` | — | `""` | Representación de valores NULL |
| `csv_date_format` | — | ISO 8601 | Formato de fechas |

### Ejemplo

```bash
# CSV con punto y coma (para locales que usan coma decimal)
cug generate -n 50000 -f csv --csv-separator ";"

# CSV estándar
cug generate -n 100000 -f csv
```

### Cuándo usar CSV

- **Importar a Excel** manualmente
- **Compatibilidad universal** con cualquier herramienta
- **ETL pipelines** que esperan texto plano
- **Intercambio de datos** entre sistemas heterogéneos

---

## DuckDB

Genera una base de datos DuckDB embebida (`.duckdb`) con todas las tablas cargadas.

### Opciones

| Opción TOML | CLI Flag | Default | Descripción |
|-------------|----------|---------|-------------|
| `duckdb_db_name` | — | `contoso.duckdb` | Nombre del archivo de base de datos |

### Ejemplo

```bash
cug generate -n 100000 -f duckdb
```

### Consultar el DuckDB generado

```sql
-- Con DuckDB CLI
.open ./output/contoso.duckdb
SELECT COUNT(*) FROM FactSales;
SELECT Year, SUM(Quantity) FROM FactSales f JOIN DimDate d ON f.OrderDateKey = d.DateKey GROUP BY Year;

-- Con Python
import duckdb
conn = duckdb.connect("./output/contoso.duckdb")
df = conn.sql("SELECT * FROM FactSales LIMIT 10").pl()
```

### Cuándo usar DuckDB

- **Consultas SQL inmediatas** sin necesidad de un servidor
- **Notebooks de Python** — integración directa con Polars/Pandas
- **Prototipado rápido** — base de datos analítica sin infraestructura
- **DBeaver / DataGrip** — exploración con herramientas GUI

---

## Delta Lake

Genera tablas en formato Delta Lake, ideal para lakehouses.

### Opciones

| Opción TOML | CLI Flag | Default | Valores |
|-------------|----------|---------|---------|
| `delta_mode` | `--delta-mode` | `overwrite` | `overwrite`, `append`, `error` |
| `delta_partition_by` | — | `None` | Lista de columnas (e.g. `["Year"]`) |
| `delta_name` | — | `contoso` | Nombre en metadata |

### Ejemplo

```bash
# Delta Lake con overwrite
cug generate -n 500000 -f delta --delta-mode overwrite

# Delta Lake con particionamiento por año
# (configurar en TOML: delta_partition_by = ["Year"])
cug generate -n 1000000 -f delta
```

### Cuándo usar Delta

- **Microsoft Fabric** — Lakehouses y Warehouses
- **Databricks** — Formato nativo
- **Apache Spark** — Versionado y ACID transactions
- **Time travel** — Historial de versiones

---

## JSON / NDJSON

Genera archivos JSON — ya sea como JSON array completo o como NDJSON (un registro por línea).

### Opciones

| Opción TOML | CLI Flag | Default | Descripción |
|-------------|----------|---------|-------------|
| `json_row_oriented` | `--json-rows` / `--json-ndjson` | `false` (NDJSON) | `true` = JSON array, `false` = NDJSON |
| `json_pretty` | — | `false` | Pretty-print (solo con `row_oriented = true`) |

### Ejemplo

```bash
# NDJSON (default, un registro por línea)
cug generate -n 50000 -f json

# JSON array
cug generate -n 10000 -f json --json-rows
```

### Cuándo usar JSON

- **APIs REST** — Payload de prueba
- **Streaming** — NDJSON para ingesta línea por línea
- **Debugging** — Inspección humana de datos
- **Web apps** — Datos de prueba para frontends

---

## Excel

Genera archivos Excel `.xlsx` — todas las tablas en un solo workbook o uno por tabla.

### Opciones

| Opción TOML | CLI Flag | Default | Descripción |
|-------------|----------|---------|-------------|
| `excel_single_workbook` | `--excel-single` / `--excel-multi` | `true` | `true` = un workbook, `false` = uno por tabla |
| `excel_workbook_name` | — | `contoso.xlsx` | Nombre del archivo Excel |

### Ejemplo

```bash
# Un solo workbook con todas las tablas como hojas
cug generate -n 20000 -f excel

# Un archivo .xlsx por tabla
cug generate -n 20000 -f excel --excel-multi
```

> [!WARNING]
> Excel tiene un límite de ~1 millón de filas por hoja. Para datasets grandes, usa otro formato.

### Cuándo usar Excel

- **Compartir con stakeholders** no-técnicos
- **Exploración rápida** de datos
- **Presentaciones** y reports ad-hoc

---

## SQL Server

Escribe directamente a una base de datos SQL Server vía ODBC.

Para documentación detallada, ver [sqlserver.md](sqlserver.md).

### Opciones principales

| Opción TOML | CLI Flag | Default | Descripción |
|-------------|----------|---------|-------------|
| `sqlserver_server` | `--sqlserver-name` | `localhost` | Instancia SQL Server |
| `sqlserver_database` | `--sqlserver-db` | `ContosoRetail` | Base de datos destino |
| `sqlserver_schema` | `--sqlserver-schema` | `dbo` | Esquema destino |
| `sqlserver_if_exists` | `--sqlserver-mode` | `replace` | `replace`, `append`, `fail` |
| `sqlserver_batch_size` | — | `5,000` | Filas por INSERT batch |
| `sqlserver_trusted` | — | `true` | Windows Authentication |

### Ejemplo

```bash
# SQL Server Express local (Windows Auth)
cug generate -n 100000 -f sqlserver \
  --sqlserver-name "localhost\SQLEXPRESS" \
  --sqlserver-db ContosoRetail

# Parquet + SQL Server simultáneos
cug generate -n 50000 -f parquet,sqlserver \
  --sqlserver-name "localhost\SQLEXPRESS" \
  --sqlserver-db ContosoDemo
```

### Cuándo usar SQL Server

- **Power BI DirectQuery** — Consultas en tiempo real
- **Dashboards empresariales** — Datos centralizados
- **SSAS Tabular** — Modelo semántico
- **Integración con aplicaciones** que usan SQL Server

---

← [Configuración TOML](configuracion-toml.md) | [Esquema de Datos →](esquema-datos.md)
