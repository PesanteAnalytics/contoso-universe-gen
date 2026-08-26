"""
Geography registry — the single source of truth for where the business operates.

Both DimCustomer and DimStore read this table, so a customer and a store in the
same country always agree on which cities and subdivisions exist there.
"""

from __future__ import annotations

# ─── Geography ───────────────────────────────────────────────────────────────
# Cities hang off the country they belong to, so a customer's City, State,
# Country and coordinates always describe one real place. Each city carries its
# ISO 3166-2 subdivision code, the subdivision name, and its approximate centre.
#
# Coverage: only en, es and pt have their own geography. Every other language
# falls back to `en` here — see the language coverage table in the README.

# (city, state_code, state_full, latitude, longitude)
_City = tuple[str, str, str, float, float]

# language -> [(country_code, country_full, weight, cities)]
_GEO_BY_LANG: dict[str, list[tuple[str, str, float, list[_City]]]] = {
    "es": [
        ("MX", "México", 0.35, [
            ("Ciudad de México", "CMX", "Ciudad de México",  19.43,  -99.13),
            ("Guadalajara",      "JAL", "Jalisco",           20.67, -103.35),
            ("Monterrey",        "NLE", "Nuevo León",        25.69, -100.32),
            ("Puebla",           "PUE", "Puebla",            19.04,  -98.20),
            ("Tijuana",          "BCN", "Baja California",   32.51, -117.04),
            ("León",             "GUA", "Guanajuato",        21.12, -101.68),
            ("Ciudad Juárez",    "CHH", "Chihuahua",         31.74, -106.49),
            ("Mérida",           "YUC", "Yucatán",           20.97,  -89.62),
            ("Cancún",           "ROO", "Quintana Roo",      21.16,  -86.85),
            ("Querétaro",        "QUE", "Querétaro",         20.59, -100.39),
        ]),
        ("CO", "Colombia", 0.15, [
            ("Bogotá",       "DC",  "Bogotá D.C.",       4.71, -74.07),
            ("Medellín",     "ANT", "Antioquia",         6.24, -75.58),
            ("Cali",         "VAC", "Valle del Cauca",   3.44, -76.52),
            ("Barranquilla", "ATL", "Atlántico",        10.97, -74.80),
        ]),
        ("AR", "Argentina", 0.12, [
            ("Buenos Aires", "C", "Ciudad Autónoma de Buenos Aires", -34.60, -58.38),
            ("Córdoba",      "X", "Córdoba",                         -31.42, -64.18),
            ("Rosario",      "S", "Santa Fe",                        -32.95, -60.64),
            ("Mendoza",      "M", "Mendoza",                         -32.89, -68.84),
        ]),
        ("ES", "España", 0.12, [
            ("Madrid",    "MD", "Comunidad de Madrid",    40.42, -3.70),
            ("Barcelona", "CT", "Cataluña",               41.39,  2.17),
            ("Valencia",  "VC", "Comunitat Valenciana",   39.47, -0.38),
            ("Sevilla",   "AN", "Andalucía",              37.39, -5.98),
            ("Zaragoza",  "AR", "Aragón",                 41.65, -0.89),
            ("Málaga",    "AN", "Andalucía",              36.72, -4.42),
        ]),
        ("CL", "Chile", 0.10, [
            ("Santiago",   "RM", "Región Metropolitana", -33.45, -70.67),
            ("Valparaíso", "VS", "Valparaíso",           -33.05, -71.62),
            ("Concepción", "BI", "Biobío",               -36.83, -73.05),
        ]),
        ("PE", "Perú", 0.08, [
            ("Lima",     "LIM", "Lima",        -12.05, -77.04),
            ("Arequipa", "ARE", "Arequipa",    -16.41, -71.54),
            ("Trujillo", "LAL", "La Libertad",  -8.11, -79.03),
        ]),
        ("EC", "Ecuador", 0.08, [
            ("Quito",     "P", "Pichincha", -0.18, -78.47),
            ("Guayaquil", "G", "Guayas",    -2.19, -79.89),
            ("Cuenca",    "A", "Azuay",     -2.90, -79.00),
        ]),
    ],
    "en": [
        ("US", "United States", 0.55, [
            ("New York",     "NY", "New York",      40.71,  -74.01),
            ("Los Angeles",  "CA", "California",    34.05, -118.24),
            ("Chicago",      "IL", "Illinois",      41.88,  -87.63),
            ("Houston",      "TX", "Texas",         29.76,  -95.37),
            ("Phoenix",      "AZ", "Arizona",       33.45, -112.07),
            ("Philadelphia", "PA", "Pennsylvania",  39.95,  -75.17),
            ("San Antonio",  "TX", "Texas",         29.42,  -98.49),
            ("San Diego",    "CA", "California",    32.72, -117.16),
            ("Dallas",       "TX", "Texas",         32.78,  -96.80),
            ("San Jose",     "CA", "California",    37.34, -121.89),
            ("Austin",       "TX", "Texas",         30.27,  -97.74),
            ("Jacksonville", "FL", "Florida",       30.33,  -81.66),
        ]),
        ("CA", "Canada", 0.12, [
            ("Toronto",   "ON", "Ontario",           43.65,  -79.38),
            ("Vancouver", "BC", "British Columbia",  49.28, -123.12),
            ("Montreal",  "QC", "Quebec",            45.50,  -73.57),
            ("Calgary",   "AB", "Alberta",           51.05, -114.07),
            ("Ottawa",    "ON", "Ontario",           45.42,  -75.70),
        ]),
        ("GB", "United Kingdom", 0.12, [
            ("London",     "LND", "Greater London",      51.51, -0.13),
            ("Manchester", "MAN", "Greater Manchester",  53.48, -2.24),
            ("Birmingham", "BIR", "West Midlands",       52.49, -1.89),
            ("Leeds",      "LDS", "West Yorkshire",      53.80, -1.55),
            ("Glasgow",    "GLG", "Scotland",            55.86, -4.25),
        ]),
        ("AU", "Australia", 0.08, [
            ("Sydney",    "NSW", "New South Wales",   -33.87, 151.21),
            ("Melbourne", "VIC", "Victoria",          -37.81, 144.96),
            ("Brisbane",  "QLD", "Queensland",        -27.47, 153.03),
            ("Perth",     "WA",  "Western Australia", -31.95, 115.86),
        ]),
        ("DE", "Germany", 0.07, [
            ("Berlin",            "BE", "Berlin",  52.52, 13.40),
            ("München",           "BY", "Bayern",  48.14, 11.58),
            ("Hamburg",           "HH", "Hamburg", 53.55,  9.99),
            ("Frankfurt am Main", "HE", "Hessen",  50.11,  8.68),
        ]),
        ("FR", "France", 0.06, [
            ("Paris",     "IDF", "Île-de-France",              48.86, 2.35),
            ("Lyon",      "ARA", "Auvergne-Rhône-Alpes",        45.76, 4.84),
            ("Marseille", "PAC", "Provence-Alpes-Côte d'Azur",  43.30, 5.37),
            ("Toulouse",  "OCC", "Occitanie",                  43.60, 1.44),
        ]),
    ],
    "fr": [
        ("FR", "France", 0.70, [
            ("Paris",      "IDF", "Île-de-France",              48.8566,  2.3522),
            ("Lyon",       "ARA", "Auvergne-Rhône-Alpes",        45.7640,  4.8357),
            ("Marseille",  "PAC", "Provence-Alpes-Côte d'Azur",  43.2965,  5.3698),
            ("Toulouse",   "OCC", "Occitanie",                   43.6047,  1.4442),
            ("Nice",       "PAC", "Provence-Alpes-Côte d'Azur",  43.7102,  7.2620),
            ("Nantes",     "PDL", "Pays de la Loire",            47.2184, -1.5536),
            ("Strasbourg", "GES", "Grand Est",                   48.5734,  7.7521),
            ("Bordeaux",   "NAQ", "Nouvelle-Aquitaine",          44.8378, -0.5792),
            ("Lille",      "HDF", "Hauts-de-France",             50.6292,  3.0573),
            ("Rennes",     "BRE", "Bretagne",                    48.1173, -1.6778),
        ]),
        ("BE", "Belgique", 0.10, [
            ("Bruxelles", "BRU", "Bruxelles-Capitale",  50.8503,  4.3517),
            ("Anvers",    "VAN", "Vlaanderen",          51.2194,  4.4025),
            ("Liège",     "WLG", "Wallonie",            50.6326,  5.5797),
        ]),
        ("CH", "Suisse", 0.08, [
            ("Genève",   "GE", "Genève",  46.2044,  6.1432),
            ("Lausanne", "VD", "Vaud",    46.5197,  6.6323),
            ("Zürich",   "ZH", "Zürich",  47.3769,  8.5417),
        ]),
        ("CA", "Canada", 0.07, [
            ("Montréal", "QC", "Québec",  45.5017, -73.5673),
            ("Québec",   "QC", "Québec",  46.8139, -71.2080),
            ("Ottawa",   "ON", "Ontario", 45.4215, -75.6972),
        ]),
        ("LU", "Luxembourg", 0.05, [
            ("Luxembourg", "LU", "Luxembourg",  49.6116,  6.1319),
        ]),
    ],
    "pt": [
        ("BR", "Brasil", 0.80, [
            ("São Paulo",      "SP", "São Paulo",         -23.55, -46.63),
            ("Rio de Janeiro", "RJ", "Rio de Janeiro",    -22.91, -43.17),
            ("Belo Horizonte", "MG", "Minas Gerais",      -19.92, -43.94),
            ("Salvador",       "BA", "Bahia",             -12.97, -38.50),
            ("Fortaleza",      "CE", "Ceará",              -3.73, -38.53),
            ("Curitiba",       "PR", "Paraná",            -25.43, -49.27),
            ("Manaus",         "AM", "Amazonas",           -3.12, -60.02),
            ("Recife",         "PE", "Pernambuco",         -8.05, -34.88),
            ("Porto Alegre",   "RS", "Rio Grande do Sul", -30.03, -51.23),
            ("Belém",          "PA", "Pará",               -1.46, -48.50),
        ]),
        ("PT", "Portugal", 0.20, [
            ("Lisboa", "11", "Lisboa", 38.72, -9.14),
            ("Porto",  "13", "Porto",  41.15, -8.61),
            ("Braga",  "03", "Braga",  41.55, -8.43),
        ]),
    ],
}


_CONTINENTS: dict[str, str] = {
    "US": "North America", "CA": "North America", "MX": "North America",
    "GB": "Europe",        "DE": "Europe",        "FR": "Europe",
    "ES": "Europe",        "PT": "Europe",        "BE": "Europe",
    "CH": "Europe",        "LU": "Europe",
    "AU": "Oceania",
    "CO": "South America", "AR": "South America", "CL": "South America",
    "PE": "South America", "EC": "South America", "BR": "South America",
}
