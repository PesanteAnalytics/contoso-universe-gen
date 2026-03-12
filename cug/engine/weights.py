"""
Weights Engine — temporal weight interpolation using Polars.

Provides WeightEngine: a class that computes:
  - daily_weight(date)       : overall volume multiplier
  - category_weights(date)   : per-category multiplier dict
"""

from __future__ import annotations

import math
from datetime import date, timedelta

import polars as pl

from ..config import AppConfig


# ---------------------------------------------------------------------------
# Low-level helpers
# ---------------------------------------------------------------------------

def interpolate(anchor_points: dict[int, float], years: list[int]) -> dict[int, float]:
    """
    Linear interpolation between year anchor points.
    anchor_points: {year: weight} — sparse, e.g. {2018: 0.85, 2020: 1.65}
    """
    if not anchor_points:
        return {y: 1.0 for y in years}

    sorted_anchors = sorted(anchor_points.items())
    result: dict[int, float] = {}

    for year in years:
        before = [(y, w) for y, w in sorted_anchors if y <= year]
        after  = [(y, w) for y, w in sorted_anchors if y  > year]

        if before and after:
            y0, w0 = before[-1]
            y1, w1 = after[0]
            t = (year - y0) / (y1 - y0)
            result[year] = w0 + t * (w1 - w0)
        elif before:
            result[year] = before[-1][1]
        elif after:
            result[year] = after[0][1]
        else:
            result[year] = 1.0

    return result


# ---------------------------------------------------------------------------
# WeightEngine class
# ---------------------------------------------------------------------------

class WeightEngine:
    """
    Pre-computes and caches daily + category weights for the entire date range.
    """

    def __init__(self, config: AppConfig) -> None:
        self._config = config
        self._start = date.fromisoformat(config.general.start_date)
        self._end   = date.fromisoformat(config.general.end_date)

        self._weekday_factors: list[float] = config.weekday_factors.factors

        # Annual events: (month, day) -> factor
        self._annual_events: dict[tuple[int, int], float] = {
            (e.month, e.day): e.factor
            for e in config.events.annual
        }

        # One-time global: date -> factor
        self._one_time_global: dict[date, float] = {}
        # One-time per-category: date -> {cat_id: factor}
        self._one_time_category: dict[date, dict[str, float]] = {}

        for evt in config.events.one_time:
            d = date.fromisoformat(evt.date_start)
            end_d = date.fromisoformat(evt.date_end)
            while d <= end_d:
                self._one_time_global[d] = evt.factor
                if evt.categories:
                    self._one_time_category[d] = evt.categories
                d += timedelta(days=1)

    def daily_weight(self, d: date) -> float:
        """
        Return the overall multiplier for a given date.
        Combines weekday factor × annual event × one-time event.
        """
        wday   = d.weekday()  # 0=Mon, 6=Sun
        base   = self._weekday_factors[wday]
        factor = self._annual_events.get((d.month, d.day), 1.0)
        global_factor = self._one_time_global.get(d, 1.0)
        return base * factor * global_factor

    def category_weights(self, d: date) -> dict[str, float]:
        """
        Return per-category weight multipliers for a given date.
        Returns an empty dict if no category-specific overrides are defined.
        """
        return self._one_time_category.get(d, {})


# ---------------------------------------------------------------------------
# Standalone function kept for backwards compat
# ---------------------------------------------------------------------------

def build_daily_weights(
    config: AppConfig,
    category_trends: dict[str, dict[int, float]],
) -> pl.DataFrame:
    """
    Build a Polars DataFrame with one row per day in [start_date, end_date].
    Columns: date, base_weight, {category_id...}
    """
    start = date.fromisoformat(config.general.start_date)
    end   = date.fromisoformat(config.general.end_date)

    days: list[date] = []
    current = start
    while current <= end:
        days.append(current)
        current += timedelta(days=1)

    years = sorted({d.year for d in days})
    wf    = config.weekday_factors.factors

    annual_events: dict[tuple[int, int], float] = {
        (e.month, e.day): e.factor for e in config.events.annual
    }

    one_time_global: dict[date, float] = {}
    one_time_category: dict[date, dict[str, float]] = {}
    for evt in config.events.one_time:
        d = date.fromisoformat(evt.date_start)
        end_d = date.fromisoformat(evt.date_end)
        while d <= end_d:
            one_time_global[d] = evt.factor
            if evt.categories:
                one_time_category[d] = evt.categories
            d += timedelta(days=1)

    cat_yearly: dict[str, dict[int, float]] = {
        cat_id: interpolate(anchors, years)
        for cat_id, anchors in category_trends.items()
    }

    rows = []
    for d in days:
        wday = d.weekday()
        base = wf[wday]
        base *= annual_events.get((d.month, d.day), 1.0)
        base *= one_time_global.get(d, 1.0)

        row: dict = {"date": d, "base_weight": base}
        one_time_cats = one_time_category.get(d, {})
        for cat_id, yearly in cat_yearly.items():
            row[cat_id] = yearly.get(d.year, 1.0) * one_time_cats.get(cat_id, 1.0)
        rows.append(row)

    return pl.DataFrame(rows)
