"""
Store Generator — physical stores + online channel.
Schema aligned to Contoso Data Generator V2.
"""

from __future__ import annotations

import random

import polars as pl

from ..i18n.geography import _GEO_BY_LANG

# Physical stores to open, split across countries by their share of the market.
# The country list, the weights and the cities all come from the geography
# registry, so DimStore and DimCustomer can never disagree about where the
# business operates — they used to, and a German run put a store called
# "Contoso Witzenhausen" in the United States.
_TOTAL_PHYSICAL_STORES = 24

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
    rng = random.Random(seed)

    geo_list = _GEO_BY_LANG.get(language, _GEO_BY_LANG["en"])
    store_counts = _stores_per_country([g[2] for g in geo_list])
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

    for (country_code, country_name, weight, cities), n_stores in zip(geo_list, store_counts):
        geo_area_key += 1
        # Spread the country's stores over distinct cities before repeating one.
        city_order = _spread_over_cities(cities, n_stores, rng)

        for city_name, _, state_name, _, _ in city_order:
            open_year  = rng.randint(2000, 2017)
            open_date  = f"{open_year}-{rng.randint(1,12):02d}-{rng.randint(1,28):02d}"
            size_label = rng.choices(sizes, weights=size_weights)[0]
            sq_min, sq_max = _SQMT[size_label]
            sq_mt      = rng.randint(sq_min, sq_max)
            city       = city_name

            rows.append({
                "StoreKey":     store_key,
                "StoreCode":    store_key,
                "GeoAreaKey":   geo_area_key,
                "CountryCode":  country_code,
                "CountryName":  country_name,
                "State":        state_name,
                "OpenDate":     open_date,
                "CloseDate":    None,
                "Description":  f"Contoso {city} #{store_key}",
                "SquareMeters": sq_mt,
                "Status":       "Current",
                "Weight":       weight,  # used internally
            })
            store_key += 1

    return pl.DataFrame(rows)


def _stores_per_country(weights: list[float]) -> list[int]:
    """Split the store count across countries by market share, one each minimum.

    Largest-remainder, so the parts always add back up to the total instead of
    drifting with rounding.
    """
    total_weight = sum(weights)
    exact = [w / total_weight * _TOTAL_PHYSICAL_STORES for w in weights]
    counts = [max(1, int(e)) for e in exact]

    # Hand out what rounding left over, biggest fractional part first.
    leftover = _TOTAL_PHYSICAL_STORES - sum(counts)
    for i in sorted(range(len(exact)), key=lambda i: exact[i] - int(exact[i]), reverse=True):
        if leftover <= 0:
            break
        counts[i] += 1
        leftover -= 1
    return counts


def _spread_over_cities(cities: list, n_stores: int, rng: random.Random) -> list:
    """Pick n_stores cities, exhausting the distinct ones before repeating."""
    chosen: list = []
    while len(chosen) < n_stores:
        batch = list(cities)
        rng.shuffle(batch)
        chosen.extend(batch[: n_stores - len(chosen)])
    return chosen
