"""
Currency Exchange Generator — DimCurrencyExchange table.

Generates daily exchange rates between currency pairs, identical to
Contoso Data Generator V2's DimCurrencyExchange schema:
    Date          (String, ISO "YYYY-MM-DD")
    FromCurrency  (String, 3-letter ISO code)
    ToCurrency    (String, 3-letter ISO code)
    Exchange      (Float64, rate to convert 1 unit of FromCurrency → ToCurrency)

Logic:
  - Base currency is USD.
  - Each non-USD currency has a baseline rate and a small daily random walk.
  - All FromCurrency = "USD" per V2 convention (store prices are in USD,
    ExchangeRate in FactSales converts to local currency).
"""

from __future__ import annotations

import math
import random
from datetime import date, timedelta

import polars as pl

# ─── Reference rates vs USD ──────────────────────────────────────────────────
# Approximate mid-market rates (synthetic, realistic order of magnitude).
_BASE_RATES: dict[str, float] = {
    "EUR": 0.92,
    "GBP": 0.79,
    "CAD": 1.36,
    "AUD": 1.53,
    "MXN": 17.10,
    "BRL": 4.97,
    "ARS": 890.0,
    "COP": 3950.0,
    "CLP": 945.0,
    "JPY": 149.5,
    "CNY": 7.23,
    "INR": 83.1,
    "AED": 3.67,
    "SAR": 3.75,
    "CHF": 0.90,
    "SEK": 10.45,
    "NOK": 10.60,
    "DKK": 6.89,
    "PLN": 3.98,
    "KRW": 1325.0,
    "SGD": 1.34,
    "HKD": 7.82,
    "TRY": 30.8,
    "ZAR": 18.7,
}

# Annual volatility per currency (fraction of rate, used for daily random walk)
_VOLATILITY: dict[str, float] = {
    "EUR": 0.06, "GBP": 0.07, "CAD": 0.06, "AUD": 0.08,
    "MXN": 0.10, "BRL": 0.14, "ARS": 0.60, "COP": 0.12,
    "CLP": 0.10, "JPY": 0.08, "CNY": 0.03, "INR": 0.05,
    "AED": 0.01, "SAR": 0.01, "CHF": 0.05, "SEK": 0.08,
    "NOK": 0.09, "DKK": 0.04, "PLN": 0.09, "KRW": 0.08,
    "SGD": 0.04, "HKD": 0.01, "TRY": 0.35, "ZAR": 0.15,
}


def generate_dim_currency_exchange(
    start: date,
    end: date,
    seed: int = 42,
) -> pl.DataFrame:
    """
    Return daily USD→X exchange rates for every trading day in [start, end].

    Schema (V2-identical):
        Date          Utf8
        FromCurrency  Utf8
        ToCurrency    Utf8
        Exchange      Float64
    """
    rng = random.Random(seed)

    currencies = list(_BASE_RATES.keys())
    current_rates = {c: _BASE_RATES[c] for c in currencies}

    # Daily volatility = annual_vol / sqrt(252)
    daily_vol = {c: _VOLATILITY.get(c, 0.05) / math.sqrt(252) for c in currencies}

    rows: list[dict] = []
    current = start

    while current <= end:
        date_str = current.isoformat()

        for code in currencies:
            # Geometric Brownian Motion step
            drift = -0.5 * daily_vol[code] ** 2          # Itô correction
            shock = rng.gauss(0.0, 1.0) * daily_vol[code]
            current_rates[code] *= math.exp(drift + shock)

            # Floor: prevent degenerate values for high-inflation currencies
            current_rates[code] = max(current_rates[code], _BASE_RATES[code] * 0.05)

            rows.append({
                "Date":         date_str,
                "FromCurrency": "USD",
                "ToCurrency":   code,
                "Exchange":     round(current_rates[code], 6),
            })

        current += timedelta(days=1)

    return pl.DataFrame(rows, schema={
        "Date":         pl.String,
        "FromCurrency": pl.String,
        "ToCurrency":   pl.String,
        "Exchange":     pl.Float64,
    })
