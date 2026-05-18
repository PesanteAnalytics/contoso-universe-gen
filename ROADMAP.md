# Roadmap: Contoso Universe Generator — Future Versions

> **Note:** v0.2.0 was released with: multi-language (8 locales), 7 output formats,
> YAML category plugins, SQL Server writer, FK validation, and Rich CLI.
> The following versions represent future evolution.

---

## v0.3 — Macro-Economic Calibration (Prophet + FRED)

### Problem It Solves

The current generator uses **manual rules** to simulate macro trends (COVID,
inflation, seasonality). The result is data with overly stable margins,
unrealistic spikes, and absent organic growth.

### Proposed Architecture

```text
[FRED API]          [Prophet Model]       [CUG Engine]
US Retail Sales  →  fit + forecast    →   volume_index(month)
(RSXFS, monthly)    with real shocks      multiplies target_orders
```

#### Layer 1 — Macro calibrator (`macro_calibrator.py`)

- Downloads `RSXFS` (US Advance Retail Sales) from FRED API (free)
- Fits a **Facebook Prophet** model on 2015-present data
- Generates a normalized monthly index `volume_index[month]`
  - Automatically includes: real seasonality, calibrated COVID shock,
    2022 inflation, 2023-2024 recovery
- Exports `macro_index.json`: `{"2020-03": 0.52, "2020-11": 1.34, ...}`

#### Layer 2 — Modified Engine

- Instead of distributing `target_orders` uniformly,
  the engine reads `macro_index[current_month]` and adjusts daily volume
- Result: ~120k orders in normal months, ~180k in Q4, ~85k during COVID lockdown
  — all calibrated with real data

### Required Libraries

```bash
pip install prophet pandas-datareader fredapi
```

### Useful FRED Parameters

| Code       | Description                      | Frequency |
| ---------- | -------------------------------- | --------- |
| `RSXFS`    | Advance Retail Sales: Total      | Monthly   |
| `RSELXFSA` | Retail Sales ex-Food & Energy    | Monthly   |
| `ECOMSA`   | E-Commerce Retail Sales          | Quarterly |
| `CPIAUCSL` | Consumer Price Index (inflation) | Monthly   |

### Additional Improvements Possible in v0.3

- **Realistic margin noise**: COGS varies ±3-5% per quarter (supply chain shocks)
- **Customer lifetime value**: Pareto distribution (20% customers → 80% revenue)
- **Product mix shift**: Electronics gains share during COVID; Home in 2021; Gaming in 2023
- **Return rates**: vary by category (Electronics 8%, Clothing 20%, Gaming 5%)

### Expected Impact vs. v0.2

| Metric               | v0.2 (current)    | v0.3 (target)          |
| -------------------- | ----------------- | ---------------------- |
| COVID 2020 spike     | +57% (unrealistic)| +12-15% (calibrated)   |
| Margin % variation   | ±0.6 pts / 8 yrs  | ±2-4 pts (realistic)   |
| Organic growth       | Flat              | +3-5% orders/year      |
| Seasonal Q4 lift     | +380% (hard-code) | +35-45% (real data)    |

---

## v0.4 — Synthetic Data Vault (SDV) Integration

If a real dataset (even partial) becomes available in the future:

- `GaussianCopulaSynthesizer` to learn multivariate distributions
- `HMASynthesizer` for FK relationships between tables (FactSales ↔ DimProduct)
- `CTGANSynthesizer` for columns with complex distributions (prices, quantities)

### References

- SDV docs: <https://docs.sdv.dev/sdv>
- TimeGAN paper: <https://arxiv.org/abs/1706.02633>
- Prophet: <https://facebook.github.io/prophet/>
- FRED API: <https://fred.stlouisfed.org/docs/api/fred/>
