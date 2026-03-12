# 🌌 Contoso Universe Generator — Plan Maestro God-Level

## Descripción

Un generador de datos sintéticos de **nivel enterprise** para retail/consumer tech, escrito **100% en Python moderno**. Supera a Contoso DG V2 en:

- **Stack nativo Python**: Polars + DuckDB + Faker → sin dependencias de .NET
- **Multi-idioma real**: datos en EN, ES, PT, FR, DE, ZH y más (nombres, ciudades, categorías)
- **Categorías extensibles**: sistema de plugins — agrega nuevas industrias con un YAML
- **Motor determinístico mejorado**: seed por día + seed por entidad, 100% reproducible
- **Salidas universales**: CSV, Parquet, DuckDB database, Delta Lake
- **CLI interactiva** con Rich + Typer (terminal hermosa)
- **Zero .NET / Zero Excel**: toda la metadata en YAML/TOML

---

> [!WARNING]
> **REGLAS DE AISLAMIENTO ESTRICTAS — LEER ANTES DE IMPLEMENTAR**
>
> Este proyecto es **completamente nuevo e independiente** del repositorio `Contoso-Data-Generator-V2`.
>
> 1. **PROHIBIDO** copiar código fuente C# o Python del V2 al nuevo repo
> 2. **PROHIBIDO** importar, referenciar o depender del binario `DatabaseGenerator.exe`
> 3. **SOLO se extraen**: conceptos lógicos, patrones de negocio, vocabulario de campos, y multipliers de categorías como **inspiración documental**
> 4. El nuevo repo debe poder correr sin que el V2 exista en el sistema

---

## Arquitectura del Nuevo Proyecto

### Nombre: `contoso-universe-gen` (o `cug`)

```
contoso-universe-gen/
├── pyproject.toml              # uv / Poetry - deps modernas
├── README.md
├── .gitignore
│
├── cug/                        # Paquete principal
│   ├── __init__.py
│   ├── cli.py                  # CLI con Typer + Rich
│   ├── config.py               # Pydantic v2: schemas de configuración
│   ├── engine/
│   │   ├── __init__.py
│   │   ├── orchestrator.py     # Orquestador principal (equiv. a Engine.cs)
│   │   ├── temporal.py         # Lógica de fechas, spikes, estacionalidad
│   │   ├── weights.py          # Interpolación de pesos diarios (Polars)
│   │   └── seeder.py           # Seed manager determinístico por día/entidad
│   │
│   ├── generators/
│   │   ├── __init__.py
│   │   ├── customers.py        # Generador de clientes (Faker + i18n)
│   │   ├── products.py         # Catálogo de productos + categorías YAML
│   │   ├── stores.py           # Tiendas físicas + online
│   │   ├── sales.py            # Transacciones de ventas (Polars vectorizado)
│   │   ├── calendar.py         # DimDate extendida + holidays por país
│   │   └── currency.py         # Tipos de cambio (ECB real o synthetic)
│   │
│   ├── i18n/
│   │   ├── __init__.py
│   │   ├── locales.py          # Registro de idiomas disponibles
│   │   └── translators.py      # Traducción de labels con deep-l / static maps
│   │
│   ├── categories/             # SISTEMA DE PLUGINS DE CATEGORÍAS
│   │   ├── __init__.py
│   │   ├── registry.py         # CategoryRegistry: descubre YAMLs automáticamente
│   │   ├── base.py             # CategoryPlugin ABC
│   │   └── builtin/
│   │       ├── electronics.yaml    # Computers, Audio, Cameras, Cell phones...
│   │       ├── home.yaml           # Home Appliances, Furniture
│   │       ├── gaming.yaml         # Games & Toys, Consoles
│   │       └── media.yaml          # Music, Movies, Streaming
│   │
│   ├── writers/
│   │   ├── __init__.py
│   │   ├── base.py             # IWriter ABC
│   │   ├── csv_writer.py
│   │   ├── parquet_writer.py   # Via Polars nativo
│   │   ├── duckdb_writer.py    # DuckDB database file
│   │   └── delta_writer.py     # Delta Lake via deltalake-python
│   │
│   └── utils/
│       ├── __init__.py
│       ├── progress.py         # Rich progress bars
│       └── validators.py       # Validación de config con Pydantic
│
├── configs/
│   ├── default.toml            # Config base
│   ├── retail_1M_en.toml       # 1M rows en inglés
│   ├── retail_5M_es.toml       # 5M rows en español
│   └── retail_100M_duckdb.toml # 100M rows → DuckDB
│
├── tests/
│   ├── test_engine.py
│   ├── test_categories.py
│   ├── test_i18n.py
│   └── test_writers.py
│
└── docs/
    ├── ARCHITECTURE.md
    ├── CATEGORY_PLUGIN_GUIDE.md  # Cómo agregar nuevas categorías
    └── I18N_GUIDE.md
```

---

## Módulos Clave — Diseño Detallado

### 1. `config.py` — Pydantic v2 Schema

```toml
# configs/retail_1M_en.toml
[general]
orders_count = 1_000_000
start_date = "2018-01-01"
end_date   = "2026-12-31"
language   = "en"          # 🌍 NUEVA FEATURE
seed       = 42

[output]
format = "parquet"         # csv | parquet | duckdb | delta
path   = "./output/"
compress = true

[customers]
pool_size   = 200_000
active_pct  = 0.20

[categories]
enabled = ["electronics", "home", "gaming"]  # Plugin keys
custom  = []                                  # Rutas a YAMLs externos

[events]
# Annual spikes (Black Friday, Christmas, etc.)
[[events.annual]]
name  = "BlackFriday"
month = 11
day   = 24
factor = 4.5

# One-time world events
[[events.one_time]]
name   = "COVID_WFH_Boom"
date   = "2020-03-15"
end    = "2021-06-30"
categories = { "Computers" = 1.65, "Games and Toys" = 1.90 }
```

### 2. Sistema de Plugins de Categorías (YAML)

```yaml
# categories/builtin/electronics.yaml
plugin_id: electronics
display_names:
  en: Electronics
  es: Electrónica
  pt: Eletrônicos
  fr: Électronique
  de: Elektronik
  zh: 电子产品

subcategories:
  - id: computers
    display_names:
      en: Computers
      es: Computadoras
    brands: [Microsoft, Dell, HP, Apple, Lenovo, Asus]
    price_range: [299, 3499]
    margin_range: [0.08, 0.22]
    trend: # Inspirado en multipliers del V2 — recreados desde cero
      2018: 0.85
      2020: 1.65 # COVID WFH boom
      2024: 0.88
    products:
      - name_template: "{brand} {model} {spec}"
        models: [Laptop, Desktop, AIO, Mini PC]
        specs: [i5/16GB, i7/32GB, Ryzen 5, M3]
```

### 3. Motor de Generación — Polars Vectorizado

El orquestador reemplaza el `Parallel.For` de C# con **procesamiento por chunks en Polars**:

```python
# engine/orchestrator.py (pseudocódigo de diseño)
import polars as pl
import duckdb
from datetime import date

class GenerationOrchestrator:
    def run(self, config: Config) -> None:
        # 1. Setup: construir catálogos (DimProduct, DimCustomer, DimStore)
        # 2. Por cada chunk de días (ej. 30 días):
        #    - Calcular pesos del día (weight interpolation en Polars)
        #    - Generar órdenes como DataFrame Polars (vectorizado)
        #    - Aplicar multiplicadores de categoría/evento
        #    - Acumular en DuckDB en-memoria para joins eficientes
        # 3. Al final: escribir al formato elegido
```

### 4. i18n — Multi-idioma Real

```python
# i18n/locales.py
LOCALE_MAP = {
    "en": {"faker": "en_US", "name": "English"},
    "es": {"faker": "es_MX", "name": "Español"},
    "pt": {"faker": "pt_BR", "name": "Português"},
    "fr": {"faker": "fr_FR", "name": "Français"},
    "de": {"faker": "de_DE", "name": "Deutsch"},
    "zh": {"faker": "zh_CN", "name": "中文"},
    "ja": {"faker": "ja_JP", "name": "日本語"},
    "ar": {"faker": "ar_AA", "name": "العربية"},
}
```

Con `--language es`:

- Nombres de clientes: `Carlos Ramírez`, `María González`
- Ciudades: `Monterrey`, `Bogotá`, `Madrid`
- Categorías (si están traducidas en YAML): `Electrónica`, `Computadoras`

### 5. CLI — Typer + Rich

```bash
# Uso básico
cug generate --config configs/retail_1M_en.toml

# Override inline
cug generate --orders 500000 --language es --output parquet --out ./mi_output/

# Modo interactivo (wizard)
cug wizard

# Ver categorías disponibles
cug categories list

# Agregar categoría custom
cug categories add ./my_fashion_category.yaml
```

---

## Stack Tecnológico

| Librería          | Rol                      | Por qué                                                  |
| ----------------- | ------------------------ | -------------------------------------------------------- |
| **Polars**        | DataFrame engine         | 5-10x más rápido que Pandas, lazy evaluation             |
| **DuckDB**        | Motor analítico embebido | In-process SQL, ideal para joins de dimensiones y output |
| **Faker**         | Datos sintéticos         | Soporte multi-locale nativo                              |
| **Pydantic v2**   | Validación de config     | Schemas tipados, errores claros                          |
| **Typer**         | CLI framework            | Basado en type hints, autocomplete                       |
| **Rich**          | Terminal UI              | Progress bars, tablas, colores                           |
| **TOML** (stdlib) | Configuración            | Más legible que JSON, Python 3.11+ built-in              |
| **PyYAML**        | Plugins de categorías    | YAML para datos maestros legibles                        |
| **deltalake**     | Delta Lake output        | Writer Python nativo para Fabric                         |
| **pyarrow**       | Parquet backend          | Requerido por Polars + Delta                             |
| **uv**            | Package manager          | Ultrarrápido, reemplaza pip+venv                         |

---

## Comparativa V2 → Nuevo (Referencia, No Copia)

| Aspecto          | Contoso DG V2 (referencia) | Contoso Universe Gen (nuevo) |
| ---------------- | -------------------------- | ---------------------------- |
| Lenguaje         | C# / .NET 8                | Python 3.12+                 |
| DataFrame        | Nativo C# arrays           | **Polars**                   |
| SQL Engine       | SQL Server                 | **DuckDB** embebido          |
| Config           | JSON                       | **TOML**                     |
| Datos maestros   | Excel (.xlsx)              | **YAML plugins**             |
| Multi-idioma     | No                         | **Sí (8+ idiomas)**          |
| Categorías extra | Hardcoded                  | **Plugin system**            |
| CLI              | Args posicionales          | **Typer + wizard**           |
| Output           | CSV/Parquet/Delta          | CSV/Parquet/**DuckDB**/Delta |
| Instalación      | .NET SDK required          | `uv pip install .`           |

---

## Estructura del Repositorio GitHub

```
Repositorio: contoso-universe-gen (NUEVO - privado inicialmente)
Branch: main

.github/
  workflows/
    ci.yml          # Tests en PR
    release.yml     # Build + publish package

NOTICE.md  ← ARCHIVO CRÍTICO:
  "Este proyecto está INSPIRADO conceptualmente en Contoso DG V2 (SQLBI/Microsoft).
   No contiene código derivado. Reimplementación original en Python."
```

---

## Plan de Implementación por Fases

### Fase 1 — Fundación (MVP)

- [ ] Crear repo `contoso-universe-gen` con estructura base
- [ ] `pyproject.toml` con uv + todas las deps
- [ ] `config.py` con Pydantic v2 schemas
- [ ] `CategoryRegistry` con 4 categorías builtin (electronics, home, gaming, media)
- [ ] `DimDate` generator con Polars
- [ ] `DimProduct` desde YAMLs
- [ ] `DimCustomer` con Faker multi-locale
- [ ] `FactSales` generator básico (Polars vectorizado)
- [ ] CSVWriter funcional
- [ ] CLI básica (`cug generate`)

### Fase 2 — Motor Completo

- [ ] `weights.py`: interpolación temporal + spikes (COVID, Black Friday, etc.)
- [ ] `temporal.py`: Poisson delivery dates, seeder por día
- [ ] `stores.py`: tiendas físicas + online con geolocalización
- [ ] `currency.py`: exchange rates sintéticos o ECB
- [ ] ParquetWriter + DuckDBWriter
- [ ] CLI wizard interactivo

### Fase 3 — God Mode Features

- [ ] i18n completo: YAML translations en todas las categorías
- [ ] `cug categories add` para plugins externos
- [ ] DeltaLakeWriter
- [ ] `cug analyze` command (DuckDB SQL report post-generación)
- [ ] Modo streaming: generar 100M+ rows sin RAM overflow
- [ ] Tests completos

---

## Verificación del Plan

### Tests Automatizados (pytest)

```bash
# Instalar y correr tests
uv pip install -e ".[dev]"
pytest tests/ -v --tb=short
```

**Cobertura mínima Goal (Fase 1)**:

- `test_config.py`: Validación Pydantic, TOML parsing
- `test_categories.py`: CategoryRegistry descubre YAMLs, YAML schema válido
- `test_engine.py`: Generación de 1000 órdenes → output determinístico
- `test_i18n.py`: Faker genera nombres en cada locale
- `test_writers.py`: CSV y Parquet escriben sin errores

### Verificación Manual (Fase 1 MVP)

```bash
cug generate --config configs/retail_1M_en.toml --orders 10000
# → Verifica: output/sales.parquet existe, tiene ~10000 filas
# → Verifica: output/dim_product.parquet tiene productos en inglés

cug generate --config configs/retail_1M_en.toml --orders 10000 --language es
# → Verifica: clientes tienen nombres en español
# → Verifica: categorías traducidas donde aplica

cug categories list
# → Muestra: electronics, home, gaming, media

duckdb output/contoso.db -c "SELECT COUNT(*) FROM sales;"
# → Retorna el count correcto
```
