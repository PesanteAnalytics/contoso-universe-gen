# Comparación de Esquemas — CUG vs Contoso Data Generator V2

> Fuentes: SQL scripts de V2 (`CreateTablesCommon.sql`, `CreateTablesSales.sql`, `CreateTablesOrders.sql`) y código fuente Python de CUG (`generators/*.py`, `models.py`)

---

## Resumen Ejecutivo

| Aspecto                    | V2                    | CUG                  |
| -------------------------- | --------------------- | -------------------- |
| **Tablas totales**         | 8 tablas              | 6 tablas             |
| **Tablas en común**        | 6                     | 6                    |
| **Tablas exclusivas**      | `Orders`, `OrderRows` | —                    |
| **Compatibilidad total**   | ❌ No directa         | —                    |
| **Compatibilidad parcial** | ✅ Sí (con mapeo)     | —                    |
| **Tecnología**             | .NET 8 / C#           | Python / Polars      |
| **Formato de salida**      | CSV, Parquet, Delta   | CSV, Parquet, DuckDB |

---

## 📅 Tabla: Date / Calendar

| Columna V2          | Columna CUG         | Estado      |
| ------------------- | ------------------- | ----------- |
| `Date`              | `Date`              | ✅ Igual    |
| `DateKey`           | `DateKey`           | ✅ Igual    |
| `Year`              | `Year`              | ✅ Igual    |
| `YearQuarter`       | `YearQuarter`       | ✅ Igual    |
| `YearQuarterNumber` | `YearQuarterNumber` | ✅ Igual    |
| `Quarter`           | `Quarter`           | ✅ Igual    |
| `YearMonth`         | `YearMonth`         | ✅ Igual    |
| `YearMonthShort`    | `YearMonthShort`    | ✅ Igual    |
| `YearMonthNumber`   | `YearMonthNumber`   | ✅ Igual    |
| `Month`             | `Month`             | ✅ Igual    |
| `MonthShort`        | `MonthShort`        | ✅ Igual    |
| `MonthNumber`       | `MonthNumber`       | ✅ Igual    |
| `DayofWeek`         | `DayofWeek`         | ✅ Igual    |
| `DayofWeekShort`    | `DayofWeekShort`    | ✅ Igual    |
| `DayofWeekNumber`   | `DayofWeekNumber`   | ✅ Igual    |
| `WorkingDay`        | `WorkingDay`        | ✅ Igual    |
| `WorkingDayNumber`  | `WorkingDayNumber`  | ✅ Igual    |
| —                   | `FiscalYear`        | 🆕 Solo CUG |
| —                   | `FiscalQuarter`     | 🆕 Solo CUG |
| —                   | `IsHoliday`         | 🆕 Solo CUG |
| —                   | `Season`            | 🆕 Solo CUG |
| —                   | `WeekdayFactor`     | 🆕 Solo CUG |

**Veredicto:** ✅ **Compatible** — CUG contiene todas las columnas de V2 más 5 columnas adicionales.

---

## 👤 Tabla: Customer

| Columna V2      | Columna CUG       | Estado        |
| --------------- | ----------------- | ------------- |
| `CustomerKey`   | `CustomerKey`     | ✅ Igual      |
| `GeoAreaKey`    | —                 | ⚠️ Solo V2    |
| `StartDT`       | —                 | ⚠️ Solo V2    |
| `EndDT`         | —                 | ⚠️ Solo V2    |
| `Continent`     | `Continent`       | ✅ Igual      |
| `Gender`        | `Gender`          | ✅ Igual      |
| `Title`         | —                 | ⚠️ Solo V2    |
| `GivenName`     | `FirstName`       | 🔄 Renombrado |
| `MiddleInitial` | —                 | ⚠️ Solo V2    |
| `Surname`       | `LastName`        | 🔄 Renombrado |
| `StreetAddress` | `Address`         | 🔄 Renombrado |
| `City`          | `City`            | ✅ Igual      |
| `State`         | `StateCode`       | 🔄 Renombrado |
| `StateFull`     | `State`           | 🔄 Renombrado |
| `ZipCode`       | `ZipCode`         | ✅ Igual      |
| `Country`       | `CountryCode`     | 🔄 Renombrado |
| `CountryFull`   | `Country`         | 🔄 Renombrado |
| `Birthday`      | `BirthDate`       | 🔄 Renombrado |
| `Age`           | `Age`             | ✅ Igual      |
| `Occupation`    | —                 | ⚠️ Solo V2    |
| `Company`       | —                 | ⚠️ Solo V2    |
| `Vehicle`       | —                 | ⚠️ Solo V2    |
| `Latitude`      | `Latitude`        | ✅ Igual      |
| `Longitude`     | `Longitude`       | ✅ Igual      |
| —               | `Email`           | 🆕 Solo CUG   |
| —               | `AnnualIncome`    | 🆕 Solo CUG   |
| —               | `CustomerSegment` | 🆕 Solo CUG   |

**Veredicto:** 🔄 **Parcialmente compatible** — Misma semántica pero nombres diferentes. V2 tiene 5 columnas de metadata de persona que CUG no genera. CUG añade 3 columnas (Email, Income, Segment).

---

## 📦 Tabla: Product

| Columna V2        | Columna CUG       | Estado                                     |
| ----------------- | ----------------- | ------------------------------------------ |
| `ProductKey`      | `ProductKey`      | ✅ Igual                                   |
| `ProductCode`     | —                 | ⚠️ Solo V2                                 |
| `ProductName`     | `ProductName`     | ✅ Igual                                   |
| `Manufacturer`    | —                 | ⚠️ Solo V2                                 |
| `Brand`           | `Brand`           | ✅ Igual                                   |
| `Color`           | —                 | ⚠️ Solo V2                                 |
| `WeightUnit`      | —                 | ⚠️ Solo V2                                 |
| `Weight`          | —                 | ⚠️ Solo V2                                 |
| `Cost`            | `UnitCost`        | 🔄 Renombrado                              |
| `Price`           | `UnitPrice`       | 🔄 Renombrado                              |
| `CategoryKey`     | `CategoryID`      | 🔄 Renombrado (tipo diferente: int vs str) |
| `CategoryName`    | `CategoryName`    | ✅ Igual                                   |
| `SubCategoryKey`  | `SubcategoryID`   | 🔄 Renombrado (tipo diferente: int vs str) |
| `SubCategoryName` | `SubcategoryName` | ✅ Igual                                   |
| —                 | `Margin`          | 🆕 Solo CUG                                |

**Veredicto:** ⚠️ **Compatible parcial** — V2 tiene más atributos físicos del producto (Color, Weight, Manufacturer). CUG usa IDs de texto en lugar de numéricos para categorías.

---

## 🏪 Tabla: Store

| Columna V2     | Columna CUG    | Estado                              |
| -------------- | -------------- | ----------------------------------- |
| `StoreKey`     | `StoreKey`     | ✅ Igual                            |
| `StoreCode`    | —              | ⚠️ Solo V2                          |
| `GeoAreaKey`   | —              | ⚠️ Solo V2                          |
| `CountryCode`  | `CountryCode`  | ✅ Igual                            |
| `CountryName`  | `Country`      | 🔄 Renombrado                       |
| `State`        | `State`        | ✅ Igual                            |
| `OpenDate`     | `OpenDate`     | ✅ Igual                            |
| `CloseDate`    | `CloseDate`    | ✅ Igual                            |
| `Description`  | `StoreName`    | 🔄 Renombrado                       |
| `SquareMeters` | `SquareMeters` | ✅ Igual                            |
| `Status`       | `StoreType`    | 🔄 Renombrado (semántica diferente) |
| —              | `City`         | 🆕 Solo CUG                         |
| —              | `Region`       | 🆕 Solo CUG                         |
| —              | `IsOnline`     | 🆕 Solo CUG                         |

**Veredicto:** ✅ **Mayormente compatible** — El núcleo es el mismo. CUG enriquece con City, Region e IsOnline.

---

## 💱 Tabla: CurrencyExchange

| Columna V2     | Columna CUG    | Estado        |
| -------------- | -------------- | ------------- |
| `Date`         | `Date`         | ✅ Igual      |
| `FromCurrency` | `FromCurrency` | ✅ Igual      |
| `ToCurrency`   | `ToCurrency`   | ✅ Igual      |
| `Exchange`     | `ExchangeRate` | 🔄 Renombrado |

**Veredicto:** ✅ **Compatible** — Misma estructura, solo `Exchange` → `ExchangeRate`.

---

## 💰 Tabla: Sales (Fact)

| Columna V2     | Columna CUG    | Estado   |
| -------------- | -------------- | -------- |
| `OrderKey`     | `OrderKey`     | ✅ Igual |
| `LineNumber`   | `LineNumber`   | ✅ Igual |
| `OrderDate`    | `OrderDate`    | ✅ Igual |
| `DeliveryDate` | `DeliveryDate` | ✅ Igual |
| `CustomerKey`  | `CustomerKey`  | ✅ Igual |
| `StoreKey`     | `StoreKey`     | ✅ Igual |
| `ProductKey`   | `ProductKey`   | ✅ Igual |
| `Quantity`     | `Quantity`     | ✅ Igual |
| `UnitPrice`    | `UnitPrice`    | ✅ Igual |
| `NetPrice`     | `NetPrice`     | ✅ Igual |
| `UnitCost`     | `UnitCost`     | ✅ Igual |
| `CurrencyCode` | `CurrencyCode` | ✅ Igual |
| `ExchangeRate` | `ExchangeRate` | ✅ Igual |

**Veredicto:** ✅ **100% Compatible** — Todas las columnas son idénticas en nombre y semántica.

---

## 📋 Tabla: Orders (Solo V2)

> **V2 únicamente.** CUG no separa Orders de Sales.

| Columna V2     | CUG        | Estado     |
| -------------- | ---------- | ---------- |
| `OrderKey`     | (en Sales) | ⚠️ Solo V2 |
| `CustomerKey`  | (en Sales) | ⚠️ Solo V2 |
| `StoreKey`     | (en Sales) | ⚠️ Solo V2 |
| `OrderDate`    | (en Sales) | ⚠️ Solo V2 |
| `DeliveryDate` | (en Sales) | ⚠️ Solo V2 |
| `CurrencyCode` | (en Sales) | ⚠️ Solo V2 |

---

## 📋 Tabla: OrderRows (Solo V2)

> **V2 únicamente.** CUG consolida todo en una tabla Sales desnormalizada.

| Columna V2   | CUG        | Estado     |
| ------------ | ---------- | ---------- |
| `OrderKey`   | (en Sales) | ⚠️ Solo V2 |
| `LineNumber` | (en Sales) | ⚠️ Solo V2 |
| `ProductKey` | (en Sales) | ⚠️ Solo V2 |
| `Quantity`   | (en Sales) | ⚠️ Solo V2 |
| `UnitPrice`  | (en Sales) | ⚠️ Solo V2 |
| `NetPrice`   | (en Sales) | ⚠️ Solo V2 |
| `UnitCost`   | (en Sales) | ⚠️ Solo V2 |

---

## Resumen de Compatibilidad por Tabla

| Tabla                | Compatibilidad              | Notas                                                     |
| -------------------- | --------------------------- | --------------------------------------------------------- |
| **Date**             | ✅ Alta (100% + extras CUG) | CUG añade FiscalYear, Season, etc.                        |
| **CurrencyExchange** | ✅ Alta (solo renombrado)   | `Exchange` → `ExchangeRate`                               |
| **Sales**            | ✅ Total (100%)             | Columnas idénticas                                        |
| **Store**            | 🔄 Media-Alta               | Núcleo compatible, CUG añade City/Region/IsOnline         |
| **Product**          | 🔄 Media                    | V2 tiene Color/Weight/Manufacturer, CUG usa IDs string    |
| **Customer**         | 🔄 Media                    | Mismo concepto, nombres diferentes, V2 tiene más metadata |
| **Orders**           | ❌ Solo V2                  | Datos redundantes con Sales en CUG                        |
| **OrderRows**        | ❌ Solo V2                  | Datos redundantes con Sales en CUG                        |

---

## ¿Son compatibles para Power BI?

**Sí, con ajustes mínimos.** Si ya tienes un modelo de Power BI construido sobre V2 y quieres migrar a CUG:

1. **Sales** → Conéctalo directamente sin cambios.
2. **Date** → Usar sin cambios (CUG tiene más columnas, no menos).
3. **CurrencyExchange** → Renombrar `ExchangeRate` → `Exchange` en Power Query.
4. **Store** → El núcleo es compatible, revisar si usas `Description` vs `StoreName`.
5. **Product** → Revisar campos de `CategoryKey`/`SubCategoryKey` si son int en las relaciones.
6. **Customer** → Actualizar referencias de nombre de columna (`GivenName` → `FirstName`, etc.).
7. **Orders/OrderRows** → No existe en CUG; si los necesitas, crear vistas derivadas de Sales.
