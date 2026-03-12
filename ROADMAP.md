# Roadmap: Contoso Universe Generator — Future Versions

> **Nota:** v0.2.0 fue lanzado con: multi-idioma (8 locales), 7 formatos output,
> YAML category plugins, SQL Server writer, validación FK, y CLI Rich.
> Las siguientes versiones representan evolución futura.

---

## v0.3 — Macro-Economic Calibration (Prophet + FRED)

### Problema que resuelve

El generador actual usa **reglas manuales** para simular tendencias macro (COVID,
inflación, seasonality). El resultado son datos con márgenes demasiado estables,
spikes irreales y crecimiento orgánico ausente.

### Arquitectura propuesta

```text
[FRED API]          [Prophet Model]       [CUG Engine]
US Retail Sales  →  fit + forecast    →   volume_index(month)
(RSXFS, monthly)    with real shocks      multiplies target_orders
```

#### Capa 1 — Macro calibrator (`macro_calibrator.py`)

- Descarga `RSXFS` (US Advance Retail Sales) desde FRED API (gratis)
- Ajusta un modelo **Facebook Prophet** sobre datos 2015-presente
- Genera un índice mensual normalizado `volume_index[month]`
  - Incluye automáticamente: seasonality real, COVID shock calibrado,
    inflación 2022, recuperación 2023-2024
- Exporta `macro_index.json`: `{"2020-03": 0.52, "2020-11": 1.34, ...}`

#### Capa 2 — Engine modificado

- En lugar de distribuir `target_orders` uniformemente,
  el engine lee `macro_index[current_month]` y ajusta el volumen diario
- Resultado: ~120k órdenes en meses normales, ~180k en Q4, ~85k en COVID lockdown
  — todo calibrado con datos reales

### Librerías necesarias

```bash
pip install prophet pandas-datareader fredapi
```

### Parámetros FRED útiles

| Código     | Descripción                      | Periodicidad |
| ---------- | -------------------------------- | ------------ |
| `RSXFS`    | Advance Retail Sales: Total      | Mensual      |
| `RSELXFSA` | Retail Sales ex-Food & Energy    | Mensual      |
| `ECOMSA`   | E-Commerce Retail Sales          | Trimestral   |
| `CPIAUCSL` | Consumer Price Index (inflación) | Mensual      |

### Mejoras adicionales posibles en v0.3

- **Margin noise realista**: COGS varía ±3-5% por trimestre (supply chain shocks)
- **Customer lifetime value**: distribución Pareto (20% clientes → 80% revenue)
- **Product mix shift**: Electronics gana share en COVID; Home en 2021; Gaming en 2023
- **Return rates**: varían por categoría (Electronics 8%, Clothing 20%, Gaming 5%)

### Impacto esperado vs. v0.2

| Métrica              | v0.2 (actual)     | v0.3 (objetivo)        |
| -------------------- | ----------------- | ---------------------- |
| COVID 2020 spike     | +57% (irreal)     | +12-15% (calibrado)    |
| Margin % variación   | ±0.6 pts / 8 años | ±2-4 pts (realista)    |
| Crecimiento orgánico | Plano             | +3-5% orden/año        |
| Seasonal Q4 lift     | +380% (hard-code) | +35-45% (datos reales) |

---

## v0.4 — Synthetic Data Vault (SDV) Integration

Si en el futuro se dispone de un dataset real (aunque sea parcial):

- `GaussianCopulaSynthesizer` para aprender distribuciones multivariadas
- `HMASynthesizer` para relaciones FK entre tablas (FactSales ↔ DimProduct)
- `CTGANSynthesizer` para columnas con distribuciones complejas (precios, cantidades)

### Referencia

- SDV docs: <https://docs.sdv.dev/sdv>
- TimeGAN paper: <https://arxiv.org/abs/1706.02633>
- Prophet: <https://facebook.github.io/prophet/>
- FRED API: <https://fred.stlouisfed.org/docs/api/fred/>
