# Category Plugins Guide (YAML)

> CUG uses YAML files to define product categories. This system allows you
> to add custom categories without touching Python code.

---

## System Architecture

```
cug/categories/
├── base.py              ← Classes: CategoryPlugin, Subcategory, ProductTemplate
├── registry.py          ← CategoryRegistry: loads builtins + custom
└── builtin/
    ├── electronics.yaml ← Canonical example (5 subcategories)
    ├── gaming.yaml
    ├── home.yaml
    └── media.yaml
```

### Loading Flow

1. `CategoryRegistry` automatically loads the 4 builtins from `builtin/`
2. If `[categories].custom_paths` has paths, they are loaded with `load_custom()`
3. `CategoryPlugin.from_yaml(path)` parses each YAML → Python objects
4. `generate_dim_product()` iterates over all categories in the registry

---

## Complete YAML Schema

```yaml
# ── Unique identifier (snake_case, required) ─────────────────────────
plugin_id: fashion

# ── Names per language (at least "en" required) ─────────────────────
display_names:
  en: Fashion & Apparel
  es: Moda y Ropa
  pt: Moda e Vestuário
  fr: Mode et Habillement
  de: Mode und Bekleidung
  zh: 时尚服饰
  ja: ファッション
  ar: أزياء

# ── Subcategories (at least 1 required) ──────────────────────────────
subcategories:

  - id: shoes                          # Unique ID snake_case
    display_names:                     # Localized names
      en: Shoes
      es: Zapatos
      pt: Sapatos
    brands: [Nike, Adidas, Puma, New Balance, Reebok]  # Available brands
    price_range: [40.0, 350.0]         # [min, max] unit price USD
    margin_range: [0.15, 0.45]         # [min, max] profit margin (0-1)
    trend:                             # Demand multiplier per year
      2018: 0.85                       # 0.85 = 15% below baseline
      2019: 0.90
      2020: 0.60                       # COVID drop
      2021: 0.75
      2022: 1.00                       # baseline
      2023: 1.15
      2024: 1.20                       # 20% above baseline
      2025: 1.25
      2026: 1.30
    products:                          # Templates for name generation
      - name_template: "{brand} {model} {spec}"
        models: [Air Max, Superstar, RS-X, Classic, Gel-Kayano]
        specs: [Size 8, Size 9, Size 10, Size 11, Size 12]
        brands: []                     # [] = uses subcategory brands

  - id: clothing
    display_names:
      en: Clothing
      es: Ropa
      pt: Roupas
    brands: [Zara, H&M, Uniqlo, Gap, Levi's]
    price_range: [15.0, 250.0]
    margin_range: [0.30, 0.65]
    trend:
      2020: 0.45
      2023: 1.10
    products:
      - name_template: "{brand} {model}"
        models: [T-Shirt, Jeans, Jacket, Dress, Hoodie, Sweater]
        specs: []
        brands: []
```

---

## Field Reference

### Root Level

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| `plugin_id` | `string` | ✅ | Unique identifier, snake_case. Example: `fashion` |
| `display_names` | `dict[str, str]` | ✅ | Map `language → name`. Minimum: `en` |
| `subcategories` | `list` | ✅ | At least 1 subcategory |

### Subcategory

| Field | Type | Required | Default | Description |
|-------|------|----------|---------|-------------|
| `id` | `string` | ✅ | — | Unique ID snake_case |
| `display_names` | `dict[str, str]` | ❌ | `{en: id}` | Localized names |
| `brands` | `list[str]` | ❌ | `[]` | Available brands |
| `price_range` | `[float, float]` | ❌ | `[99, 999]` | Price range [min, max] |
| `margin_range` | `[float, float]` | ❌ | `[0.10, 0.30]` | Margin range [min, max] |
| `trend` | `dict[int, float]` | ❌ | `{}` | Demand multiplier per year |
| `products` | `list[ProductTemplate]` | ❌ | `[]` | Product name templates |

### ProductTemplate

| Field | Type | Required | Default | Description |
|-------|------|----------|---------|-------------|
| `name_template` | `string` | ❌ | `{brand} {model}` | Name pattern with placeholders |
| `models` | `list[str]` | ❌ | `[]` | Model variants |
| `specs` | `list[str]` | ❌ | `[]` | Technical specifications |
| `brands` | `list[str]` | ❌ | Inherits sub | `[]` uses subcategory brands |

### `name_template` Placeholders

| Placeholder | Source | Example |
|-------------|--------|---------|
| `{brand}` | `brands` from product or subcategory | `Nike` |
| `{model}` | `models` from template | `Air Max` |
| `{spec}` | `specs` from template | `256GB` |
| `{size}` | Random: 43, 55, 65, 75, 85 (inches) | `65"` |

---

## How to Use a Custom Plugin

### Step 1: Create the YAML File

Save as `./my_plugins/fashion.yaml` (or any path).

### Step 2: Configure in TOML

```toml
[categories]
enabled = ["electronics", "home", "gaming", "media", "fashion"]
custom_paths = ["./my_plugins/fashion.yaml"]
```

> ⚠️ The YAML `plugin_id` must match the name in `enabled`.

### Step 3: Run

```bash
cug generate -c my_config.toml
```

### Step 4: Verify

```bash
cug categories
# Should show: Electronics, Home, Gaming, Media, Fashion

cug categories -l es
# Should show: Electrónica, Hogar, Gaming, Media, Moda y Ropa
```

---

## Example: Existing Category (Electronics)

The `cug/categories/builtin/electronics.yaml` file has:

- **5 subcategories**: Computers, Cell Phones, Audio, Cameras, TV & Video
- **8 languages**: en, es, pt, fr, de, zh, ja, ar
- **Realistic trends**: COVID WFH boom in Computers (1.65x in 2020), Camera drop (0.35x)
- **Templates with specs**: `{brand} {model} {spec}` → "Dell Laptop i7/32GB/1TB"

To create a custom plugin, use this file as reference:
`cug/categories/builtin/electronics.yaml`

---

## Important Notes

- **Uncovered trends** use linear interpolation or the nearest value
- **Products are generated**: 5-15 per subcategory (deterministic random)
- **Price** is randomly generated within `price_range`
- **Margin** is randomly generated within `margin_range`, determining `Cost` = `Price * (1 - margin)`
- If `brands` in a ProductTemplate is empty (`[]`), brands are inherited from the parent subcategory
