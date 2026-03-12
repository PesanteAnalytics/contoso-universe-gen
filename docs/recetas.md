# Recetas Rápidas

> Escenarios comunes resueltos con un solo comando. Copia y pega directamente en tu terminal.

---

## 🧪 Prueba Rápida

El escenario más básico: verificar que todo funciona.

```bash
# ~5K órdenes, formato parquet, configuración quicktest
cug generate -c configs/quicktest.toml
```

**Output:** `./output/` con archivos `.parquet` para cada tabla.

---

## 📊 Dataset para Power BI (Parquet)

El caso más común: generar datos para importar en Power BI Desktop.

```bash
# 100K órdenes en Parquet (formato optimal para Power BI)
cug generate -n 100000 -f parquet
```

Para Power BI en español:

```bash
cug generate -n 100000 -f parquet -l es
```

---

## 🗄️ SQL Server Express Local

Cargar datos directamente en SQL Server Express con Windows Authentication.

```bash
# 100K órdenes en SQL Server Express
cug generate -n 100000 -f sqlserver \
  --sqlserver-name "localhost\SQLEXPRESS" \
  --sqlserver-db ContosoRetail
```

---

## 🔗 Parquet + SQL Server (simultáneo)

Generar ambos formatos en una sola ejecución — archivos locales y base de datos.

```bash
cug generate -n 100000 -f parquet,sqlserver \
  --sqlserver-name "localhost\SQLEXPRESS" \
  --sqlserver-db ContosoRetail
```

---

## 🎓 Workshop / Capacitación

Multi-formato para que los participantes elijan su herramienta preferida.

```bash
# Parquet + CSV + DuckDB, en español, 50K órdenes
cug generate -n 50000 -f parquet,csv,duckdb -l es
```

---

## 🏭 Dataset de Producción (1M órdenes)

Para testing a escala con validación de integridad.

```bash
# Usar config predefinido (1M, español, strict)
cug generate -c configs/retail_1M_es.toml --strict
```

O manualmente:

```bash
cug generate -n 1000000 -f parquet -l es --strict
```

---

## ☁️ Microsoft Fabric / Lakehouse (Delta)

Generar tablas Delta Lake listas para subir a OneLake.

```bash
cug generate -n 500000 -f delta --delta-mode overwrite
```

---

## 📤 Exportar a CSV (compatible con todo)

Para compartir datos con sistemas que solo aceptan CSV.

```bash
# CSV estándar (con compresión gzip automática)
cug generate -n 200000 -f csv

# CSV con punto y coma (para locales europeos)
cug generate -n 100000 -f csv --csv-separator ";"
```

---

## 📋 Datos de prueba para API (JSON)

Generar datos en formato JSON para testing de APIs.

```bash
# NDJSON (un registro por línea, ideal para streaming)
cug generate -n 10000 -f json

# JSON array (ideal para payloads REST)
cug generate -n 5000 -f json --json-rows
```

---

## 📎 Compartir con Excel

Para stakeholders que prefieren Excel.

```bash
# Todo en un solo workbook (una hoja por tabla)
cug generate -n 20000 -f excel

# Un archivo .xlsx por tabla
cug generate -n 20000 -f excel --excel-multi
```

> ⚠️ Excel tiene límite de ~1M filas por hoja. Usa `parquet` para datasets grandes.

---

## 🔄 Reproducibilidad Garantizada

Generar el mismo dataset exacto cada vez.

```bash
# Misma semilla = mismo output
cug generate --seed 42 -n 100000 -f parquet -o ./output/v1

# Otra versión con semilla diferente
cug generate --seed 2024 -n 100000 -f parquet -o ./output/v2
```

---

## 🌍 Multi-idioma

Generar datasets en diferentes idiomas.

```bash
# Español
cug generate -n 50000 -f parquet -l es

# Portugués
cug generate -n 50000 -f parquet -l pt

# Chino
cug generate -n 50000 -f parquet -l zh

# Árabe
cug generate -n 50000 -f parquet -l ar
```

Ver idiomas disponibles:

```bash
cug info
```

---

## 🔍 Consultar DuckDB Generado

Después de generar en formato DuckDB, puedes consultar inmediatamente:

```bash
# Generar
cug generate -n 100000 -f duckdb

# Consultar con DuckDB CLI
duckdb ./output/contoso.duckdb
```

```sql
-- Ventas por año
SELECT d.Year, COUNT(*) as Ventas, SUM(f.TotalAmount) as Total
FROM FactSales f
JOIN DimDate d ON f.OrderDateKey = d.DateKey
GROUP BY d.Year
ORDER BY d.Year;

-- Top 10 productos más vendidos
SELECT p.ProductName, SUM(f.Quantity) as Unidades
FROM FactSales f
JOIN DimProduct p ON f.ProductKey = p.ProductKey
GROUP BY p.ProductName
ORDER BY Unidades DESC
LIMIT 10;
```

---

## 🏗️ Escenario Completo (todos los formatos)

Para generar absolutamente todo en una sola corrida:

```bash
cug generate -n 100000 \
  -f parquet,csv,duckdb,delta,json,excel,sqlserver \
  --sqlserver-name "localhost\SQLEXPRESS" \
  --sqlserver-db ContosoRetail \
  -l es \
  --strict
```

---

## ⚡ Guía de Rendimiento

| target_orders | Tiempo aprox. | Memoria aprox. |
|--------------|--------------|----------------|
| 5,000 | ~5 seg | ~100 MB |
| 100,000 | ~30 seg | ~500 MB |
| 1,000,000 | ~5 min | ~2 GB |
| 10,000,000 | ~45 min | ~8 GB |

> [!TIP]
> Para datasets muy grandes (>5M), reduce `chunk_days` en el config TOML para controlar el uso de memoria.

---

← [SQL Server](sqlserver.md) | [Volver al índice](README.md)
