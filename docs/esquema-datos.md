# Esquema de Datos

> Las 7 tablas generadas por CUG, sus columnas, tipos de datos y relaciones de clave foránea.

---

## Modelo de Datos (Star Schema)

CUG genera un esquema estrella clásico con **1 tabla de hechos** y **6 tablas de dimensiones**.

```
                         ┌─────────────────┐
                         │    DimDate       │
                         │  (DateKey PK)    │
                         └────────┬─────────┘
                                  │ OrderDateKey, DeliveryDateKey
                                  │
┌──────────────────┐     ┌────────┴─────────┐     ┌──────────────────┐
│   DimCustomer    │     │                  │     │   DimProduct     │
│ (CustomerKey PK) │─────│    FactSales     │─────│ (ProductKey PK)  │
└──────────────────┘     │                  │     └──────────────────┘
                         └────────┬─────────┘
                                  │
                         ┌────────┴─────────┐
                         │    DimStore       │
                         │  (StoreKey PK)    │
                         └────────┬─────────┘
                                  │
                         ┌────────┴─────────┐
                         │   DimCurrency     │
                         │ (CurrencyKey PK)  │
                         └────────┬─────────┘
                                  │
                         ┌────────┴──────────────┐
                         │  DimCurrencyExchange   │
                         │ (CurrencyCode+Date PK) │
                         └────────────────────────┘
```

---

## Tablas de Dimensión

### `DimDate` — Calendario

Calendario completo que cubre todo el rango temporal configurado (por defecto: 2018-01-01 a 2026-12-31).

| Columna | Tipo | Descripción |
|---------|------|-------------|
| `DateKey` | `Int32` | Clave primaria (formato `YYYYMMDD`, e.g. `20240115`) |
| `Date` | `Date` | Fecha completa |
| `Year` | `Int16` | Año (e.g. `2024`) |
| `Quarter` | `Int8` | Trimestre (1–4) |
| `Month` | `Int8` | Mes (1–12) |
| `MonthName` | `String` | Nombre del mes (localizado según idioma) |
| `Day` | `Int8` | Día del mes (1–31) |
| `DayOfWeek` | `Int8` | Día de la semana (0=Lun ... 6=Dom) |
| `DayName` | `String` | Nombre del día (localizado) |
| `WeekOfYear` | `Int8` | Semana del año (1–53) |
| `IsWeekend` | `Boolean` | Sábado o domingo |
| `IsHoliday` | `Boolean` | Día festivo del país configurado |

---

### `DimCustomer` — Clientes

Pool de clientes sintéticos generados con Faker.

| Columna | Tipo | Descripción |
|---------|------|-------------|
| `CustomerKey` | `Int32` | Clave primaria |
| `CustomerName` | `String` | Nombre completo (localizado) |
| `Gender` | `String` | Género |
| `City` | `String` | Ciudad (localizada) |
| `StateProvince` | `String` | Estado / Provincia |
| `Country` | `String` | País |
| `Continent` | `String` | Continente |
| `EmailAddress` | `String` | Dirección de email |
| `Birthday` | `Date` | Fecha de nacimiento |

> [!NOTE]
> El `pool_size` en la configuración controla cuántos clientes únicos se generan. Solo el `active_pct` de ellos tendrán al menos una compra.

---

### `DimProduct` — Productos

Catálogo de productos organizado por categoría y subcategoría.

| Columna | Tipo | Descripción |
|---------|------|-------------|
| `ProductKey` | `Int32` | Clave primaria |
| `ProductName` | `String` | Nombre del producto (localizado) |
| `Category` | `String` | Categoría principal (e.g. Electronics, Home) |
| `Subcategory` | `String` | Subcategoría (e.g. Laptops, Headphones) |
| `Brand` | `String` | Marca del producto |
| `UnitPrice` | `Float64` | Precio unitario en USD |
| `UnitCost` | `Float64` | Costo unitario en USD |
| `Weight` | `Float64` | Peso del producto |

---

### `DimStore` — Tiendas

Tiendas físicas y canal online.

| Columna | Tipo | Descripción |
|---------|------|-------------|
| `StoreKey` | `Int32` | Clave primaria |
| `StoreName` | `String` | Nombre de la tienda |
| `StoreType` | `String` | Tipo: `Physical` u `Online` |
| `City` | `String` | Ciudad de la tienda |
| `StateProvince` | `String` | Estado / Provincia |
| `Country` | `String` | País |
| `SquareMeters` | `Int32` | Metros cuadrados (solo tiendas físicas) |
| `OpenDate` | `Date` | Fecha de apertura |

---

### `DimCurrency` — Monedas

Monedas soportadas en el dataset.

| Columna | Tipo | Descripción |
|---------|------|-------------|
| `CurrencyKey` | `Int32` | Clave primaria |
| `CurrencyCode` | `String` | Código ISO 4217 (e.g. `USD`, `EUR`) |
| `CurrencyName` | `String` | Nombre de la moneda |

---

### `DimCurrencyExchange` — Tasas de Cambio

Tasas de cambio diarias contra USD.

| Columna | Tipo | Descripción |
|---------|------|-------------|
| `CurrencyCode` | `String` | Código de moneda (FK → DimCurrency) |
| `Date` | `Date` | Fecha de la tasa |
| `ExchangeRate` | `Float64` | Tasa de cambio (1 USD = X unidades) |

---

## Tabla de Hechos

### `FactSales` — Ventas

La tabla principal de hechos. Cada fila representa una línea de orden de venta.

| Columna | Tipo | Descripción |
|---------|------|-------------|
| `OrderKey` | `Int64` | Identificador único de la orden |
| `OrderLineKey` | `Int32` | Número de línea dentro de la orden |
| `OrderDateKey` | `Int32` | FK → DimDate (fecha de la orden) |
| `DeliveryDateKey` | `Int32` | FK → DimDate (fecha de entrega) |
| `CustomerKey` | `Int32` | FK → DimCustomer |
| `ProductKey` | `Int32` | FK → DimProduct |
| `StoreKey` | `Int32` | FK → DimStore |
| `CurrencyKey` | `Int32` | FK → DimCurrency |
| `Quantity` | `Int16` | Cantidad comprada |
| `UnitPrice` | `Float64` | Precio unitario al momento de la venta |
| `TotalAmount` | `Float64` | Monto total (Quantity × UnitPrice) |
| `DiscountAmount` | `Float64` | Descuento aplicado |
| `IsOnline` | `Boolean` | `true` si la compra fue online |

---

## Relaciones de Clave Foránea (FK)

| FK en FactSales | → Dimensión | Clave |
|-----------------|-------------|-------|
| `OrderDateKey` | `DimDate` | `DateKey` |
| `DeliveryDateKey` | `DimDate` | `DateKey` |
| `CustomerKey` | `DimCustomer` | `CustomerKey` |
| `ProductKey` | `DimProduct` | `ProductKey` |
| `StoreKey` | `DimStore` | `StoreKey` |
| `CurrencyKey` | `DimCurrency` | `CurrencyKey` |

---

## Validación de Integridad

CUG puede validar la integridad referencial **en memoria** antes de escribir. Para activar esta validación:

```toml
[output]
integrity_check  = true    # Activar validación
integrity_strict = true    # Abortar en violaciones (o false para solo reportar)
```

O desde la línea de comandos:

```bash
cug generate --strict       # Valida y aborta en errores
cug generate --no-strict    # Valida e informa, pero continúa
```

---

## Volumen de Datos Aproximado

El `target_orders` controla el número de órdenes generadas. Aquí una guía del volumen total:

| target_orders | FactSales (filas aprox.) | DimCustomer | Tamaño Parquet aprox. |
|--------------|------------------------|--------------|-----------------------|
| 5,000 | ~8K–12K | ~15K | ~2 MB |
| 100,000 | ~160K–240K | ~50K | ~30 MB |
| 1,000,000 | ~1.6M–2.4M | ~50K | ~250 MB |
| 10,000,000 | ~16M–24M | ~50K | ~2.5 GB |

> [!NOTE]
> `FactSales` tiene más filas que órdenes porque cada orden puede tener múltiples líneas (productos).

---

← [Formatos de Salida](formatos-salida.md) | [SQL Server →](sqlserver.md)
