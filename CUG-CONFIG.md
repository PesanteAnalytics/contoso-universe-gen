# 📦 CUG — Configuración Activa

> **Tarjeta de configuración persistente** para el Contoso Universe Generator.
> Edita los valores en la columna **Valor** y el agente los aplicará automáticamente.
> Los valores aquí son los **defaults** — cambia solo lo que necesites.

---

## 🔧 General

| Variable   | Valor      | Opciones                       |
| ---------- | ---------- | ------------------------------ |
| start_date | 2022-01-01 | Fecha YYYY-MM-DD               |
| end_date   | 2026-03-17 | Fecha YYYY-MM-DD               |
| language   | en         | en, es, pt, fr, de, zh, ja, ar |
| country    | US         | Código ISO 3166-1              |
| seed       | 42         | Cualquier entero               |
| chunk_days | 30         | Entero > 0                     |

## 📤 Output

| Variable         | Valor    | Opciones                                                                              |
| ---------------- | -------- | ------------------------------------------------------------------------------------- |
| output_path      | ./output | Ruta de directorio                                                                    |
| formats          | parquet, csv, duckdb, delta, json | parquet, csv, duckdb, delta, json, excel, sqlserver — separar con coma para múltiples |
| target_orders    | 1000000  | Entero > 0 (≈ filas generadas)                                                        |
| compress         | true     | true / false — compresión Gzip para CSV                                               |
| integrity_check  | false    | true / false — validar integridad FK                                                  |
| integrity_strict | true     | true / false — abortar en violaciones FK                                              |

## 📄 Opciones de Formato

> Solo aplican las opciones del formato seleccionado arriba.

### Parquet

| Variable               | Valor | Opciones                              |
| ---------------------- | ----- | ------------------------------------- |
| parquet_compression    | zstd  | zstd, snappy, gzip, lz4, brotli, none |
| parquet_row_group_size | auto  | Entero o auto                         |

### CSV

| Variable           | Valor | Opciones                                |
| ------------------ | ----- | --------------------------------------- |
| csv_separator      | ,     | Cualquier carácter                      |
| csv_include_header | true  | true / false                            |
| csv_null_value     |       | Cualquier string (vacío = default)      |
| csv_date_format    | auto  | auto = ISO 8601, o patrón como %Y-%m-%d |

### DuckDB

| Variable       | Valor          | Opciones                   |
| -------------- | -------------- | -------------------------- |
| duckdb_db_name | contoso.duckdb | Nombre del archivo .duckdb |

### Delta Lake

| Variable           | Valor     | Opciones                                            |
| ------------------ | --------- | --------------------------------------------------- |
| delta_mode         | overwrite | overwrite, append, error                            |
| delta_partition_by |           | Lista de columnas, ej: Year (vacío = sin partición) |
| delta_name         | contoso   | Nombre metadata Delta                               |

### JSON

| Variable          | Valor | Opciones                                                   |
| ----------------- | ----- | ---------------------------------------------------------- |
| json_row_oriented | false | false = NDJSON (1 record/línea), true = JSON array         |
| json_pretty       | false | true / false — pretty-print (solo con row_oriented = true) |

### Excel

| Variable              | Valor        | Opciones                                                    |
| --------------------- | ------------ | ----------------------------------------------------------- |
| excel_single_workbook | true         | true = todas las tablas en 1 xlsx, false = 1 xlsx por tabla |
| excel_workbook_name   | contoso.xlsx | Nombre del archivo Excel                                    |

### SQL Server

| Variable                    | Valor                | Opciones                                             |
| --------------------------- | -------------------- | ---------------------------------------------------- |
| sqlserver_server            | localhost\SQLEXPRESS | Instancia del servidor                               |
| sqlserver_database          | ContosoRetail        | Base de datos destino (se crea si no existe)         |
| sqlserver_schema            | dbo                  | Esquema destino                                      |
| sqlserver_driver            | auto                 | auto = detectar, o nombre exacto del driver ODBC     |
| sqlserver_trusted           | true                 | true = Windows Auth, false = SQL Auth                |
| sqlserver_username          |                      | Solo si trusted = false                              |
| sqlserver_password          |                      | Solo si trusted = false                              |
| sqlserver_if_exists         | replace              | replace, append, fail                                |
| sqlserver_batch_size        | 5000                 | Filas por INSERT batch                               |
| sqlserver_connection_string |                      | ODBC string completa (sobreescribe todo lo anterior) |

## 👥 Clientes

| Variable         | Valor | Opciones                                  |
| ---------------- | ----- | ----------------------------------------- |
| pool_size        | 50000 | Entero > 0 — total clientes únicos        |
| active_pct       | 0.30  | 0.01 – 1.0 — % que compran al menos 1 vez |
| online_pct_start | 0.05  | 0.0 – 1.0 — % ventas online al inicio     |
| online_pct_end   | 0.55  | 0.0 – 1.0 — % ventas online al final      |

## 📂 Categorías

| Variable     | Valor                            | Opciones                                      |
| ------------ | -------------------------------- | --------------------------------------------- |
| enabled      | electronics, home, gaming, media | Categorías activas separadas por coma         |
| custom_paths |                                  | Rutas a plugins YAML custom (vacío = ninguno) |

## 📅 Eventos Anuales

> Eventos recurrentes que afectan el volumen de ventas cada año.
> Para agregar: nueva fila. Para desactivar: elimina la fila o pon factor = 1.0.

| Evento         | Mes | Día | Factor |
| -------------- | --- | --- | ------ |
| Black Friday   | 11  | 25  | 2.8    |
| Cyber Monday   | 11  | 28  | 2.5    |
| Christmas      | 12  | 25  | 2.0    |
| Back to School | 8   | 15  | 1.8    |
| Prime Day      | 7   | 12  | 2.5    |

## 📅 Eventos Históricos (One-Time)

> Eventos únicos con impacto en un rango específico de fechas.
> Para agregar: nueva fila. Para desactivar: elimina la fila o pon factor = 1.0.

| Evento                  | Fecha Inicio | Fecha Fin  | Factor |
| ----------------------- | ------------ | ---------- | ------ |
| COVID Lockdown Drop     | 2020-03-15   | 2020-04-30 | 0.45   |
| COVID eCommerce Surge   | 2020-05-01   | 2021-03-31 | 1.18   |
| Post-COVID Recovery     | 2021-04-01   | 2022-06-30 | 1.06   |
| Inflation Pressure 2022 | 2022-01-01   | 2022-12-31 | 0.92   |
| AI & Electronics Boom 2023-2024 | 2023-06-01   | 2024-12-31 | 1.09   |

## 📊 Factores por Día de Semana

> Lun=0 … Dom=6. Factor 1.0 = promedio. Mayor = más ventas, menor = menos.

| Día       | Factor |
| --------- | ------ |
| Lunes     | 0.75   |
| Martes    | 0.85   |
| Miércoles | 0.95   |
| Jueves    | 1.05   |
| Viernes   | 1.20   |
| Sábado    | 1.60   |
| Domingo   | 0.30   |

---

> **Última ejecución**: _2026-03-12 16:15_
> **Última modificación**: _2026-03-12 16:14_
