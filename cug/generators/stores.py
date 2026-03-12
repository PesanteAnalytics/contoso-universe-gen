"""
Store Generator — physical stores + online channel.
Schema aligned to Contoso Data Generator V2.
"""

from __future__ import annotations

import random

import polars as pl
from faker import Faker

from ..i18n import get_locale


_STORE_CONFIGS: dict[str, list[dict]] = {
    "en": [
        {"country": "US", "country_name": "United States",  "n_stores": 12, "weight": 0.55},
        {"country": "CA", "country_name": "Canada",         "n_stores": 3,  "weight": 0.12},
        {"country": "GB", "country_name": "United Kingdom", "n_stores": 4,  "weight": 0.12},
        {"country": "AU", "country_name": "Australia",      "n_stores": 2,  "weight": 0.08},
        {"country": "DE", "country_name": "Germany",        "n_stores": 2,  "weight": 0.07},
        {"country": "FR", "country_name": "France",         "n_stores": 2,  "weight": 0.06},
    ],
    "es": [
        {"country": "MX", "country_name": "México",         "n_stores": 8, "weight": 0.35},
        {"country": "CO", "country_name": "Colombia",       "n_stores": 4, "weight": 0.15},
        {"country": "AR", "country_name": "Argentina",      "n_stores": 3, "weight": 0.12},
        {"country": "ES", "country_name": "España",         "n_stores": 3, "weight": 0.12},
        {"country": "CL", "country_name": "Chile",          "n_stores": 2, "weight": 0.10},
        {"country": "PE", "country_name": "Perú",           "n_stores": 2, "weight": 0.08},
        {"country": "EC", "country_name": "Ecuador",        "n_stores": 2, "weight": 0.08},
    ],
}

# Square metres by store size (matches realistic retail footprints)
_SQMT: dict[str, tuple[int, int]] = {
    "Small":  (200,  800),
    "Medium": (800,  3000),
    "Large":  (3000, 10000),
}


def generate_dim_store(
    language: str = "en",
    seed: int = 42,
) -> pl.DataFrame:
    """
    Generate a Store table with schema aligned to Contoso Data Generator V2.

    V2-compatible columns:
      StoreKey     : int
      StoreCode    : int     (numeric store code, unique)
      GeoAreaKey   : int     (geography area foreign key)
      CountryCode  : str     (ISO 3166-1 alpha-2)
      CountryName  : str
      State        : str
      OpenDate     : date (YYYY-MM-DD)
      CloseDate    : date or None
      Description  : str     (store display name)
      SquareMeters : int
      Status       : str     (Online / Current / Closed)

    Internal-only column kept for sales generator (not written to output):
      Weight       : float   (sampling weight — dropped at output time if needed)
    """
    locale_info = get_locale(language)
    fake = Faker(locale_info.faker_locale)
    Faker.seed(seed)
    rng = random.Random(seed)

    store_configs = _STORE_CONFIGS.get(language, _STORE_CONFIGS["en"])
    sizes = ["Small", "Medium", "Large"]
    size_weights = [0.3, 0.5, 0.2]

    rows = []
    store_key = 1
    geo_area_key = 0   # incrementing geo area index

    # ── Online store (StoreKey = 1, special) ──────────────────────────────────
    rows.append({
        "StoreKey":     1,
        "StoreCode":    1,
        "GeoAreaKey":   0,
        "CountryCode":  "ONLINE",
        "CountryName":  "Online Channel",
        "State":        "",
        "OpenDate":     "2014-01-01",
        "CloseDate":    None,
        "Description":  "Online Store",
        "SquareMeters": 0,
        "Status":       "Online",
        "Weight":       1.0,      # used internally for sales generator
    })
    store_key = 2

    for config in store_configs:
        geo_area_key += 1
        for _ in range(config["n_stores"]):
            open_year  = rng.randint(2000, 2017)
            open_date  = f"{open_year}-{rng.randint(1,12):02d}-{rng.randint(1,28):02d}"
            size_label = rng.choices(sizes, weights=size_weights)[0]
            sq_min, sq_max = _SQMT[size_label]
            sq_mt      = rng.randint(sq_min, sq_max)
            city       = fake.city()

            rows.append({
                "StoreKey":     store_key,
                "StoreCode":    store_key,
                "GeoAreaKey":   geo_area_key,
                "CountryCode":  config["country"],
                "CountryName":  config["country_name"],
                "State":        fake.state() if hasattr(fake, "state") else "",
                "OpenDate":     open_date,
                "CloseDate":    None,
                "Description":  f"Contoso {city} #{store_key}",
                "SquareMeters": sq_mt,
                "Status":       "Current",
                "Weight":       config["weight"],  # used internally
            })
            store_key += 1

    return pl.DataFrame(rows)
