"""
Sales Generator — FactSales (the heart of the generator).
Schema aligned to Contoso Data Generator V2.

Architecture (VECTORIZED — no Python row loops):
  1. Pre-compute daily order volumes for all days using NumPy
  2. Expand dates using np.repeat()
  3. Assign all customers, products, stores in one vectorized np.random call
  4. Compute prices, discounts, margins with NumPy array ops
  5. Concat into Polars DataFrame at the very end

Grain: one row per ORDER LINE. An order (OrderKey) groups 1..n lines that
share customer, date, channel and store; LineNumber runs 1..n within it.
`customers.avg_lines_per_order = 1.0` collapses that back to one line per order.

V2-compatible output columns:
  OrderKey        : int
  LineNumber      : int
  OrderDate       : str   (YYYY-MM-DD)
  DeliveryDate    : str   (YYYY-MM-DD)
  CustomerKey     : int
  StoreKey        : int
  ProductKey      : int
  Channel         : str
  Quantity        : int
  UnitPrice       : float
  NetPrice        : float
  UnitCost        : float
  CurrencyCode    : str
  ExchangeRate    : float
"""

from __future__ import annotations

from datetime import date, timedelta

import numpy as np
import polars as pl

from ..config import INACTIVE_SEGMENT, AppConfig

# ─── Constants ───────────────────────────────────────────────────────────────

_ANNUAL_INFLATION = 0.04
_BASE_YEAR        = 2018
_ORGANIC_GROWTH   = 0.05

_CURRENCY_CODES: dict[str, str] = {
    "en": "USD",
    "es": "MXN",
    "de": "EUR",
    "fr": "EUR",
    "pt": "BRL",
    "zh": "CNY",
    "ja": "JPY",
}


# ─── Vectorized helpers ───────────────────────────────────────────────────────

def _inflation_factor(years_elapsed: np.ndarray) -> np.ndarray:
    return (1.0 + _ANNUAL_INFLATION) ** years_elapsed


def _growth_factor(years_elapsed: np.ndarray) -> np.ndarray:
    return (1.0 + _ORGANIC_GROWTH) ** years_elapsed


# ─── Main generator (fully vectorized) ───────────────────────────────────────

def generate_fact_sales(
    config: AppConfig,
    dim_date: pl.DataFrame,
    dim_customer: pl.DataFrame,
    dim_product: pl.DataFrame,
    dim_store: pl.DataFrame,
) -> pl.DataFrame:
    """
    Generate the FactSales table aligned to Contoso Data Generator V2.
    Uses fully vectorized NumPy operations — no Python row loops.
    """
    cfg      = config.general
    out_cfg  = config.output
    cust_cfg = config.customers

    rng = np.random.default_rng(cfg.seed)

    currency_code = _CURRENCY_CODES.get(cfg.language, "USD")

    start_dt = date.fromisoformat(cfg.start_date)
    end_dt   = date.fromisoformat(cfg.end_date)
    total_days = (end_dt - start_dt).days + 1

    # ── 1. Build per-day metadata arrays ─────────────────────────────────────
    all_dates    = [start_dt + timedelta(days=i) for i in range(total_days)]

    # Years-elapsed from base (float, for inflation/growth)
    years_elapsed = np.array(
        [(d.year - _BASE_YEAR) + (d.month - 1) / 12 for d in all_dates]
    )

    # Weekday index (0=Mon … 6=Sun)
    weekday_idx  = np.array([d.weekday() for d in all_dates])
    weekday_w    = np.array(config.weekday_factors.factors)
    wday_factors = weekday_w[weekday_idx]

    # Annual event factors (Black Friday, etc.)
    annual_events: dict[tuple[int, int], float] = {
        (e.month, e.day): e.factor for e in config.events.annual
    }
    annual_factors = np.array([
        annual_events.get((d.month, d.day), 1.0) for d in all_dates
    ])

    # One-time event factors
    one_time_global: dict[date, float] = {}
    for evt in config.events.one_time:
        d = date.fromisoformat(evt.date_start)
        end_d = date.fromisoformat(evt.date_end)
        while d <= end_d:
            one_time_global[d] = evt.factor
            d += timedelta(days=1)
    one_time_factors = np.array([one_time_global.get(d, 1.0) for d in all_dates])

    # Combined daily demand weight
    day_weights = wday_factors * annual_factors * one_time_factors

    # Growth factor per day
    growth = _growth_factor(years_elapsed)

    # ── 2. Compute daily order counts ────────────────────────────────────────
    target_orders = out_cfg.target_orders
    avg_daily     = target_orders / total_days

    # Expected orders per day: avg × weight × growth
    lambdas = avg_daily * day_weights * growth

    # Sample daily order counts based on expected volume
    if avg_daily < 1.0:
        # Low-volume mode: use Poisson to allow zero-order days
        # This ensures target_orders=100 → ~100 FactSales rows
        n_per_day = rng.poisson(lambdas).astype(np.int64)
    else:
        # Normal mode: Gaussian noise (~15% stddev) with min 1 order/day
        noise   = rng.normal(0, 1, size=total_days)
        n_per_day = np.maximum(1, np.round(lambdas + noise * lambdas * 0.15)).astype(np.int64)

    # -- 4. Order-level attributes --------------------------------------------
    # From here to step 9 everything is per ORDER. A real order is one customer,
    # one day, one channel, one store -- several product lines. Drawing those
    # once per order and expanding afterwards is what makes the basket coherent
    # instead of a pile of unrelated rows that happen to share an OrderKey.
    total_orders  = int(n_per_day.sum())
    order_day_idx = np.repeat(np.arange(total_days), n_per_day)

    # -- 5. Assign customers, weighted by segment ------------------------------
    # Uniform sampling would give every registered customer the same revenue,
    # which no retailer has ever seen. Each segment's demand_weight decides how
    # often one of its members shows up; dormant customers weigh 0 and never do.
    customer_keys = dim_customer["CustomerKey"].to_numpy()
    weight_map    = {seg.name: seg.demand_weight for seg in cust_cfg.segments}
    weight_map[INACTIVE_SEGMENT] = 0.0

    has_segments = "CustomerSegment" in dim_customer.columns

    def _per_customer(mapping: dict[str, float]) -> np.ndarray:
        """Map each customer's segment label onto its numeric behaviour."""
        if not has_segments:
            return np.ones(len(customer_keys))
        return (
            dim_customer
            .select(pl.col("CustomerSegment").replace_strict(mapping, default=1.0))
            .to_series()
            .cast(pl.Float64)
            .to_numpy()
        )

    if has_segments:
        cust_weights = (
            dim_customer
            .select(pl.col("CustomerSegment").replace_strict(weight_map, default=0.0))
            .to_series()
            .cast(pl.Float64)
            .to_numpy()
        )
    else:
        cust_weights = np.ones(len(customer_keys))

    if cust_weights.sum() <= 0:
        # Every customer came out dormant (possible with a tiny pool and a low
        # active_pct). Fall back to uniform rather than emitting zero orders.
        cust_weights = np.ones(len(customer_keys))
    cust_p = cust_weights / cust_weights.sum()

    order_cust_idx  = rng.choice(len(customer_keys), size=total_orders, p=cust_p)
    order_cust_keys = customer_keys[order_cust_idx].astype(np.int32)

    # Basket behaviour, read back from the same segment definition.
    lines_map = {seg.name: seg.lines_multiplier for seg in cust_cfg.segments}
    qty_map   = {seg.name: seg.quantity_multiplier for seg in cust_cfg.segments}
    lines_map[INACTIVE_SEGMENT] = 1.0
    qty_map[INACTIVE_SEGMENT]   = 1.0
    cust_lines_mult = _per_customer(lines_map)
    cust_qty_mult   = _per_customer(qty_map)

    # -- 6. Assign channels (online vs store), per order -----------------------
    # Linearly interpolate online_pct for each order's date
    start_d = date.fromisoformat(cfg.start_date)
    end_d   = date.fromisoformat(cfg.end_date)
    total_d = max((end_d - start_d).days, 1)
    elapsed_frac = np.array([(d - start_d).days / total_d for d in all_dates])
    online_pcts_per_day = (
        cust_cfg.online_pct_start
        + elapsed_frac * (cust_cfg.online_pct_end - cust_cfg.online_pct_start)
    )
    online_pcts     = online_pcts_per_day[order_day_idx]
    order_is_online = rng.random(size=total_orders) < online_pcts

    # -- 7. Assign stores, per order -------------------------------------------
    phys_stores  = dim_store.filter(pl.col("Status") == "Current")
    phys_keys    = phys_stores["StoreKey"].to_numpy()
    phys_weights = phys_stores["Weight"].to_numpy().astype(float)
    phys_w_norm  = phys_weights / phys_weights.sum()

    # Online orders -> StoreKey=1, physical -> weighted random
    n_phys   = int((~order_is_online).sum())
    phys_sel = rng.choice(phys_keys, size=n_phys, p=phys_w_norm)

    order_store_keys = np.ones(total_orders, dtype=np.int32)   # default = 1 (online)
    order_store_keys[~order_is_online] = phys_sel.astype(np.int32)

    # -- 8. Delivery offset, per order -----------------------------------------
    # Online: Poisson(lambda=4), capped 1-14; Physical: same day (0).
    # An order ships as one parcel, so the offset belongs to the order, not the line.
    order_offsets = np.zeros(total_orders, dtype=np.int32)
    n_online = int(order_is_online.sum())
    if n_online > 0:
        delivery_days = np.clip(rng.poisson(lam=4.0, size=n_online), 1, 14)
        order_offsets[order_is_online] = delivery_days

    # -- 9. Basket size -> expand orders into lines ----------------------------
    # Lines beyond the first are Poisson, scaled by the customer's segment: a
    # key account fills a bigger cart than a one-off shopper. With
    # avg_lines_per_order = 1.0 the lambda is zero and every order stays a
    # single line, which is the shape CUG produced before baskets existed.
    # The multipliers are relative, so they are normalised by their own
    # order-weighted mean before scaling. Without that, raising a segment's
    # basket size would quietly drag the whole table's average up and
    # `avg_lines_per_order` would stop being the number it claims to be.
    order_lines_mult = cust_lines_mult[order_cust_idx]
    order_lines_mult = order_lines_mult / max(order_lines_mult.mean(), 1e-9)
    extra_lam = max(cust_cfg.avg_lines_per_order - 1.0, 0.0) * order_lines_mult
    if extra_lam.max() > 0:
        n_lines = 1 + rng.poisson(extra_lam)
        n_lines = np.clip(n_lines, 1, cust_cfg.max_lines_per_order).astype(np.int64)
    else:
        n_lines = np.ones(total_orders, dtype=np.int64)

    total_rows    = int(n_lines.sum())
    row_order_idx = np.repeat(np.arange(total_orders), n_lines)

    # LineNumber = 1..n within each order
    line_starts = np.repeat(np.cumsum(n_lines) - n_lines, n_lines)
    line_number = (np.arange(total_rows) - line_starts + 1).astype(np.int32)

    # Expand the order-level draws down to line level
    day_idx             = order_day_idx[row_order_idx]
    order_customer_keys = order_cust_keys[row_order_idx]
    store_keys          = order_store_keys[row_order_idx]
    is_online           = order_is_online[row_order_idx]
    channels            = np.where(is_online, "Online", "Store")
    row_qty_mult        = cust_qty_mult[order_cust_idx][row_order_idx]

    # -- 10. Assign products (one draw per LINE) -------------------------------
    product_keys   = dim_product["ProductKey"].to_numpy()
    product_prices = dim_product["Price"].to_numpy(allow_copy=True).astype(float)
    product_costs  = dim_product["Cost"].to_numpy(allow_copy=True).astype(float)

    # Simple weight: 1/price (cheaper products sell more)
    prod_w = 1.0 / np.maximum(product_prices, 1.0)
    prod_w /= prod_w.sum()

    prod_indices     = rng.choice(len(product_keys), size=total_rows, p=prod_w)
    order_prod_keys  = product_keys[prod_indices].astype(np.int32)
    base_prices      = product_prices[prod_indices]
    base_costs       = product_costs[prod_indices]

    # -- 11. Apply inflation ---------------------------------------------------
    row_years_elapsed  = years_elapsed[day_idx]
    inflation          = _inflation_factor(row_years_elapsed)
    unit_prices        = np.round(base_prices * inflation, 2)
    unit_costs         = np.round(base_costs  * inflation, 2)

    # Quarterly COGS noise +/-4% (vectorized via per-quarter seed)
    quarters    = np.array([(d.year * 4 + (d.month - 1) // 3) for d in all_dates])
    row_quarters = quarters[day_idx]
    # Deterministic noise: hash quarter index -> small gaussian
    q_noise_seed = (row_quarters * 31337 + cfg.seed) & 0xFFFFFFFF
    q_rng        = np.random.default_rng(int(q_noise_seed.mean()))
    cogs_noise   = np.clip(q_rng.normal(0, 0.02, size=total_rows), -0.06, 0.06)
    # Cap the noisy cost just under the list price. Thin-margin subcategories
    # (gaming hardware starts at 2%) would otherwise be pushed past their own
    # price by the +6% tail of the noise, producing a unit sold at a loss.
    # Margin can be thin; it must not invert.
    unit_costs   = np.round(
        np.minimum(unit_costs * (1 + cogs_noise), unit_prices * 0.99), 2
    )

    # -- 12. Quantity: exponential-like, scaled by segment ----------------------
    raw_qty  = rng.exponential(scale=1.0 / 1.2, size=total_rows) * row_qty_mult
    quantity = np.clip(np.ceil(raw_qty), 1, 10).astype(np.int8)

    # -- 13. Discounts ---------------------------------------------------------
    months     = np.array([d.month for d in all_dates])
    days_of_m  = np.array([d.day   for d in all_dates])
    row_months = months[day_idx]
    row_day_m  = days_of_m[day_idx]

    is_seasonal = (
        ((row_months == 11) & (row_day_m >= 15)) |
        (row_months == 12)
    )

    roll = rng.random(size=total_rows)
    disc_pct = np.zeros(total_rows, dtype=float)

    # Normal discount tiers
    normal  = ~is_seasonal
    disc_pct = np.where(normal & (roll >= 0.60) & (roll < 0.80), 0.075,  disc_pct)
    disc_pct = np.where(normal & (roll >= 0.80) & (roll < 0.93), 0.20,   disc_pct)
    disc_pct = np.where(normal & (roll >= 0.93),                  0.35,   disc_pct)

    # Seasonal discount tiers
    disc_pct = np.where(is_seasonal & (roll >= 0.35) & (roll < 0.60), 0.125,  disc_pct)
    disc_pct = np.where(is_seasonal & (roll >= 0.60) & (roll < 0.85), 0.25,   disc_pct)
    disc_pct = np.where(is_seasonal & (roll >= 0.85),                  0.425,  disc_pct)

    discounts  = np.round(unit_prices * disc_pct, 2)
    net_prices = np.round(unit_prices - discounts, 2)

    # -- 14. Order / delivery dates as strings ---------------------------------
    base_epoch        = start_dt.toordinal()
    order_ordinals    = base_epoch + day_idx
    delivery_ordinals = order_ordinals + order_offsets[row_order_idx]
    max_ordinal       = end_dt.toordinal() + 14   # allow 14 days past end

    # Clamp delivery dates to end_dt + 14
    delivery_ordinals = np.minimum(delivery_ordinals, max_ordinal)

    # Vectorized ordinal -> date string via numpy datetime
    epoch = np.datetime64("0001-01-01")
    order_dates_np    = epoch + (order_ordinals    - 1).astype("timedelta64[D]")
    delivery_dates_np = epoch + (delivery_ordinals - 1).astype("timedelta64[D]")

    order_date_strs    = order_dates_np.astype("datetime64[D]").astype(str)
    delivery_date_strs = delivery_dates_np.astype("datetime64[D]").astype(str)

    # -- 15. Build Polars DataFrame --------------------------------------------
    order_keys = (row_order_idx + 1).astype(np.int64)

    df = pl.DataFrame({
        "OrderKey":     order_keys,
        "LineNumber":   line_number,
        "OrderDate":    order_date_strs.tolist(),
        "DeliveryDate": delivery_date_strs.tolist(),
        "CustomerKey":  order_customer_keys,
        "StoreKey":     store_keys,
        "ProductKey":   order_prod_keys,
        "Channel":      channels.tolist(),
        "Quantity":     quantity,
        "UnitPrice":    unit_prices,
        "NetPrice":     net_prices,
        "UnitCost":     unit_costs,
        "CurrencyCode": [currency_code] * total_rows,
        "ExchangeRate": np.ones(total_rows, dtype=np.float64),
    })

    return df
