"""
Customer segmentation and multi-line orders.

Two properties this file defends, both invisible in a row count:

  1. Revenue is *concentrated*. A uniform draw over the customer pool gives
     every customer the same expected spend, which is not a shape any retailer
     has ever reported. The segments turn that into a Pareto head.
  2. An order is *coherent*. Its lines share customer, date, channel and store,
     because that is what a receipt looks like.
"""

from __future__ import annotations

import polars as pl
import pytest

from cug.config import INACTIVE_SEGMENT, AppConfig
from cug.generators.customers import generate_dim_customer
from cug.orchestrator import run_generation

# ── Config validation ────────────────────────────────────────────────────────

def test_segment_shares_must_sum_to_one():
    """A base that adds to 90% would silently leave a tenth of it unclassified."""
    with pytest.raises(ValueError, match="must sum to 1.0"):
        AppConfig.model_validate({
            "customers": {"segments": [
                {"name": "Big",   "share": 0.10, "demand_weight": 10.0},
                {"name": "Small", "share": 0.80, "demand_weight": 1.0},
            ]}
        })


def test_duplicate_segment_names_rejected():
    """Names are the join key between DimCustomer and the sales weights."""
    with pytest.raises(ValueError, match="Duplicate segment names"):
        AppConfig.model_validate({
            "customers": {"segments": [
                {"name": "Big", "share": 0.5, "demand_weight": 10.0},
                {"name": "Big", "share": 0.5, "demand_weight": 1.0},
            ]}
        })


def test_default_segments_are_pareto_shaped():
    """The top fifth of the active base should carry the clear majority of demand."""
    segs = AppConfig().customers.segments
    total = sum(s.share * s.demand_weight for s in segs)
    head = sum(s.share * s.demand_weight for s in segs if s.share <= 0.20)
    assert head / total > 0.65, f"head carries only {head / total:.0%} of demand"


# ── DimCustomer ──────────────────────────────────────────────────────────────

def test_dim_customer_carries_segment_column():
    df = generate_dim_customer(pool_size=20_000, seed=42, active_pct=0.30)
    assert "CustomerSegment" in df.columns

    counts = dict(df["CustomerSegment"].value_counts().iter_rows())
    assert set(counts) == {INACTIVE_SEGMENT, "Key Account", "Large", "Medium", "Small"}

    # ~70% dormant, within sampling noise
    assert 0.66 < counts[INACTIVE_SEGMENT] / len(df) < 0.74

    active = len(df) - counts[INACTIVE_SEGMENT]
    assert 0.75 < counts["Small"] / active < 0.85       # configured 0.80
    assert 0.005 < counts["Key Account"] / active < 0.02  # configured 0.01


def test_active_pct_actually_does_something():
    """It was a config field nothing read; a 10%/90% split must now be visible."""
    lo = generate_dim_customer(pool_size=10_000, seed=7, active_pct=0.10)
    hi = generate_dim_customer(pool_size=10_000, seed=7, active_pct=0.90)
    def dormant(df):
        return (df["CustomerSegment"] == INACTIVE_SEGMENT).sum()

    assert dormant(lo) > dormant(hi) * 5


# ── FactSales ────────────────────────────────────────────────────────────────

@pytest.fixture(scope="module")
def generated(tmp_path_factory):
    """One 8k-order run with baskets on, reused by the fact-table tests."""
    cfg = AppConfig()
    cfg.general.start_date = "2023-01-01"
    cfg.general.end_date   = "2024-12-31"
    cfg.output.target_orders = 8_000
    cfg.output.formats = []          # nothing to write; the frames are enough
    cfg.output.output_path = str(tmp_path_factory.mktemp("seg"))
    cfg.customers.pool_size = 20_000
    cfg.customers.avg_lines_per_order = 2.6
    return run_generation(config=cfg)


def test_dormant_customers_never_place_an_order(generated):
    dormant = generated.dim_customer.filter(
        pl.col("CustomerSegment") == INACTIVE_SEGMENT
    ).select("CustomerKey")
    hits = generated.fact_sales.join(dormant, on="CustomerKey", how="semi")
    assert len(hits) == 0, f"{len(hits)} orders from customers marked dormant"


def test_revenue_is_concentrated_in_the_head(generated):
    """Per-customer spend must rise monotonically with the segment tier."""
    joined = (
        generated.fact_sales
        .join(generated.dim_customer.select("CustomerKey", "CustomerSegment"),
              on="CustomerKey")
        .with_columns((pl.col("NetPrice") * pl.col("Quantity")).alias("Revenue"))
    )
    per_customer = (
        joined.group_by("CustomerSegment")
        .agg((pl.col("Revenue").sum() / pl.col("CustomerKey").n_unique()).alias("avg"))
    )
    avg = dict(per_customer.iter_rows())
    assert avg["Key Account"] > avg["Large"] > avg["Medium"] > avg["Small"]
    assert avg["Key Account"] > avg["Small"] * 10


def test_orders_have_multiple_coherent_lines(generated):
    f = generated.fact_sales
    n_orders = f["OrderKey"].n_unique()
    assert len(f) > n_orders * 1.5, "baskets requested but every order is one line"

    # Everything that belongs to the order, not the line, is constant within it.
    varying = (
        f.group_by("OrderKey")
        .agg([pl.col(c).n_unique().alias(c)
              for c in ("CustomerKey", "OrderDate", "Channel", "StoreKey", "DeliveryDate")])
        .filter(pl.any_horizontal(
            pl.col("CustomerKey") > 1, pl.col("OrderDate") > 1, pl.col("Channel") > 1,
            pl.col("StoreKey") > 1, pl.col("DeliveryDate") > 1,
        ))
    )
    assert len(varying) == 0, f"{len(varying)} orders mix customers/dates/stores"


def test_line_numbers_run_one_to_n(generated):
    f = generated.fact_sales
    per_order = f.group_by("OrderKey").agg(
        pl.len().alias("lines"),
        pl.col("LineNumber").min().alias("lo"),
        pl.col("LineNumber").max().alias("hi"),
        pl.col("LineNumber").n_unique().alias("distinct"),
    )
    assert per_order.filter(pl.col("lo") != 1).height == 0
    assert per_order.filter(pl.col("hi") != pl.col("lines")).height == 0
    assert per_order.filter(pl.col("distinct") != pl.col("lines")).height == 0


def test_nobody_buys_before_they_are_a_customer(generated):
    early = (
        generated.fact_sales
        .join(generated.dim_customer.select("CustomerKey", "StartDT"), on="CustomerKey")
        .filter(pl.col("OrderDate") < pl.col("StartDT"))
    )
    assert len(early) == 0, f"{len(early)} orders predate the customer's StartDT"


def test_single_line_mode_is_still_available(tmp_path):
    """avg_lines_per_order = 1.0 reproduces the pre-basket fact shape."""
    cfg = AppConfig()
    cfg.general.start_date = "2024-01-01"
    cfg.general.end_date   = "2024-06-30"
    cfg.output.target_orders = 2_000
    cfg.output.formats = []
    cfg.output.output_path = str(tmp_path)
    cfg.customers.pool_size = 5_000
    cfg.customers.avg_lines_per_order = 1.0

    f = run_generation(config=cfg).fact_sales
    assert f["OrderKey"].n_unique() == len(f)
    assert f["LineNumber"].max() == 1
