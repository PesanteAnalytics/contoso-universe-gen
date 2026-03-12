"""
Data models shared across orchestrator and writers to avoid circular imports.
"""

from __future__ import annotations

import polars as pl


class GenerationResult:
    """Container for all generated DataFrames."""

    def __init__(self):
        self.dim_date:              pl.DataFrame | None = None
        self.dim_customer:          pl.DataFrame | None = None
        self.dim_product:           pl.DataFrame | None = None
        self.dim_store:             pl.DataFrame | None = None
        self.dim_currency:          pl.DataFrame | None = None
        self.dim_currency_exchange: pl.DataFrame | None = None
        self.fact_sales:            pl.DataFrame | None = None

    def summary(self) -> dict[str, int]:
        return {
            "DimDate":             len(self.dim_date)              if self.dim_date is not None else 0,
            "DimCustomer":         len(self.dim_customer)          if self.dim_customer is not None else 0,
            "DimProduct":          len(self.dim_product)           if self.dim_product is not None else 0,
            "DimStore":            len(self.dim_store)             if self.dim_store is not None else 0,
            "DimCurrency":         len(self.dim_currency)          if self.dim_currency is not None else 0,
            "DimCurrencyExchange": len(self.dim_currency_exchange) if self.dim_currency_exchange is not None else 0,
            "FactSales":           len(self.fact_sales)            if self.fact_sales is not None else 0,
        }
