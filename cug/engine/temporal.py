"""
Temporal logic helpers — Poisson delivery dates, date utils.
"""

from __future__ import annotations

import math
import random
from datetime import date, timedelta


def poisson_days(lam: float, rng: random.Random, max_days: int = 30) -> int:
    """
    Sample the number of delivery days from a Poisson distribution.
    lam: average delivery days (lambda)
    min: 1 day, max: max_days
    """
    # Knuth algorithm for Poisson
    L = math.exp(-lam)
    k = 0
    p = 1.0
    while p > L:
        k += 1
        p *= rng.random()
    result = max(1, k - 1)
    return min(result, max_days)


def delivery_date(order_date: date, channel: str, rng: random.Random) -> date:
    """
    Calculate delivery date for an order.
    Physical store: same-day (no delivery).
    Online: Poisson-distributed 1-14 days.
    """
    if channel == "physical":
        return order_date

    # Online: avg 4 days delivery, lambda=4
    lam = 4.0
    days = poisson_days(lam, rng, max_days=14)
    return order_date + timedelta(days=days)


def date_range(start: date, end: date) -> list[date]:
    """Return a list of dates from start to end (inclusive)."""
    days = []
    current = start
    while current <= end:
        days.append(current)
        current += timedelta(days=1)
    return days


def chunk_date_ranges(start: date, end: date, chunk_size: int) -> list[tuple[date, date]]:
    """Split [start, end] into chunks of chunk_size days each."""
    chunks = []
    current = start
    while current <= end:
        chunk_end = min(current + timedelta(days=chunk_size - 1), end)
        chunks.append((current, chunk_end))
        current = chunk_end + timedelta(days=1)
    return chunks


def online_pct_for_date(d: date, start: date, end: date,
                         pct_start: float, pct_end: float) -> float:
    """
    Linearly interpolate the online channel percentage for a given date.
    Represents the growth of eCommerce over time.
    """
    total_days = (end - start).days
    if total_days == 0:
        return pct_start
    elapsed = (d - start).days
    t = elapsed / total_days
    return pct_start + t * (pct_end - pct_start)


# ── Aliases matching the call-sites in sales.py ──────────────────────────────

_ONLINE_START  = date(2014, 1, 1)
_ONLINE_END    = date(2030, 12, 31)


def interpolate_online_pct(d: date, pct_start: float, pct_end: float) -> float:
    """
    Convenience wrapper for online_pct_for_date.
    Uses the full eCommerce growth window (2014 → 2030).
    """
    return online_pct_for_date(d, _ONLINE_START, _ONLINE_END, pct_start, pct_end)


def poisson_delivery_days(is_online: bool, rng: random.Random) -> int:
    """
    Return the number of delivery days for an order.
    Physical: 0 days (in-store pickup).
    Online: Poisson(lambda=4), capped at 14.
    """
    if not is_online:
        return 0
    return poisson_days(lam=4.0, rng=rng, max_days=14)
