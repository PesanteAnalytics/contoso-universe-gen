# Basic Usage — CUG Agent Skill

Common scenarios and trigger phrases for everyday use.

---

## 🟢 Quick Test Dataset (~5K orders)

**User says:**
> "Generate a quick test dataset" / "Dame datos de prueba rápido"

**Agent behavior:**
1. Reads (or creates) `CUG-CONFIG.md`
2. Sets `target_orders = 5000`, format = `parquet`
3. Executes `cug generate -c configs/quicktest.toml`

**Output:**
```
✅ Dataset generated successfully
  📁 Directory: ./output
  📊 Tables: 7 (star schema)
  📝 Format: parquet
  🔢 Orders: ~5,000
  ⏱️ Time: 2.1s
```

---

## 🟢 Standard 100K Dataset

**User says:**
> "Generate 100,000 rows in Parquet" / "Generar 100K filas en parquet"

**Agent behavior:**
1. Updates `CUG-CONFIG.md`: `target_orders = 100000`, `formats = parquet`
2. Confirms: *"Your configuration is updated. Shall I proceed?"*
3. Executes generation

---

## 🟢 CSV for Excel Users

**User says:**
> "Create a CSV dataset for my team" / "Generar CSV para el equipo"

**Agent behavior:**
1. Updates `formats = csv` in `CUG-CONFIG.md`
2. Warns if `target_orders > 800,000` and Excel is requested
3. Executes: `cug generate -n 50000 -f csv`

---

## 🟢 Power BI Workshop Dataset

**User says:**
> "I need data for my Power BI workshop in Spanish" / "Datos para Power BI en español"

**Agent behavior:**
1. Updates `language = es`, `formats = parquet`
2. Executes with recommended `target_orders = 50000`

**What changes in Spanish mode:**
- `MonthName`, `DayName` → translated
- `CategoryName` → from YAML `display_names`
- Customer cities/countries → Latin American locale
- Primary currency → `MXN`

---

## 🟢 Populate SQL Server

**User says:**
> "Meter datos en SQL Server" / "Populate SQL Server with demo data"

**Agent behavior:**
1. Updates `formats = sqlserver` in `CUG-CONFIG.md`
2. Uses `<sql_server_instance>` placeholder from skill config
3. Executes:
   ```bash
   cug generate -n 100000 -f sqlserver \
     --sqlserver-name "<sql_server_instance>" \
     --sqlserver-db ContosoDemo
   ```

> **Note**: SQL Server output requires the `pyodbc` optional dependency.
> Install it into the same environment as CUG: `pip install pyodbc`
> (CUG is not on PyPI yet, so there is no `[sqlserver]` extra to install.)

---

## 🟢 Reproducible Dataset (Seed)

**User says:**
> "Generate the same data as last time, seed 42"

**Agent behavior:**
1. Ensures `seed = 42` in `CUG-CONFIG.md`
2. Same seed → identical output every time (deterministic)

---

## ⚠️ Excel Warning Scenario

**User says:**
> "Generate 2 million rows in Excel"

**Agent behavior:**
1. Detects Excel + `target_orders > 800,000`
2. Warns: *"Excel has a hard limit of 1,048,576 rows. Your dataset would be truncated. Proceed anyway, or switch to Parquet?"*
3. Waits for user confirmation before proceeding
