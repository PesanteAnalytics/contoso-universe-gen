"""
Product Generator — builds Product table aligned to Contoso Data Generator V2 schema.
"""

from __future__ import annotations

import random

import polars as pl

from ..categories import CategoryRegistry

# Static lists for V2-compatible attributes
_COLORS = [
    "Black", "White", "Silver", "Gray", "Blue", "Red", "Green", "Brown",
    "Yellow", "Orange", "Purple", "Pink", "Gold", "Beige", "Multicolor",
]

_WEIGHT_UNITS = ["lb", "kg", "oz", "g"]

_MANUFACTURERS = [
    "Contoso Ltd.", "Adventure Works", "Fabrikam Inc.", "Northwind Traders",
    "Litware Inc.", "Proseware Inc.", "A. Datum Corporation",
    "Wide World Importers", "Southridge Video", "The Phone Company",
    "Tailspin Toys", "Blue Yonder Airlines",
]


def generate_dim_product(
    registry: CategoryRegistry,
    language: str = "en",
    seed: int = 42,
) -> pl.DataFrame:
    """
    Generate a Product table with schema aligned to Contoso Data Generator V2.

    V2-compatible columns:
      ProductKey      : int (sequential)
      ProductCode     : str (e.g. "PROD-00001")
      ProductName     : str
      Manufacturer    : str
      Brand           : str
      Color           : str
      WeightUnit      : str
      Weight          : float
      Cost            : float   (was UnitCost)
      Price           : float   (was UnitPrice)
      CategoryKey     : int     (was CategoryID as str)
      CategoryName    : str
      SubCategoryKey  : int     (was SubcategoryID as str)
      SubCategoryName : str
    """
    rng = random.Random(seed)

    # Build a deterministic int key for each unique category / subcategory ID
    cat_key_map: dict[str, int] = {}
    sub_key_map: dict[str, int] = {}
    cat_counter = 1
    sub_counter = 1

    # First pass to populate key maps
    for plugin in registry.all():
        if plugin.plugin_id not in cat_key_map:
            cat_key_map[plugin.plugin_id] = cat_counter
            cat_counter += 1
        for sub in plugin.subcategories:
            if sub.id not in sub_key_map:
                sub_key_map[sub.id] = sub_counter
                sub_counter += 1

    rows = []
    product_key = 1

    for plugin in registry.all():
        cat_name = plugin.display_name(language)
        cat_key  = cat_key_map[plugin.plugin_id]

        for sub in plugin.subcategories:
            sub_name = sub.display_names.get(language) or sub.display_names.get("en", sub.id)
            sub_key  = sub_key_map[sub.id]

            # Generate 5-15 products per subcategory
            n_products = rng.randint(5, 15)
            for _ in range(n_products):
                brand = rng.choice(sub.brands) if sub.brands else "Generic"
                price = round(rng.uniform(*sub.price_range), 2)
                margin = round(rng.uniform(*sub.margin_range), 4)
                cost = round(price * (1 - margin), 2)

                # Build product name from templates if available
                if sub.products:
                    template = rng.choice(sub.products)
                    model = rng.choice(template.models) if template.models else ""
                    spec  = rng.choice(template.specs) if template.specs else ""
                    b     = rng.choice(template.brands) if template.brands else brand
                    name  = template.name_template
                    name  = name.replace("{brand}", b).replace("{model}", model)
                    name  = name.replace("{spec}", spec).replace("{size}", f'{rng.choice([43,55,65,75,85])}"')
                    name  = " ".join(name.split())  # normalize spaces
                else:
                    name = f"{brand} {sub_name} #{product_key}"

                rows.append({
                    "ProductKey":      product_key,
                    "ProductCode":     f"PROD-{product_key:05d}",
                    "ProductName":     name,
                    "Manufacturer":    rng.choice(_MANUFACTURERS),
                    "Brand":           brand,
                    "Color":           rng.choice(_COLORS),
                    "WeightUnit":      rng.choice(_WEIGHT_UNITS),
                    "Weight":          round(rng.uniform(0.1, 50.0), 2),
                    "Cost":            cost,
                    "Price":           price,
                    "CategoryKey":     cat_key,
                    "CategoryName":    cat_name,
                    "SubCategoryKey":  sub_key,
                    "SubCategoryName": sub_name,
                })
                product_key += 1

    return pl.DataFrame(rows)
