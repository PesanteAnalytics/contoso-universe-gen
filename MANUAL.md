# Contoso Universe Generator — Manual de Uso

> **CUG** genera datasets sintéticos de retail 100% relacionales, listos para Power BI, DuckDB, Parquet o CSV. Cada ejecución produce tablas dimensionales y de hechos coherentes, con eventos históricos realistas (COVID, Black Friday, etc.).

---

## Tabla de Contenidos

1. [Instalación](#instalación)
2. [Comandos CLI](#comandos-cli)
3. [Configuración TOML](#configuración-toml)
4. [Integridad de Datos](#integridad-de-datos)
5. [Formatos de Salida](#formatos-de-salida)
6. [Tablas Generadas](#tablas-generadas)
7. [Recetas Rápidas](#recetas-rápidas)

---

## Instalación

```bash
# Desde el directorio raíz del proyecto
pip install -e .

# Verificar instalación
cug --help
```

---

## Comandos CLI

### `cug generate` — Generar dataset

```
cug generate [OPTIONS]
```

| Opción            | Abreviatura | Descripción                                            |
| ----------------- | ----------- | ------------------------------------------------------ |
| `--config PATH`   | `-c`        | Ruta al archivo `.toml`. Sin valor usa `default.toml`. |
| `--output DIR`    | `-o`        | Directorio de salida. Sobreescribe el config.          |
| `--language CODE` | `-l`        | Idioma: `en`, `es`, `pt`, `fr`, `de`, `zh`, `ja`, `ar` |
| `--orders N`      | `-n`        | Número aproximado de órdenes.                          |
| `--formats LIST`  | `-f`        | Formatos separados por coma (ver §5).                  |
| `--seed N`        | —           | Semilla aleatoria para reproducibilidad.               |
| `--strict`        | —           | Aborta si encuentra violaciones FK.                    |
| `--no-strict`     | —           | Reporta violaciones pero continúa generando.           |
| `--verbose`       | `-v`        | Muestra pasos detallados de progreso.                  |

#### Opciones específicas por formato

| Opción                              | Descripción                                                |
| ----------------------------------- | ---------------------------------------------------------- |
| `--parquet-compression CODEC`       | `zstd` (default), `snappy`, `gzip`, `lz4`, `brotli`, `none` |
| `--csv-separator SEP`              | Delimitador CSV (default: `,`)                              |
| `--delta-mode MODE`                | Delta Lake: `overwrite` (default), `append`, `error`        |
| `--json-rows` / `--json-ndjson`    | JSON array vs NDJSON (default: NDJSON)                      |
| `--excel-single` / `--excel-multi` | Un `.xlsx` o uno por tabla (default: single)                |
| `--sqlserver-name SERVER`          | Instancia SQL Server (e.g. `localhost\SQLEXPRESS`)          |
| `--sqlserver-db DATABASE`          | Base de datos destino (default: `ContosoRetail`)            |
| `--sqlserver-schema SCHEMA`        | Esquema destino (default: `dbo`)                            |
| `--sqlserver-mode MODE`            | Si tabla existe: `replace` (default), `append`, `fail`      |

#### Ejemplos

```bash
# Generación rápida con config de prueba
cug generate -c configs/quicktest.toml

# Dataset en español, 500 K órdenes, solo CSV y Parquet
cug generate -c configs/default.toml -l es -n 500000 -f csv,parquet

# Multi-formato: Parquet + DuckDB + Delta Lake
cug generate -n 100000 -f parquet,duckdb,delta

# Directo a SQL Server
cug generate -n 50000 -f sqlserver --sqlserver-name "localhost\SQLEXPRESS" --sqlserver-db MiBase

# Forzar modo strict desde CLI (aunque el config diga lo contrario)
cug generate -c mis_configs/prod.toml --strict

# Generar con reproducibilidad garantizada
cug generate --seed 2024 -o ./output/v1
```

---

### `cug info` — Ver idiomas disponibles

```bash
cug info
```

Lista todos los idiomas soportados con su código, nombre y locale de Faker.

---

### `cug categories` — Ver categorías de productos

```bash
cug categories
cug categories --language es
```

Muestra todas las categorías y subcategorías disponibles con sus rangos de precio.

---

### `cug formats` — Ver formatos disponibles

```bash
cug formats
```

Muestra una tabla con todos los formatos soportados, extensiones, opciones configurables y casos de uso.

---

### `cug init [DIR]` — Copiar plantilla de config

```bash
cug init ./mi_proyecto
```

Copia `default.toml` como `my_config.toml` en el directorio indicado para personalización.

---

## Configuración TOML

La configuración se divide en secciones principales.

### `[general]`

```toml
[general]
start_date  = "2018-01-01"   # Inicio del rango temporal (YYYY-MM-DD)
end_date    = "2026-12-31"   # Fin del rango temporal
language    = "en"           # Idioma: en | es | pt | fr | de | zh | ja | ar
country     = "US"           # País para generación de datos (ISO 3166-1)
seed        = 42             # Semilla maestra (mismo seed = mismo output)
chunk_days  = 30             # Días procesados por chunk (ajusta memoria vs. velocidad)
```

### `[output]`

```toml
[output]
output_path      = "./output"                      # Directorio de salida
formats          = ["parquet"]                     # Formatos a escribir (ver §5)
target_orders    = 100_000                         # Órdenes objetivo (~aproximado)
compress         = true                            # Compresión Gzip para CSV
integrity_check  = false                           # Activar validación FK (ver §4)
integrity_strict = true                            # Abortar en violación (vs. solo reportar)
```

### `[output.format_options]` — Opciones por formato

Cada formato tiene sus opciones específicas. Todas son opcionales — se usan defaults sensatos.

```toml
[output.format_options]
# Parquet
parquet_compression     = "zstd"        # zstd | snappy | gzip | lz4 | brotli | none

# CSV
csv_separator           = ","           # delimitador de campos
csv_include_header      = true
csv_null_value          = ""

# DuckDB
duckdb_db_name          = "contoso.duckdb"

# Delta Lake (ideal para Microsoft Fabric / Databricks)
delta_mode              = "overwrite"   # overwrite | append | error
delta_name              = "contoso"

# JSON / NDJSON
json_row_oriented       = false         # false = NDJSON, true = JSON array
json_pretty             = false

# Excel
excel_single_workbook   = true          # true = todo en un .xlsx, false = uno por tabla
excel_workbook_name     = "contoso.xlsx"

# SQL Server (ver §6 para detalles)
# sqlserver_server      = "localhost\\SQLEXPRESS"
# sqlserver_database    = "ContosoRetail"
# sqlserver_schema      = "dbo"
# sqlserver_if_exists   = "replace"     # replace | append | fail
# sqlserver_batch_size  = 5000
```

### `[customers]`

```toml
[customers]
pool_size         = 50_000   # Total de clientes únicos en el universo
active_pct        = 0.30     # Fracción de clientes que realizan al menos una compra
online_pct_start  = 0.05     # % de órdenes online al inicio del período
online_pct_end    = 0.55     # % de órdenes online al final del período (crecimiento lineal)
```

### `[categories]`

```toml
[categories]
enabled      = ["electronics", "home", "gaming", "media"]
custom_paths = []   # Rutas a plugins de categorías personalizadas
```

### `[[events.annual]]` — Eventos recurrentes anuales

```toml
[[events.annual]]
name   = "Black Friday"
month  = 11
day    = 25
factor = 4.5          # Multiplicador de ventas ese día (4.5x la demanda base)
```

### `[[events.one_time]]` — Eventos históricos únicos

```toml
[[events.one_time]]
name       = "COVID eCommerce Surge"
date_start = "2020-05-01"
date_end   = "2021-03-31"
factor     = 1.85          # Ventas 85% por encima de la base durante ese período
```

### `[weekday_factors]`

```toml
[weekday_factors]
# Índices: 0=Lun, 1=Mar, 2=Mié, 3=Jue, 4=Vie, 5=Sáb, 6=Dom
factors = [0.75, 0.85, 0.95, 1.05, 1.20, 1.60, 0.30]
```

---

## Integridad de Datos

CUG incluye un motor de validación referencial que verifica las relaciones FK **en memoria, antes de escribir cualquier archivo**. Esto garantiza que los datasets generados sean 100% válidos para herramientas de BI.

### Relaciones verificadas

| FK en `FactSales` | Dimensión     | Clave         |
| ----------------- | ------------- | ------------- |
| `OrderDateKey`    | `DimDate`     | `DateKey`     |
| `DeliveryDateKey` | `DimDate`     | `DateKey`     |
| `CustomerKey`     | `DimCustomer` | `CustomerKey` |
| `ProductKey`      | `DimProduct`  | `ProductKey`  |
| `StoreKey`        | `DimStore`    | `StoreKey`    |
| `CurrencyKey`     | `DimCurrency` | `CurrencyKey` |

### Modos de operación

| Modo            | Config                                               | CLI           | Comportamiento                                 |
| --------------- | ---------------------------------------------------- | ------------- | ---------------------------------------------- |
| **Desactivado** | `integrity_check = false`                            | —             | No valida. Máxima velocidad.                   |
| **Report-only** | `integrity_check = true`, `integrity_strict = false` | `--no-strict` | Imprime el reporte y continúa.                 |
| **Strict**      | `integrity_check = true`, `integrity_strict = true`  | `--strict`    | Aborta con error detallado si hay violaciones. |

> [!NOTE]
> El flag CLI (`--strict` / `--no-strict`) siempre sobreescribe el valor del config,
> lo que permite validar temporalmente sin editar archivos.

---

## Formatos de Salida

CUG soporta 7 formatos de salida. Se pueden combinar libremente: `-f parquet,csv,sqlserver`.

| Formato     | Extensión / Destino | Descripción                                              | Caso de uso                          |
| ----------- | ------------------- | -------------------------------------------------------- | ------------------------------------ |
| `parquet`   | `.parquet`          | Columnar comprimido, tipos nativos                       | Power BI, Spark, Fabric Direct Lake  |
| `csv`       | `.csv` / `.csv.gz`  | Texto plano, se comprime si `compress = true`            | Compatibilidad universal             |
| `duckdb`    | `.duckdb`           | Base de datos analítica embebida                         | Consultas SQL inmediatas             |
| `delta`     | Delta Lake          | Tablas delta con versionado                              | Fabric, Databricks, Lakehouse       |
| `json`      | `.json` / `.ndjson` | JSON array o NDJSON (un registro por línea)              | APIs, integración web, debugging     |
| `excel`     | `.xlsx`             | Workbook Excel con una hoja por tabla (o uno por tabla)  | Compartir con usuarios no-técnicos   |
| `sqlserver` | SQL Server          | Tablas en base de datos SQL Server vía ODBC              | Power BI DirectQuery, dashboards     |

### Consultar el DuckDB generado

```sql
-- En DuckDB CLI o Python
SELECT COUNT(*) FROM read_parquet('./output/FactSales.parquet');

-- Con el archivo .duckdb directamente
ATTACH './output/contoso.duckdb' AS db;
SELECT * FROM db.FactSales LIMIT 10;
```

---

## SQL Server

CUG puede escribir directamente a una base de datos SQL Server. El writer crea automáticamente la base de datos (si no existe) y las tablas con tipos correctos.

### Prerequisitos

1. **SQL Server** instalado y accesible (Express, Developer, Standard, o Azure SQL)
2. **ODBC Driver** — se auto-detecta. Drivers soportados (en orden de preferencia):
   - ODBC Driver 18 for SQL Server
   - ODBC Driver 17 for SQL Server
   - SQL Server Native Client 11.0

> [!NOTE]
> Para verificar qué drivers tienes instalados:
> ```python
> import pyodbc; print(pyodbc.drivers())
> ```

### Autenticación

| Método | Config | Descripción |
| ------ | ------ | ----------- |
| **Windows Auth** (default) | `sqlserver_trusted = true` | Usa las credenciales del usuario actual. Ideal para desarrollo local. |
| **SQL Auth** | `sqlserver_trusted = false` + `username` + `password` | Autenticación por usuario SQL. Para servidores remotos o Azure. |
| **Connection string** | `sqlserver_connection_string = "..."` | ODBC string completa. Sobreescribe todas las demás opciones. |

### Ejemplo rápido

```bash
# Windows Auth contra SQL Server Express local
cug generate -n 100000 -f sqlserver \
  --sqlserver-name "localhost\SQLEXPRESS" \
  --sqlserver-db ContosoRetail

# Múltiples formatos simultáneos
cug generate -n 50000 -f parquet,sqlserver \
  --sqlserver-name "localhost\SQLEXPRESS" \
  --sqlserver-db ContosoDemo
```

### Mapeo de tipos Polars → SQL Server

| Polars          | SQL Server      | Notas                                  |
| --------------- | --------------- | -------------------------------------- |
| `Int8`          | `TINYINT`       |                                        |
| `Int16`         | `SMALLINT`      |                                        |
| `Int32`         | `INT`           |                                        |
| `Int64`         | `BIGINT`        |                                        |
| `UInt8/16`      | `SMALLINT/INT`  | SQL Server no tiene unsigned           |
| `Float32/64`    | `REAL/FLOAT`    |                                        |
| `String`        | `NVARCHAR(400)` |                                        |
| `Boolean`       | `BIT`           | Se convierte a `1`/`0` internamente   |
| `Date`          | `DATE`          |                                        |
| `Datetime`      | `DATETIME2`     |                                        |
| `Duration`      | `BIGINT`        | Almacenado como microsegundos          |
| `Null`          | `NVARCHAR(1)`   | Columnas donde todos los valores son `None` |

### Troubleshooting

#### Error: `DataError` con `fast_executemany`

El writer usa `pyodbc.fast_executemany` para inserciones de alta velocidad. Si falla en alguna tabla, automáticamente cae a inserción fila-por-fila con un mensaje de advertencia.

#### Caracteres corruptos (CJK) en columnas de texto

**No** configurar `conn.setencoding(encoding="utf-8")` manualmente. SQL Server usa UTF-16LE internamente y `pyodbc` en Windows lo maneja correctamente por defecto. Forzar UTF-8 corrompe los datos NVARCHAR.

#### Error de conexión con ODBC Driver 18

El Driver 18 requiere certificado SSL válido. Para desarrollo local, el writer agrega automáticamente `TrustServerCertificate=yes`.

---

## Tablas Generadas

| Tabla               | Descripción                                | Columnas clave                                                                    |
| ------------------- | ------------------------------------------ | --------------------------------------------------------------------------------- |
| `DimDate`           | Calendario completo del período            | `DateKey`, `Year`, `Month`, `Quarter`, `DayName`, `IsWeekend`, `IsHoliday`        |
| `DimCustomer`       | Pool de clientes sintéticos                | `CustomerKey`, `CustomerName`, `City`, `Country`, `EmailAddress`                  |
| `DimProduct`        | Catálogo de productos por categoría        | `ProductKey`, `ProductName`, `Category`, `Subcategory`, `UnitPrice`               |
| `DimStore`          | Tiendas físicas y canal online             | `StoreKey`, `StoreName`, `StoreType`, `Country`                                   |
| `DimCurrency`       | Monedas soportadas                         | `CurrencyKey`, `CurrencyCode`, `CurrencyName`                                    |
| `DimCurrencyExchange` | Tasas de cambio diarias                   | `CurrencyCode`, `Date`, `ExchangeRate`                                            |
| `FactSales`         | Tabla de hechos de ventas                  | `OrderKey`, `CustomerKey`, `ProductKey`, `StoreKey`, `Quantity`, `UnitPrice`       |

---

## Recetas Rápidas

### Dataset mínimo para pruebas (5K órdenes, todos los formatos)

```bash
cug generate -c configs/quicktest.toml
```

### Dataset de producción en español (1M órdenes)

```bash
cug generate -c configs/retail_1M_es.toml --strict
```

### Solo CSV, sin validación, máxima velocidad

```bash
cug generate -n 200000 -f csv
```

### Multi-formato para workshop (Parquet + DuckDB + CSV)

```bash
cug generate -n 100000 -f parquet,duckdb,csv -l es
```

### SQL Server Express local con Windows Auth

```bash
cug generate -n 50000 -f sqlserver \
  --sqlserver-name "localhost\SQLEXPRESS" \
  --sqlserver-db ContosoDemo
```

### Dataset completo para Power BI (Parquet + SQL Server)

```bash
cug generate -n 1000000 -f parquet,sqlserver \
  --sqlserver-name "localhost\SQLEXPRESS" \
  --sqlserver-db ContosoRetail
```

### Delta Lake para Microsoft Fabric

```bash
cug generate -n 500000 -f delta --delta-mode overwrite
```

### Reproducir exactamente el mismo dataset

```bash
cug generate --seed 42 -o ./output/reproducible
```

---

_Generado con CUG v0.2.0 — [github.com/Support1-PAL/contoso-universe-gen](https://github.com/Support1-PAL/contoso-universe-gen)_
