# Referencia CLI

> Todos los comandos de la interfaz de línea de comandos de CUG.

---

## Invocación

```bash
# Si instalaste con pip install -e .
cug <comando> [opciones]

# Si usas el entorno virtual directamente
.venv\Scripts\python.exe -m cug <comando> [opciones]
```

---

## Comandos Disponibles

| Comando | Descripción |
|---------|-------------|
| `cug generate` | Genera un dataset completo |
| `cug info` | Muestra idiomas disponibles |
| `cug categories` | Muestra categorías de productos |
| `cug formats` | Muestra formatos de salida disponibles |
| `cug init [DIR]` | Copia la plantilla de configuración a un directorio |

---

## `cug generate` — Generar Dataset

El comando principal. Genera un dataset completo de retail con tablas dimensionales y de hechos.

```bash
cug generate [OPTIONS]
```

### Opciones Generales

| Opción | Abreviatura | Default | Descripción |
|--------|-------------|---------|-------------|
| `--config PATH` | `-c` | `default.toml` (built-in) | Ruta al archivo `.toml` de configuración |
| `--output DIR` | `-o` | `./output` | Directorio de salida. Sobreescribe el config |
| `--language CODE` | `-l` | `en` | Idioma: `en`, `es`, `pt`, `fr`, `de`, `zh`, `ja`, `ar` |
| `--orders N` | `-n` | `100,000` | Número aproximado de órdenes a generar |
| `--formats LIST` | `-f` | `parquet` | Formatos separados por coma (ver [Formatos](formatos-salida.md)) |
| `--seed N` | — | `42` | Semilla aleatoria para reproducibilidad |
| `--strict` | — | — | Aborta si encuentra violaciones de FK |
| `--no-strict` | — | — | Reporta violaciones pero continúa generando |
| `--verbose` | `-v` | `false` | Muestra pasos detallados de progreso |

### Opciones Específicas por Formato

#### Parquet

| Opción | Default | Valores |
|--------|---------|---------|
| `--parquet-compression CODEC` | `zstd` | `zstd`, `snappy`, `gzip`, `lz4`, `brotli`, `none` |

#### CSV

| Opción | Default | Descripción |
|--------|---------|-------------|
| `--csv-separator SEP` | `,` | Delimitador de campos |

#### Delta Lake

| Opción | Default | Valores |
|--------|---------|---------|
| `--delta-mode MODE` | `overwrite` | `overwrite`, `append`, `error` |

#### JSON

| Opción | Default | Descripción |
|--------|---------|-------------|
| `--json-rows` | — | Genera JSON como array de objetos |
| `--json-ndjson` | ✓ (default) | Genera NDJSON (un registro por línea) |

#### Excel

| Opción | Default | Descripción |
|--------|---------|-------------|
| `--excel-single` | ✓ (default) | Todas las tablas en un solo `.xlsx` |
| `--excel-multi` | — | Un archivo `.xlsx` por tabla |

#### SQL Server

| Opción | Default | Descripción |
|--------|---------|-------------|
| `--sqlserver-name SERVER` | `localhost` | Instancia SQL Server (e.g. `localhost\SQLEXPRESS`) |
| `--sqlserver-db DATABASE` | `ContosoRetail` | Base de datos destino |
| `--sqlserver-schema SCHEMA` | `dbo` | Esquema destino |
| `--sqlserver-mode MODE` | `replace` | Si tabla existe: `replace`, `append`, `fail` |

### Ejemplos

```bash
# Generación rápida con config de prueba (~5K órdenes)
cug generate -c configs/quicktest.toml

# Dataset en español, 500K órdenes, CSV y Parquet
cug generate -l es -n 500000 -f csv,parquet

# Multi-formato: Parquet + DuckDB + Delta Lake
cug generate -n 100000 -f parquet,duckdb,delta

# Directo a SQL Server Express local
cug generate -n 50000 -f sqlserver --sqlserver-name "localhost\SQLEXPRESS" --sqlserver-db MiBase

# Forzar modo strict (valida FK y aborta si hay errores)
cug generate -c configs/default.toml --strict

# Reproducibilidad garantizada con semilla específica
cug generate --seed 2024 -o ./output/v1

# Compresión Parquet personalizada
cug generate -f parquet --parquet-compression snappy

# Delta Lake para Microsoft Fabric
cug generate -n 500000 -f delta --delta-mode overwrite
```

---

## `cug info` — Ver Idiomas Disponibles

```bash
cug info
```

Muestra una tabla con todos los idiomas soportados, su código, nombre y locale de Faker asociado.

**Idiomas soportados:** `en` (English), `es` (Español), `pt` (Português), `fr` (Français), `de` (Deutsch), `zh` (中文), `ja` (日本語), `ar` (العربية)

---

## `cug categories` — Ver Categorías de Productos

```bash
cug categories
cug categories --language es
```

| Opción | Default | Descripción |
|--------|---------|-------------|
| `--language CODE` / `-l` | `en` | Idioma para los nombres de display |

Muestra todas las categorías y subcategorías de productos con sus marcas y rangos de precio.

**Categorías por default:** `electronics`, `home`, `gaming`, `media`

---

## `cug formats` — Ver Formatos de Salida

```bash
cug formats
```

Muestra una tabla con todos los formatos soportados, sus extensiones, opciones configurables y casos de uso recomendados.

---

## `cug init` — Copiar Plantilla de Configuración

```bash
cug init [DIR]
```

| Argumento | Default | Descripción |
|-----------|---------|-------------|
| `DIR` | `.` (directorio actual) | Directorio donde se copiará `my_config.toml` |

Copia `default.toml` como `my_config.toml` en el directorio indicado para que puedas personalizarlo.

```bash
# Copiar plantilla al directorio actual
cug init

# Copiar plantilla a un directorio específico
cug init ./mi_proyecto

# Luego usar la config personalizada
cug generate -c ./mi_proyecto/my_config.toml
```

---

## Prioridad de Configuración

Los valores se resuelven con esta prioridad (el más alto gana):

1. **Flags CLI** — `--orders 50000` sobreescribe todo
2. **Archivo TOML** — `target_orders = 100000` en el config
3. **Defaults internos** — Valores hardcodeados en el código

> [!NOTE]
> Los flags `--strict` / `--no-strict` siempre sobreescriben el valor de `integrity_strict` del archivo TOML. Esto permite validar temporalmente sin editar archivos de configuración.

---

← [Volver al índice](README.md) | [Configuración TOML →](configuracion-toml.md)
