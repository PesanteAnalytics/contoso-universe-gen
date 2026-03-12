# Contoso Universe Generator — Documentación

> **CUG** genera datasets sintéticos de retail 100% relacionales, listos para Power BI, DuckDB, Parquet, SQL Server y más. Cada ejecución produce tablas dimensionales y de hechos coherentes, con eventos históricos realistas (COVID, Black Friday, estacionalidad).

---

## 📚 Índice de la Documentación

| Documento | Descripción |
|-----------|-------------|
| [Instalación](instalacion.md) | Prerequisitos, instalación con pip/uv, drivers ODBC |
| [Referencia CLI](cli-referencia.md) | Todos los comandos (`generate`, `info`, `categories`, `formats`, `init`) con opciones y ejemplos |
| [Configuración TOML](configuracion-toml.md) | Estructura completa del archivo `.toml` con explicaciones detalladas |
| [Formatos de Salida](formatos-salida.md) | Los 7 formatos soportados (Parquet, CSV, DuckDB, Delta, JSON, Excel, SQL Server) |
| [Esquema de Datos](esquema-datos.md) | Las 7 tablas generadas, columnas, tipos de datos, relaciones FK |
| [SQL Server](sqlserver.md) | Guía dedicada: ODBC drivers, autenticación, mapeo de tipos, troubleshooting |
| [Recetas Rápidas](recetas.md) | Escenarios comunes resueltos en un solo comando |

---

## 📋 Planificación & Estrategia

Documentos de planificación del proyecto, estrategia y decisiones de diseño.

| Documento | Descripción |
|-----------|-------------|
| [Plan Maestro — Arquitectura Original](planning/cug_master_plan.md) | 🏗️ Documento fundacional: arquitectura, stack, plugins YAML, motor Polars, fases de implementación |
| [Comparación de Esquemas V2 vs CUG](planning/schema_comparison_v2_vs_cug.md) | 📊 Mapeo columna-por-columna entre DG V2 y CUG — compatibilidad Power BI |
| [CUG vs DG V2 — Análisis Estratégico](planning/contoso_comparison_strategy.md) | 🔍 Comparativa completa, oportunidades de contribución a SQLBI, beneficios, y plan de trabajo 4 fases |
| [Plan de Creación del Skill](planning/skill_creation_plan.md) | ✅ Plan original para crear la SKILL.md y la documentación en español (ya ejecutado) |
| [`ROADMAP.md`](../ROADMAP.md) | 🚀 Roadmap técnico del proyecto (v0.3 Prophet, v0.4 SDV) |

---

## 🚀 Inicio Rápido

```bash
# Instalación
pip install -e .

# Generar un dataset de prueba (~5K órdenes)
cug generate -c configs/quicktest.toml

# Generar 100K órdenes en Parquet (default)
cug generate -n 100000

# Generar 50K órdenes en español y múltiples formatos
cug generate -n 50000 -f parquet,csv,duckdb -l es
```

---

## 🏗️ Arquitectura

CUG genera un esquema estrella (star schema) con 7 tablas:

```
                    ┌─────────────┐
                    │   DimDate   │
                    └──────┬──────┘
                           │
┌─────────────┐    ┌───────┴───────┐    ┌─────────────┐
│ DimCustomer │────│   FactSales   │────│  DimProduct  │
└─────────────┘    └───────┬───────┘    └─────────────┘
                           │
                    ┌──────┴──────┐
                    │  DimStore   │
                    └──────┬──────┘
                           │
               ┌───────────┴────────────┐
               │     DimCurrency        │
               └───────────┬────────────┘
                           │
               ┌───────────┴────────────┐
               │  DimCurrencyExchange   │
               └────────────────────────┘
```

---

## 📎 Enlaces Útiles

- **Manual completo (en inglés/español):** [`MANUAL.md`](../MANUAL.md)
- **Roadmap del proyecto:** [`ROADMAP.md`](../ROADMAP.md)
- **Configuraciones predefinidas:** [`configs/`](../configs/)

---

_Contoso Universe Generator v0.2.0_
