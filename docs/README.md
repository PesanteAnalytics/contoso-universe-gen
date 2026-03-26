# Contoso Universe Generator — Documentación

> **CUG** genera datasets sintéticos de retail 100% relacionales, listos para Power BI, DuckDB, Parquet, SQL Server y más. Cada ejecución produce tablas dimensionales y de hechos coherentes, con eventos históricos realistas (COVID, Black Friday, estacionalidad).

---

## 📚 Índice de la Documentación

| Documento | Descripción |
|-----------|-------------|
| [Instalación](instalacion.md) | Prerequisitos, instalación con pip/uv, drivers ODBC |
| [Referencia CLI](cli-referencia.md) | Todos los comandos (`generate`, `info`, `categories`, `formats`, `init`) con opciones y ejemplos |
| [Configuración TOML](configuracion-toml.md) | Estructura completa del archivo `.toml` con explicaciones detalladas |
| [Formatos de Salida](output-formats.md) | Los 7 formatos soportados (Parquet, CSV, DuckDB, Delta, JSON, Excel, SQL Server) |
| [Esquema de Datos](esquema-datos.md) | Las 7 tablas generadas, columnas, tipos de datos, relaciones FK |
| [SQL Server](sqlserver.md) | Guía dedicada: ODBC drivers, autenticación, mapeo de tipos, troubleshooting |
| [Recetas Rápidas](recetas.md) | Escenarios comunes resueltos en un solo comando |
| [Plugins de Categorías (YAML)](category-plugins.md) | Schema YAML, campos, defaults, cómo crear categorías custom |
| [Referencia i18n](i18n-reference.md) | Qué cambia y qué NO cambia por idioma — impacto real del setting `language` |

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

- **Roadmap del proyecto:** [`ROADMAP.md`](../ROADMAP.md)

- **Configuraciones predefinidas:** [`configs/`](../configs/)

---

_Contoso Universe Generator v0.2.0_
