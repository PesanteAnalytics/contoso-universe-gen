# Referencia de Internacionalización (i18n)

> Esta guía explica exactamente qué cambia y qué NO cambia cuando se selecciona
> un idioma en CUG.

---

## Idiomas soportados

| Código | Idioma | Faker Locale | País Default | Moneda Principal |
|--------|--------|-------------|-------------|-----------------|
| `en` | English | `en_US` | US | USD |
| `es` | Español | `es_MX` | MX | MXN |
| `pt` | Português | `pt_BR` | BR | BRL |
| `fr` | Français | `fr_FR` | FR | EUR |
| `de` | Deutsch | `de_DE` | DE | EUR |
| `zh` | 中文 | `zh_CN` | CN | CNY |
| `ja` | 日本語 | `ja_JP` | JP | JPY |
| `ar` | العربية | `ar_AA` | SA | AED |

---

## ✅ Qué SÍ se traduce (valores dentro de columnas)

### DimDate — Nombres de meses y días

| Columna | `en` | `es` | `pt` | `fr` | `de` |
|---------|------|------|------|------|------|
| `MonthName` | January | Enero | Janeiro | Janvier | Januar |
| `MonthNameShort` | Jan | Ene | Jan | Jan | Jan |
| `DayName` | Monday | Lunes | Segunda | Lundi | Montag |
| `DayNameShort` | Mon | Lun | Seg | Lun | Mon |

> **Nota**: `zh`, `ja`, `ar` no tienen nombres de mes/día en el mapeo actual.
> El sistema aplica fallback a inglés para estos idiomas.

### DimDate — Festivos

Los festivos se cargan automáticamente según el **country** configurado,
usando la librería `holidays`:

| Language | Country Default | Ejemplo Festivo |
|----------|----------------|-----------------|
| `en` | US | Independence Day (Jul 4) |
| `es` | MX | Día de la Independencia (Sep 16) |
| `pt` | BR | Independência do Brasil (Sep 7) |
| `fr` | FR | Fête Nationale (Jul 14) |
| `de` | DE | Tag der Deutschen Einheit (Oct 3) |

### DimProduct — Nombres de categoría y subcategoría

| Columna | `en` | `es` | `pt` |
|---------|------|------|------|
| `CategoryName` | Electronics | Electrónica | Eletrônicos |
| `SubCategoryName` | Computers | Computadoras | Computadores |
| `CategoryName` | Home | Hogar | Casa e Decoração |
| `SubCategoryName` | Cell Phones | Teléfonos Móviles | Celulares |

> Los nombres provienen de `display_names` en cada archivo YAML de categoría.
> Si un idioma no tiene traducción en el YAML, se usa fallback a inglés.

### DimCustomer — Geografía y ciudades

| Componente | `en` | `es` | `pt` |
|-----------|------|------|------|
| Ciudades | New York, LA, Chicago... | CDMX, Guadalajara, Bogotá... | São Paulo, Rio, Curitiba... |
| Países | US, CA, GB, AU | MX, CO, AR, ES, CL, PE, EC | BR, PT |
| Distribución | US 55%, CA 12%... | MX 35%, CO 15%... | BR 80%, PT 20% |

### DimStore — Países y tiendas

| Componente | `en` | `es` |
|-----------|------|------|
| Países | US (12), CA (3), GB (4)... | MX (8), CO (4), AR (3)... |
| Nombres ciudad | Faker locale cities | Faker locale cities |

### DimCurrency — Moneda primaria

| Language | Moneda usada en FactSales |
|----------|--------------------------|
| `en` | USD (CurrencyKey = 1) |
| `es` | MXN (CurrencyKey = 6) |
| `pt` | BRL (CurrencyKey = 7) |
| `fr` | EUR (CurrencyKey = 2) |
| `de` | EUR (CurrencyKey = 2) |
| `zh` | CNY (CurrencyKey = 12) |
| `ja` | JPY (CurrencyKey = 11) |
| `ar` | AED (CurrencyKey = 14) |

> `DimCurrency` siempre contiene las 25 monedas del catálogo.
> El `language` solo afecta cuál se usa como **moneda principal** en `FactSales`.

---

## ❌ Qué NO se traduce

### Headers de columna (SIEMPRE en inglés)

Los nombres de las columnas del DataFrame **nunca cambian**, independientemente
del idioma:

| Tabla | Columna (siempre) | NO será |
|-------|-------------------|---------|
| DimProduct | `ProductKey` | ~~`ClaveProducto`~~ |
| DimProduct | `ProductName` | ~~`NombreProducto`~~ |
| DimProduct | `CategoryName` | ~~`NombreCategoria`~~ |
| FactSales | `OrderDate` | ~~`FechaPedido`~~ |
| FactSales | `UnitPrice` | ~~`PrecioUnitario`~~ |
| DimCustomer | `CustomerKey` | ~~`ClaveCliente`~~ |
| DimDate | `MonthName` | ~~`NombreMes`~~ |

> ⚠️ **Esta es una limitación actual**. La localización de headers está planeada
> como feature opt-in en una versión futura (ver ROADMAP).

### Nombres de producto (parcialmente en inglés)

Los **nombres de producto** se generan desde los templates de cada YAML:
- Las **marcas** siempre están en inglés: `Apple`, `Samsung`, `Dell`
- Los **modelos y specs** están en inglés: `Laptop i7/32GB`, `OLED 4K UHD`
- Solo `CategoryName` y `SubCategoryName` se traducen

Ejemplo con `language: es`:
```
ProductName:     "Dell Laptop i7/32GB/1TB"      ← inglés
CategoryName:    "Electrónica"                   ← español ✅
SubCategoryName: "Computadoras"                  ← español ✅
```

### Otros valores que NO cambian

| Elemento | Valor | Razón |
|----------|-------|-------|
| `ProductCode` | `PROD-00001` | Formato fijo |
| `Manufacturer` | `Contoso Ltd.` | Nombres de empresa globales |
| `Color` | `Black`, `White`... | Lista estática en inglés |
| `WeightUnit` | `lb`, `kg`... | Unidades estándar |
| `CurrencyCode` | `USD`, `MXN`... | Códigos ISO |
| `CurrencyName` | `US Dollar`... | Nombres en inglés |
| `Status` (Store) | `Online`, `Current` | Enum fijo |
| `Gender` | `M`, `F`, `Other` | Códigos fijos |

---

## Tabla resumen de impacto por idioma

```
╔══════════════════════════╦══════╦══════╦══════════════════════════╗
║ Componente               ║ i18n ║ Tipo ║ Detalle                  ║
╠══════════════════════════╬══════╬══════╬══════════════════════════╣
║ MonthName / DayName      ║  ✅  ║ Dato ║ Solo en/es/pt/fr/de      ║
║ CategoryName             ║  ✅  ║ Dato ║ Según YAML display_names ║
║ SubCategoryName          ║  ✅  ║ Dato ║ Según YAML display_names ║
║ Ciudades (Customer)      ║  ✅  ║ Dato ║ Pool diferente por lang  ║
║ Países (Customer/Store)  ║  ✅  ║ Dato ║ Distribución por lang    ║
║ Moneda principal (Sales) ║  ✅  ║ FK   ║ USD→MXN→BRL→EUR...       ║
║ Festivos (Calendar)      ║  ✅  ║ Dato ║ Según country config     ║
║ Headers de columna       ║  ❌  ║  —   ║ Siempre en inglés        ║
║ ProductName              ║  ❌  ║  —   ║ Templates en inglés      ║
║ Manufacturer / Brand     ║  ❌  ║  —   ║ Nombres globales         ║
║ Color / WeightUnit       ║  ❌  ║  —   ║ Lista estática inglés    ║
║ CurrencyCode/Name        ║  ❌  ║  —   ║ Catálogo ISO fijo        ║
╚══════════════════════════╩══════╩══════╩══════════════════════════╝
```

---

## Consideraciones para Power BI

1. **Headers en inglés** = compatibilidad directa con modelos Power BI existentes
2. **Valores traducidos** = los slicers mostrarán "Electrónica" en vez de "Electronics"
3. **Moneda local** = los valores monetarios usan la moneda del idioma seleccionado
4. **Festivos locales** = las columnas `IsHoliday` y `HolidayName` reflejan el país correcto
