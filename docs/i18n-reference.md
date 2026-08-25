# Internationalization (i18n) Reference

> This guide explains exactly what changes and what does NOT change when
> selecting a language in CUG.

---

## Supported Languages

| Code | Language | Locale Tag | Default Country | Primary Currency |
|------|----------|-------------|-----------------|-----------------|
| `en` | English | `en_US` | US | USD |
| `es` | Español | `es_MX` | MX | MXN |
| `pt` | Português | `pt_BR` | BR | BRL |
| `fr` | Français | `fr_FR` | FR | EUR |
| `de` | Deutsch | `de_DE` | DE | EUR |
| `zh` | 中文 | `zh_CN` | CN | CNY |
| `ja` | 日本語 | `ja_JP` | JP | JPY |
| `ar` | العربية | `ar_AA` | SA | AED |

---

## ✅ What IS Translated (values within columns)

### DimDate — Month and Day Names

| Column | `en` | `es` | `pt` | `fr` | `de` |
|--------|------|------|------|------|------|
| `MonthName` | January | Enero | Janeiro | Janvier | Januar |
| `MonthNameShort` | Jan | Ene | Jan | Jan | Jan |
| `DayName` | Monday | Lunes | Segunda | Lundi | Montag |
| `DayNameShort` | Mon | Lun | Seg | Lun | Mon |

> **Note**: `zh`, `ja`, `ar` don't have month/day name mappings in the current version.
> The system falls back to English for these languages.

### DimDate — Holidays

Holidays are automatically loaded based on the configured **country**,
using the `holidays` library:

| Language | Default Country | Holiday Example |
|----------|----------------|-----------------|
| `en` | US | Independence Day (Jul 4) |
| `es` | MX | Día de la Independencia (Sep 16) |
| `pt` | BR | Independência do Brasil (Sep 7) |
| `fr` | FR | Fête Nationale (Jul 14) |
| `de` | DE | Tag der Deutschen Einheit (Oct 3) |

### DimProduct — Category and Subcategory Names

| Column | `en` | `es` | `pt` |
|--------|------|------|------|
| `CategoryName` | Electronics | Electrónica | Eletrônicos |
| `SubCategoryName` | Computers | Computadoras | Computadores |
| `CategoryName` | Home | Hogar | Casa e Decoração |
| `SubCategoryName` | Cell Phones | Teléfonos Móviles | Celulares |

> Names come from `display_names` in each category YAML file.
> If a language doesn't have a translation in the YAML, English is used as fallback.

### DimCustomer — Geography and Cities

| Component | `en` | `es` | `pt` |
|-----------|------|------|------|
| Cities | New York, LA, Chicago... | CDMX, Guadalajara, Bogotá... | São Paulo, Rio, Curitiba... |
| Countries | US, CA, GB, AU | MX, CO, AR, ES, CL, PE, EC | BR, PT |
| Distribution | US 55%, CA 12%... | MX 35%, CO 15%... | BR 80%, PT 20% |

### DimStore — Countries and Stores

Stores read the same geography registry as customers, so the two tables always
agree on which countries the business operates in and which cities exist there.

| Component | `en` | `es` | `pt` |
|-----------|------|------|------|
| Countries | US, CA, GB, AU, DE, FR | MX, CO, AR, ES, CL, PE, EC | BR, PT |
| Store count | 24 physical + 1 online, split by market share |  |  |
| City names | Drawn from the country's own city list |  |  |

> ⚠️ **Fallback**: only `en`, `es` and `pt` have their own geography. Every other
> language uses the `en` layout for both stores and customers, while still
> translating the product catalogue. See the coverage table in the README.

### DimCurrency — Primary Currency

| Language | Currency Used in FactSales |
|----------|---------------------------|
| `en` | USD (CurrencyKey = 1) |
| `es` | MXN (CurrencyKey = 6) |
| `pt` | BRL (CurrencyKey = 7) |
| `fr` | EUR (CurrencyKey = 2) |
| `de` | EUR (CurrencyKey = 2) |
| `zh` | CNY (CurrencyKey = 12) |
| `ja` | JPY (CurrencyKey = 11) |
| `ar` | AED (CurrencyKey = 14) |

> `DimCurrency` always contains all 25 currencies in the catalog.
> The `language` only affects which one is used as the **primary currency** in `FactSales`.

---

## ❌ What is NOT Translated

### Column Headers (ALWAYS in English)

DataFrame column names **never change**, regardless of the language:

| Table | Column (always) | Will NOT be |
|-------|-----------------|-------------|
| DimProduct | `ProductKey` | ~~`ClaveProducto`~~ |
| DimProduct | `ProductName` | ~~`NombreProducto`~~ |
| DimProduct | `CategoryName` | ~~`NombreCategoria`~~ |
| FactSales | `OrderDate` | ~~`FechaPedido`~~ |
| FactSales | `UnitPrice` | ~~`PrecioUnitario`~~ |
| DimCustomer | `CustomerKey` | ~~`ClaveCliente`~~ |
| DimDate | `MonthName` | ~~`NombreMes`~~ |

> ⚠️ **This is a current limitation**. Header localization is planned
> as an opt-in feature in a future version (see ROADMAP).

### Product Names (partially in English)

**Product names** are generated from templates in each YAML:
- **Brands** are always in English: `Apple`, `Samsung`, `Dell`
- **Models and specs** are in English: `Laptop i7/32GB`, `OLED 4K UHD`
- Only `CategoryName` and `SubCategoryName` are translated

Example with `language: es`:
```
ProductName:     "Dell Laptop i7/32GB/1TB"      ← English
CategoryName:    "Electrónica"                   ← Spanish ✅
SubCategoryName: "Computadoras"                  ← Spanish ✅
```

### Other Values That Do NOT Change

| Element | Value | Reason |
|---------|-------|--------|
| `ProductCode` | `PROD-00001` | Fixed format |
| `Manufacturer` | `Contoso Ltd.` | Global company names |
| `Color` | `Black`, `White`... | Static English list |
| `WeightUnit` | `lb`, `kg`... | Standard units |
| `CurrencyCode` | `USD`, `MXN`... | ISO codes |
| `CurrencyName` | `US Dollar`... | English names |
| `Status` (Store) | `Online`, `Current` | Fixed enum |
| `Gender` | `M`, `F`, `Other` | Fixed codes |

---

## Language Impact Summary Table

```
╔══════════════════════════╦══════╦══════╦══════════════════════════╗
║ Component                ║ i18n ║ Type ║ Detail                   ║
╠══════════════════════════╬══════╬══════╬══════════════════════════╣
║ MonthName / DayName      ║  ✅  ║ Data ║ Only en/es/pt/fr/de      ║
║ CategoryName             ║  ✅  ║ Data ║ Per YAML display_names   ║
║ SubCategoryName          ║  ✅  ║ Data ║ Per YAML display_names   ║
║ Cities (Customer)        ║  ✅  ║ Data ║ Different pool per lang  ║
║ Countries (Customer/Store)║ ✅  ║ Data ║ Distribution per lang    ║
║ Primary Currency (Sales) ║  ✅  ║ FK   ║ USD→MXN→BRL→EUR...       ║
║ Holidays (Calendar)      ║  ✅  ║ Data ║ Per country config       ║
║ Column Headers           ║  ❌  ║  —   ║ Always in English        ║
║ ProductName              ║  ❌  ║  —   ║ English templates        ║
║ Manufacturer / Brand     ║  ❌  ║  —   ║ Global names             ║
║ Color / WeightUnit       ║  ❌  ║  —   ║ Static English list      ║
║ CurrencyCode/Name        ║  ❌  ║  —   ║ Fixed ISO catalog        ║
╚══════════════════════════╩══════╩══════╩══════════════════════════╝
```

---

## Power BI Considerations

1. **English headers** = direct compatibility with existing Power BI models
2. **Translated values** = slicers will show "Electrónica" instead of "Electronics"
3. **Local currency** = monetary values use the selected language's currency
4. **Local holidays** = the `IsHoliday` and `HolidayName` columns reflect the correct country
