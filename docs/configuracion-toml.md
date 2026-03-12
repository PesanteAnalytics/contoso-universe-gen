# Configuración TOML

> Estructura completa del archivo de configuración `.toml` de CUG con explicaciones detalladas de cada sección y variable.

---

## Ubicación

Los archivos de configuración se encuentran en `configs/`:

| Archivo | Descripción |
|---------|-------------|
| `configs/default.toml` | Configuración estándar, 100K órdenes |
| `configs/quicktest.toml` | Prueba rápida, ~5K órdenes |
| `configs/retail_1M_en.toml` | 1M órdenes en inglés |
| `configs/retail_1M_es.toml` | 1M órdenes en español |
| `configs/retail_10M_es.toml` | 10M órdenes en español |

Para crear tu propia configuración:

```bash
cug init ./mi_proyecto
# Genera: ./mi_proyecto/my_config.toml
```

---

## Secciones del Archivo TOML

### `[general]` — Configuración General

```toml
[general]
start_date  = "2018-01-01"   # Inicio del rango temporal (YYYY-MM-DD)
end_date    = "2026-03-05"   # Fin del rango temporal
language    = "en"           # Idioma: en | es | pt | fr | de | zh | ja | ar
country     = "US"           # País para generación de datos (ISO 3166-1)
seed        = 42             # Semilla maestra (mismo seed = mismo output)
chunk_days  = 30             # Días procesados por chunk (ajusta memoria vs. velocidad)
```

| Variable | Default | Opciones | Descripción |
|----------|---------|----------|-------------|
| `start_date` | `2018-01-01` | Cualquier fecha `YYYY-MM-DD` | Inicio del rango temporal de ventas |
| `end_date` | `2026-03-05` | Cualquier fecha `YYYY-MM-DD` | Fin del rango temporal de ventas |
| `language` | `en` | `en`, `es`, `pt`, `fr`, `de`, `zh`, `ja`, `ar` | Idioma para nombres de clientes, productos y categorías |
| `country` | `US` | Código ISO 3166-1 | País para días festivos y localización de datos |
| `seed` | `42` | Cualquier entero | Semilla aleatoria maestra. Mismo seed = mismo dataset |
| `chunk_days` | `30` | > 0 | Días por chunk de procesamiento. Valores más bajos = menos memoria, más lento |

> [!TIP]
> Para datasets muy grandes (>5M órdenes), reduce `chunk_days` a `15` para evitar problemas de memoria.

---

### `[output]` — Configuración de Salida

```toml
[output]
output_path      = "./output"       # Directorio de salida
formats          = ["parquet"]      # Formatos a escribir
target_orders    = 100_000          # Órdenes objetivo (~aproximado)
compress         = true             # Compresión Gzip para CSV
integrity_check  = false            # Activar validación FK
integrity_strict = true             # Abortar en violación (vs. solo reportar)
```

| Variable | Default | Opciones | Descripción |
|----------|---------|----------|-------------|
| `output_path` | `./output` | Cualquier directorio | Directorio donde se guardan los archivos generados |
| `formats` | `["parquet"]` | Lista combinable | Formatos de salida (ver [Formatos](formatos-salida.md)) |
| `target_orders` | `100,000` | > 0 | Número aproximado de órdenes. El resultado real varía ±5% |
| `compress` | `true` | `true` / `false` | Aplica compresión Gzip a archivos CSV |
| `integrity_check` | `false` | `true` / `false` | Activa la validación de integridad referencial (FK) |
| `integrity_strict` | `true` | `true` / `false` | Si es `true`, aborta con error si hay violaciones FK |

**Formatos disponibles:** `parquet`, `csv`, `duckdb`, `delta`, `json`, `excel`, `sqlserver`

```toml
# Ejemplo: múltiples formatos simultáneos
formats = ["parquet", "csv", "duckdb"]
```

### Modos de Integridad

| Modo | Config | CLI Flag | Comportamiento |
|------|--------|----------|----------------|
| **Desactivado** | `integrity_check = false` | — | No valida. Máxima velocidad |
| **Report-only** | `integrity_check = true`, `integrity_strict = false` | `--no-strict` | Imprime reporte y continúa |
| **Strict** | `integrity_check = true`, `integrity_strict = true` | `--strict` | Aborta con error detallado |

> [!NOTE]
> Los flags CLI (`--strict` / `--no-strict`) siempre sobreescriben el valor del config.

---

### `[output.format_options]` — Opciones por Formato

Cada formato tiene opciones específicas. Todas son opcionales — se usan defaults sensatos.

```toml
[output.format_options]
```

#### Parquet

```toml
parquet_compression     = "zstd"        # zstd | snappy | gzip | lz4 | brotli | none
# parquet_row_group_size = 100000       # filas por row group (default: auto)
```

| Variable | Default | Opciones | Descripción |
|----------|---------|----------|-------------|
| `parquet_compression` | `zstd` | `zstd`, `snappy`, `gzip`, `lz4`, `brotli`, `none` | Algoritmo de compresión |
| `parquet_row_group_size` | `None` (auto) | Entero positivo | Filas por row group |

#### CSV

```toml
csv_separator           = ","           # delimitador de campos
csv_include_header      = true          # incluir fila de encabezados
csv_null_value          = ""            # representación de valores nulos
# csv_date_format       = "%Y-%m-%d"   # formato de fechas (default: ISO 8601)
```

| Variable | Default | Opciones | Descripción |
|----------|---------|----------|-------------|
| `csv_separator` | `,` | Cualquier carácter | Delimitador de campos |
| `csv_include_header` | `true` | `true` / `false` | Incluir fila de encabezados |
| `csv_null_value` | `""` | Cualquier string | Representación de valores NULL |
| `csv_date_format` | `None` (ISO 8601) | Patrón de fecha | Formato de fechas en el CSV |

#### DuckDB

```toml
duckdb_db_name          = "contoso.duckdb"
```

| Variable | Default | Descripción |
|----------|---------|-------------|
| `duckdb_db_name` | `contoso.duckdb` | Nombre del archivo de base de datos |

#### Delta Lake

```toml
delta_mode              = "overwrite"   # overwrite | append | error
# delta_partition_by    = ["Year"]      # particionar FactSales por columna(s)
delta_name              = "contoso"     # nombre en metadata
```

| Variable | Default | Opciones | Descripción |
|----------|---------|----------|-------------|
| `delta_mode` | `overwrite` | `overwrite`, `append`, `error` | Modo de escritura |
| `delta_partition_by` | `None` | Lista de columnas | Columnas para particionar (e.g. `["Year"]`) |
| `delta_name` | `contoso` | Cualquier string | Nombre en metadata de Delta |

#### JSON / NDJSON

```toml
json_row_oriented       = false         # false = NDJSON, true = JSON array
json_pretty             = false         # pretty-print (solo con row_oriented = true)
```

| Variable | Default | Opciones | Descripción |
|----------|---------|----------|-------------|
| `json_row_oriented` | `false` | `true` / `false` | `false` = NDJSON (un registro por línea), `true` = JSON array |
| `json_pretty` | `false` | `true` / `false` | Formato legible. Solo aplica con `row_oriented = true` |

#### Excel

```toml
excel_single_workbook   = true          # true = todo en un .xlsx, false = uno por tabla
excel_workbook_name     = "contoso.xlsx"
```

| Variable | Default | Opciones | Descripción |
|----------|---------|----------|-------------|
| `excel_single_workbook` | `true` | `true` / `false` | `true` = todas las tablas en un solo workbook |
| `excel_workbook_name` | `contoso.xlsx` | Nombre de archivo | Nombre del workbook Excel |

#### SQL Server

```toml
# sqlserver_server            = "localhost\\SQLEXPRESS"
# sqlserver_database          = "ContosoRetail"
# sqlserver_schema            = "dbo"
# sqlserver_driver            = "ODBC Driver 17 for SQL Server"  # auto-detectado
# sqlserver_trusted           = true           # Windows Auth
# sqlserver_username          = ""             # Solo SQL Auth
# sqlserver_password          = ""             # Solo SQL Auth
# sqlserver_if_exists         = "replace"      # replace | append | fail
# sqlserver_batch_size        = 5000           # filas por INSERT batch
# sqlserver_connection_string = ""             # ODBC string completa (override)
```

Para detalles completos de SQL Server, ver [sqlserver.md](sqlserver.md).

---

### `[customers]` — Configuración de Clientes

```toml
[customers]
pool_size         = 50_000   # Total de clientes únicos en el universo
active_pct        = 0.30     # Fracción de clientes que compran al menos 1 vez
online_pct_start  = 0.05     # % de órdenes online al inicio del período
online_pct_end    = 0.55     # % de órdenes online al final del período
```

| Variable | Default | Rango | Descripción |
|----------|---------|-------|-------------|
| `pool_size` | `50,000` | > 0 | Total de clientes únicos generados |
| `active_pct` | `0.30` | 0.01 – 1.0 | % de clientes que realizan al menos una compra |
| `online_pct_start` | `0.05` | 0.0 – 1.0 | % de ventas online al inicio del período |
| `online_pct_end` | `0.55` | 0.0 – 1.0 | % de ventas online al final (crecimiento lineal) |

> [!TIP]
> El crecimiento lineal de `online_pct_start` a `online_pct_end` simula la digitalización progresiva del comercio retail.

---

### `[categories]` — Categorías de Productos

```toml
[categories]
enabled      = ["electronics", "home", "gaming", "media"]
custom_paths = []
```

| Variable | Default | Descripción |
|----------|---------|-------------|
| `enabled` | `["electronics", "home", "gaming", "media"]` | Categorías activas para la generación |
| `custom_paths` | `[]` | Rutas a archivos YAML con categorías personalizadas (plugins) |

---

### `[[events.annual]]` — Eventos Recurrentes Anuales

Eventos que ocurren cada año y afectan la demanda.

```toml
[[events.annual]]
name   = "Black Friday"
month  = 11
day    = 25
factor = 2.8    # Multiplicador de ventas ese día (2.8x la demanda base)
```

| Variable | Descripción |
|----------|-------------|
| `name` | Nombre del evento |
| `month` | Mes (1-12) |
| `day` | Día del mes |
| `factor` | Multiplicador de demanda. 1.0 = sin cambio, 2.0 = doble, 0.5 = mitad |

**Eventos incluidos por default:**

| Evento | Mes/Día | Factor | Descripción |
|--------|---------|--------|-------------|
| Black Friday | 11/25 | 2.8x | Pico de ventas retail |
| Cyber Monday | 11/28 | 2.5x | Pico online post Black Friday |
| Christmas | 12/25 | 2.0x | Temporada navideña |
| Back to School | 8/15 | 1.8x | Regreso a clases |
| Prime Day | 7/12 | 2.5x | Evento de ventas online |

---

### `[[events.one_time]]` — Eventos Históricos Únicos

Eventos que ocurren una sola vez en un rango de fechas.

```toml
[[events.one_time]]
name       = "COVID Lockdown Drop"
date_start = "2020-03-15"
date_end   = "2020-04-30"
factor     = 0.45    # Ventas al 45% de la base (caída del 55%)
```

| Variable | Descripción |
|----------|-------------|
| `name` | Nombre del evento |
| `date_start` | Fecha de inicio (`YYYY-MM-DD`) |
| `date_end` | Fecha de fin (`YYYY-MM-DD`) |
| `factor` | Multiplicador de demanda durante el período |

**Eventos one-time incluidos por default:**

| Evento | Período | Factor | Descripción |
|--------|---------|--------|-------------|
| COVID Lockdown Drop | Mar–Abr 2020 | 0.45x | Caída por confinamiento |
| COVID eCommerce Surge | May 2020–Mar 2021 | 1.18x | Boom del comercio online |
| Post-COVID Recovery | Abr 2021–Jun 2022 | 1.06x | Recuperación gradual |
| Inflation Pressure 2022 | Ene–Dic 2022 | 0.92x | Presión inflacionaria |
| AI & Electronics Boom | Jun 2023–Dic 2024 | 1.09x | Boom de IA y renovación tech |

---

### `[weekday_factors]` — Factores por Día de la Semana

```toml
[weekday_factors]
# Índices: 0=Lun, 1=Mar, 2=Mié, 3=Jue, 4=Vie, 5=Sáb, 6=Dom
factors = [0.75, 0.85, 0.95, 1.05, 1.20, 1.60, 0.30]
```

| Día | Factor Default | Descripción |
|-----|---------------|-------------|
| Lunes | 0.75 | Día más bajo (excepto domingo) |
| Martes | 0.85 | Ligeramente por debajo del promedio |
| Miércoles | 0.95 | Cercano al promedio |
| Jueves | 1.05 | Ligeramente por encima |
| Viernes | 1.20 | Aumento significativo |
| **Sábado** | **1.60** | **Día pico de ventas** |
| Domingo | 0.30 | Día más bajo de la semana |

---

← [Referencia CLI](cli-referencia.md) | [Formatos de Salida →](formatos-salida.md)
