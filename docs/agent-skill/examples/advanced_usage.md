# Advanced Usage — CUG Agent Skill

Advanced configurations, custom events, YAML plugins, and multi-format outputs.

---

## 🔵 Multi-Format Workshop Bundle

Generate data in three formats simultaneously for a workshop:

**CUG-CONFIG.md setup:**
```
| formats | parquet, csv, duckdb |
| target_orders | 50000 |
| language | es |
```

**Equivalent CLI:**
```bash
cug generate -n 50000 -f parquet,csv,duckdb -l es
```

**DuckDB auto-creates 3 analytical views:**

| View | Description |
|---|---|
| `v_sales_summary` | Daily sales totals (date, year, month, orders, revenue, margin) |
| `v_top_products` | Top 20 products by revenue |
| `v_category_trend` | Monthly revenue by category |

---

## 🔵 Delta Lake for Microsoft Fabric

**CUG-CONFIG.md setup:**
```
| formats | delta |
| target_orders | 500000 |
| delta_mode | overwrite |
```

**Equivalent CLI:**
```bash
cug generate -n 500000 -f delta --delta-mode overwrite
```

> **Note**: `Null`-type columns are automatically cast to `String` before writing (Delta requirement).

---

## 🔵 Custom Historical Events

Simulate business events like a COVID impact or a store expansion:

**CUG-CONFIG.md Historical Events table:**

| Name | Date Start | Date End | Factor |
|---|---|---|---|
| COVID Impact | 2020-03-01 | 2021-06-30 | 0.4 |
| Post-COVID Recovery | 2021-07-01 | 2022-12-31 | 1.3 |
| Mega Sale 2023 | 2023-11-01 | 2023-11-30 | 2.5 |

**TOML equivalent (for reference):**
```toml
[[events.one_time]]
name = "COVID Impact"
date_start = "2020-03-01"
date_end = "2021-06-30"
factor = 0.4

[[events.one_time]]
name = "Post-COVID Recovery"
date_start = "2021-07-01"
date_end = "2022-12-31"
factor = 1.3
```

---

## 🔵 Custom Annual Events

Tune recurring seasonal peaks:

**CUG-CONFIG.md Annual Events table:**

| Name | Month | Day | Factor |
|---|---|---|---|
| Black Friday | 11 | 28 | 4.5 |
| Cyber Monday | 12 | 2 | 3.8 |
| Valentine's Day | 2 | 14 | 2.1 |
| Back to School | 8 | 15 | 1.8 |

---

## 🔵 YAML Category Plugin

Add a custom product category (e.g., Fashion & Apparel):

**1. Create the YAML plugin:**
```yaml
# my_plugins/fashion.yaml
plugin_id: fashion
display_names:
  en: Fashion & Apparel
  es: Moda y Ropa
subcategories:
  - id: shoes
    display_names: { en: Shoes, es: Zapatos }
    brands: [Nike, Adidas, Puma]
    price_range: [40.0, 350.0]
    margin_range: [0.15, 0.45]
    trend:
      2020: 0.60
      2024: 1.20
    products:
      - name_template: "{brand} {model} {spec}"
        models: [Air Max, Superstar, Velocity]
        specs: [Size 8, Size 10, Size 12]
```

**2. Register in CUG-CONFIG.md:**
```
| enabled | electronics, home, gaming, media, fashion |
| custom_paths | ./my_plugins/fashion.yaml |
```

> **Full guide**: [`docs/category-plugins.md`](../../category-plugins.md)

---

## 🔵 High-Volume Production Run (1M+ orders)

For large datasets optimized for performance:

**CUG-CONFIG.md setup:**
```
| target_orders | 1000000 |
| formats | parquet |
| language | en |
| seed | 42 |
| chunk_days | 30 |
| compress | true |
| integrity_check | true |
| integrity_strict | true |
```

**Equivalent CLI:**
```bash
cug generate -n 1000000 -f parquet --seed 42 --strict
```

> `chunk_days = 30` controls memory usage — smaller chunks = less RAM, more time.

---

## 🔵 Versioned Output Directories

Generate multiple snapshots for A/B testing or version control:

```bash
# Version 1 — baseline
cug generate --seed 42 -n 100000 -f parquet -o ./output/v1

# Version 2 — modified config
cug generate --seed 99 -n 100000 -f parquet -o ./output/v2
```

In `CUG-CONFIG.md`, set:
```
| output_path | ./output/v1 |
| seed | 42 |
```

---

## 🔵 Weekday Demand Shaping

Customize demand by day of week (useful for retail realism):

**CUG-CONFIG.md Weekday Factors table:**

| Day | Factor |
|---|---|
| Monday | 0.85 |
| Tuesday | 0.80 |
| Wednesday | 0.90 |
| Thursday | 0.95 |
| Friday | 1.20 |
| Saturday | 1.60 |
| Sunday | 1.40 |

This simulates typical retail patterns with weekend peaks.
