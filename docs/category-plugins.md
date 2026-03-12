# Guía de Plugins de Categorías (YAML)

> CUG usa archivos YAML para definir categorías de productos. Este sistema permite
> agregar categorías custom sin tocar código Python.

---

## Arquitectura del sistema

```
cug/categories/
├── base.py              ← Clases: CategoryPlugin, Subcategory, ProductTemplate
├── registry.py          ← CategoryRegistry: carga builtins + custom
└── builtin/
    ├── electronics.yaml ← Ejemplo canónico (5 subcategorías)
    ├── gaming.yaml
    ├── home.yaml
    └── media.yaml
```

### Flujo de carga

1. `CategoryRegistry` carga automáticamente los 4 builtins de `builtin/`
2. Si `[categories].custom_paths` tiene rutas, las carga con `load_custom()`
3. `CategoryPlugin.from_yaml(path)` parsea cada YAML → objetos Python
4. `generate_dim_product()` itera sobre todas las categorías del registry

---

## Schema YAML completo

```yaml
# ── Identificador único (snake_case, obligatorio) ────────────────────────
plugin_id: fashion

# ── Nombres por idioma (obligatorio al menos "en") ──────────────────────
display_names:
  en: Fashion & Apparel
  es: Moda y Ropa
  pt: Moda e Vestuário
  fr: Mode et Habillement
  de: Mode und Bekleidung
  zh: 时尚服饰
  ja: ファッション
  ar: أزياء

# ── Subcategorías (al menos 1 obligatoria) ──────────────────────────────
subcategories:

  - id: shoes                          # ID único snake_case
    display_names:                     # Nombres localizados
      en: Shoes
      es: Zapatos
      pt: Sapatos
    brands: [Nike, Adidas, Puma, New Balance, Reebok]  # Marcas disponibles
    price_range: [40.0, 350.0]         # [min, max] precio unitario USD
    margin_range: [0.15, 0.45]         # [min, max] margen de ganancia (0-1)
    trend:                             # Multiplicador de demanda por año
      2018: 0.85                       # 0.85 = 15% menos que baseline
      2019: 0.90
      2020: 0.60                       # COVID drop
      2021: 0.75
      2022: 1.00                       # baseline
      2023: 1.15
      2024: 1.20                       # 20% más que baseline
      2025: 1.25
      2026: 1.30
    products:                          # Templates para generar nombres
      - name_template: "{brand} {model} {spec}"
        models: [Air Max, Superstar, RS-X, Classic, Gel-Kayano]
        specs: [Size 8, Size 9, Size 10, Size 11, Size 12]
        brands: []                     # [] = usa brands de la subcategoría

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

## Referencia de campos

### Nivel raíz

| Campo | Tipo | Obligatorio | Descripción |
|-------|------|-------------|-------------|
| `plugin_id` | `string` | ✅ | Identificador único, snake_case. Ejemplo: `fashion` |
| `display_names` | `dict[str, str]` | ✅ | Mapa `idioma → nombre`. Mínimo: `en` |
| `subcategories` | `list` | ✅ | Al menos 1 subcategoría |

### Subcategoría

| Campo | Tipo | Obligatorio | Default | Descripción |
|-------|------|-------------|---------|-------------|
| `id` | `string` | ✅ | — | ID único snake_case |
| `display_names` | `dict[str, str]` | ❌ | `{en: id}` | Nombres localizados |
| `brands` | `list[str]` | ❌ | `[]` | Marcas disponibles |
| `price_range` | `[float, float]` | ❌ | `[99, 999]` | Rango de precio [min, max] |
| `margin_range` | `[float, float]` | ❌ | `[0.10, 0.30]` | Rango de margen [min, max] |
| `trend` | `dict[int, float]` | ❌ | `{}` | Multiplicador demanda por año |
| `products` | `list[ProductTemplate]` | ❌ | `[]` | Templates de nombre producto |

### ProductTemplate

| Campo | Tipo | Obligatorio | Default | Descripción |
|-------|------|-------------|---------|-------------|
| `name_template` | `string` | ❌ | `{brand} {model}` | Patrón de nombre con placeholders |
| `models` | `list[str]` | ❌ | `[]` | Variantes de modelo |
| `specs` | `list[str]` | ❌ | `[]` | Especificaciones técnicas |
| `brands` | `list[str]` | ❌ | Hereda sub | `[]` usa brands de subcategoría |

### Placeholders de `name_template`

| Placeholder | Fuente | Ejemplo |
|-------------|--------|---------|
| `{brand}` | `brands` de producto o subcategoría | `Nike` |
| `{model}` | `models` del template | `Air Max` |
| `{spec}` | `specs` del template | `256GB` |
| `{size}` | Aleatorio: 43, 55, 65, 75, 85 (pulgadas) | `65"` |

---

## Cómo usar un plugin custom

### Paso 1: Crear el archivo YAML

Guardar como `./my_plugins/fashion.yaml` (o cualquier ruta).

### Paso 2: Configurar en TOML

```toml
[categories]
enabled = ["electronics", "home", "gaming", "media", "fashion"]
custom_paths = ["./my_plugins/fashion.yaml"]
```

> ⚠️ El `plugin_id` del YAML debe coincidir con el nombre en `enabled`.

### Paso 3: Ejecutar

```bash
cug generate -c mi_config.toml
```

### Paso 4: Verificar

```bash
cug categories
# Debería mostrar: Electronics, Home, Gaming, Media, Fashion

cug categories -l es
# Debería mostrar: Electrónica, Hogar, Gaming, Media, Moda y Ropa
```

---

## Ejemplo: Categoría existente (Electronics)

El archivo `cug/categories/builtin/electronics.yaml` tiene:

- **5 subcategorías**: Computers, Cell Phones, Audio, Cameras, TV & Video
- **8 idiomas**: en, es, pt, fr, de, zh, ja, ar
- **Trends realistas**: COVID WFH boom en Computers (1.65x en 2020), caída en Cameras (0.35x)
- **Templates con specs**: `{brand} {model} {spec}` → "Dell Laptop i7/32GB/1TB"

Para crear un plugin custom, usa este archivo como referencia:
`cug/categories/builtin/electronics.yaml`

---

## Notas importantes

- Los **trends no cubiertos** usan interpolación lineal o el valor más cercano
- Los **productos se generan**: 5-15 por subcategoría (aleatorio determinístico)
- El **precio** se genera aleatoriamente dentro de `price_range`
- El **margen** se genera aleatoriamente dentro de `margin_range`, determinando `Cost` = `Price * (1 - margin)`
- Si `brands` en un ProductTemplate está vacío (`[]`), se heredan las brands de la subcategoría padre
