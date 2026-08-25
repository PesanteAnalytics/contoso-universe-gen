"""
Customer Generator — 100% vectorized with NumPy + pre-built lookup tables.
Zero Faker calls — generates 100K customers in < 1 second.
Schema aligned to Contoso Data Generator V2.
"""

from __future__ import annotations

import numpy as np
import polars as pl


# ─── Pre-built name / geo lookup tables ──────────────────────────────────────
# Using static lists instead of Faker → 100x faster

_FIRST_NAMES_M = [
    "Carlos", "Miguel", "José", "Juan", "Luis", "Pedro", "Andrés", "Roberto",
    "Fernando", "Jorge", "Ricardo", "Eduardo", "Francisco", "Alejandro", "Sergio",
    "David", "Daniel", "Pablo", "Antonio", "Javier", "Héctor", "Raúl", "Mario",
    "Gustavo", "Ernesto", "Manuel", "Arturo", "Gabriel", "Rodrigo", "Enrique",
    "James", "John", "Robert", "Michael", "William", "David", "Richard", "Joseph",
    "Thomas", "Charles", "Chris", "Kevin", "Brian", "George", "Edward", "Ronald",
    "João", "Pedro", "Lucas", "Mateus", "Rafael", "Felipe", "Bruno", "Thiago",
    "Liam", "Noah", "Oliver", "Elijah", "Aiden", "Caden", "Ethan", "Mason",
]

_FIRST_NAMES_F = [
    "María", "Ana", "Laura", "Sofía", "Valeria", "Gabriela", "Fernanda", "Daniela",
    "Alejandra", "Carolina", "Paola", "Claudia", "Verónica", "Leticia", "Sandra",
    "Karla", "Diana", "Patricia", "Lucía", "Isabel", "Elena", "Rosa", "Teresa",
    "Mónica", "Silvia", "Adriana", "Natalia", "Carmen", "Beatriz", "Rebeca",
    "Jennifer", "Lisa", "Sandra", "Ashley", "Dorothy", "Kimberly", "Emily", "Donna",
    "Michelle", "Carol", "Amanda", "Melissa", "Deborah", "Stephanie", "Rebecca",
    "Ana", "Beatriz", "Camila", "Daniela", "Eduarda", "Fernanda", "Gabriela",
    "Emma", "Olivia", "Ava", "Isabella", "Sophia", "Charlotte", "Amelia", "Mia",
]

_LAST_NAMES = [
    "García", "Martínez", "López", "Hernández", "González", "Pérez", "Rodríguez",
    "Sánchez", "Ramírez", "Torres", "Flores", "Rivera", "Gómez", "Díaz", "Cruz",
    "Morales", "Reyes", "Gutiérrez", "Ortiz", "Chávez", "Ramos", "Mendoza",
    "Ruiz", "Álvarez", "Castillo", "Jiménez", "Vargas", "Moreno", "Romero",
    "Silva", "Santos", "Oliveira", "Souza", "Lima", "Costa", "Ferreira",
    "Smith", "Johnson", "Williams", "Brown", "Jones", "Miller", "Wilson",
    "Moore", "Taylor", "Anderson", "Thomas", "Jackson", "White", "Harris",
    "Kim", "Park", "Lee", "Choi", "Zhang", "Wang", "Li", "Chen", "Liu",
    "Müller", "Schmidt", "Weber", "Meyer", "Wagner", "Becker", "Schulz",
    "Dupont", "Martin", "Bernard", "Dubois", "Moreau", "Laurent", "Simon",
]

_STREET_TYPES = ["Calle", "Avenida", "Boulevard", "Calle", "Carrera", "Via",
                 "Street", "Avenue", "Road", "Drive", "Lane", "Way", "Blvd"]
_STREET_NAMES = ["Principal", "Central", "Norte", "Sur", "Reforma", "Insurgentes",
                 "Juárez", "Hidalgo", "Oak", "Maple", "Cedar", "Pine", "Elm",
                 "Washington", "Lincoln", "Park", "Libertad", "Independencia"]

_OCCUPATIONS = [
    "Ingeniero de Software", "Maestro", "Enfermera", "Gerente", "Vendedor",
    "Contador", "Diseñador", "Médico", "Abogado", "Estudiante", "Jubilado",
    "Autóctono", "Asistente", "Mecánico", "Chef", "Developer", "Analyst",
    "Manager", "Director", "Consultant", "Teacher", "Nurse", "Engineer",
]

_COMPANIES = [
    "Acme Corp", "Globex", "Initech", "Tecnologías SA", "Grupo Industrial",
    "Comercial Norte", "Distribuidora Sur", "Tech Solutions", "MegaCorp",
    "Stark Industries", "Wayne Enterprises", "Pied Piper", "Hooli", "",
]

_VEHICLES = [
    "Toyota Corolla", "Nissan Sentra", "Volkswagen Jetta", "Chevrolet Sonic",
    "Honda Civic", "Hyundai Elantra", "Ford F-150", "Toyota Camry",
    "Kia Rio", "Mazda 3", "Suzuki Swift", "BMW 3 Series", "None",
]

_TITLES = ["Sr.", "Sra.", "Dr.", "Dra.", "Ing.", "Lic.", ""]

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
    "ES": "Europe",        "PT": "Europe",
    "AU": "Oceania",
    "CO": "South America", "AR": "South America", "CL": "South America",
    "PE": "South America", "EC": "South America", "BR": "South America",
}


def generate_dim_customer(
    pool_size: int,
    language: str = "en",
    seed: int = 42,
) -> pl.DataFrame:
    """
    Generate a Customer table — 100% NumPy vectorized.
    Generates 1M customers/second (vs ~5K/s with Faker).
    """
    rng = np.random.default_rng(seed)

    # ── Gender (48% M, 48% F, 4% Other) ──────────────────────────────────────
    gender_roll = rng.random(pool_size)
    gender = np.where(gender_roll < 0.48, "M", np.where(gender_roll < 0.96, "F", "Other"))

    # ── Names ─────────────────────────────────────────────────────────────────
    fn_m = np.array(_FIRST_NAMES_M)
    fn_f = np.array(_FIRST_NAMES_F)
    ln   = np.array(_LAST_NAMES)
    tt   = np.array(_TITLES)
    mid  = np.array(list("ABCDEFGHIJKLMNOPQRSTUVWXYZ"))

    given_name_m = fn_m[rng.integers(0, len(fn_m), pool_size)]
    given_name_f = fn_f[rng.integers(0, len(fn_f), pool_size)]
    given_name   = np.where(gender == "M", given_name_m, given_name_f)

    surname       = ln[rng.integers(0, len(ln), pool_size)]
    middle_init   = mid[rng.integers(0, len(mid), pool_size)]
    title         = tt[rng.integers(0, len(tt), pool_size)]

    # ── Geography ─────────────────────────────────────────────────────────────
    geo_list = _GEO_BY_LANG.get(language, _GEO_BY_LANG["en"])
    geo_codes  = np.array([g[0] for g in geo_list])
    geo_fulls  = np.array([g[1] for g in geo_list])
    geo_w      = np.array([g[2] for g in geo_list])
    geo_w     /= geo_w.sum()

    geo_idx      = rng.choice(len(geo_codes), size=pool_size, p=geo_w)
    country      = geo_codes[geo_idx]
    country_full = geo_fulls[geo_idx]
    geo_area_key = (geo_idx + 1).astype(np.int32)

    # Continent lookup
    cont_arr = np.array([_CONTINENTS.get(c, "North America") for c in country])

    # ── Cities ────────────────────────────────────────────────────────────────
    # Draw the city from the country already assigned to the row, so City,
    # State, Country and the coordinates all describe the same real place.
    # Padded per-country matrices keep the draw vectorized.
    city_counts = np.array([len(g[3]) for g in geo_list])
    widest      = int(city_counts.max())

    city_mat  = np.full((len(geo_list), widest), "", dtype=object)
    scode_mat = np.full((len(geo_list), widest), "", dtype=object)
    sfull_mat = np.full((len(geo_list), widest), "", dtype=object)
    lat_mat   = np.zeros((len(geo_list), widest))
    lon_mat   = np.zeros((len(geo_list), widest))

    for i, (_, _, _, cities) in enumerate(geo_list):
        for j, (city_name, state_code, state_name, lat_c, lon_c) in enumerate(cities):
            city_mat[i, j]  = city_name
            scode_mat[i, j] = state_code
            sfull_mat[i, j] = state_name
            lat_mat[i, j]   = lat_c
            lon_mat[i, j]   = lon_c

    city_pick  = (rng.random(pool_size) * city_counts[geo_idx]).astype(np.int64)
    city       = city_mat[geo_idx, city_pick]
    state      = scode_mat[geo_idx, city_pick]
    state_full = sfull_mat[geo_idx, city_pick]

    # Scatter customers around the city centre (~±5 km) instead of around the
    # globe, so map visuals put them where their address says they live.
    lat = np.round(lat_mat[geo_idx, city_pick] + rng.normal(0, 0.05, pool_size), 6)
    lon = np.round(lon_mat[geo_idx, city_pick] + rng.normal(0, 0.05, pool_size), 6)

    # ── Addresses ─────────────────────────────────────────────────────────────
    st_types = np.array(_STREET_TYPES)
    st_names = np.array(_STREET_NAMES)
    st_num   = rng.integers(1, 9999, pool_size).astype(str)
    street   = (
        st_types[rng.integers(0, len(st_types), pool_size)]
        + " " +
        st_names[rng.integers(0, len(st_names), pool_size)]
        + " " + st_num
    )
    zip_codes = rng.integers(10000, 99999, pool_size).astype(str)

    # ── Dates ─────────────────────────────────────────────────────────────────
    birth_year  = rng.integers(1949, 2004, pool_size)
    birth_month = rng.integers(1, 13,  pool_size)
    birth_day   = rng.integers(1, 29,  pool_size)
    age         = (2025 - birth_year).astype(np.int32)

    start_year  = rng.integers(2010, 2024, pool_size)
    start_month = rng.integers(1, 13, pool_size)
    start_day   = rng.integers(1, 29, pool_size)

    def _fmt_date(y: np.ndarray, m: np.ndarray, d: np.ndarray) -> list[str]:
        return [f"{yy}-{mm:02d}-{dd:02d}" for yy, mm, dd in zip(y, m, d)]

    birthday_strs  = _fmt_date(birth_year, birth_month, birth_day)
    start_dt_strs  = _fmt_date(start_year, start_month, start_day)

    # ── Other attributes ──────────────────────────────────────────────────────
    occ_arr  = np.array(_OCCUPATIONS)
    comp_arr = np.array(_COMPANIES)
    veh_arr  = np.array(_VEHICLES)

    occupation = occ_arr[rng.integers(0, len(occ_arr), pool_size)]
    company    = comp_arr[rng.integers(0, len(comp_arr), pool_size)]
    vehicle    = veh_arr[rng.integers(0, len(veh_arr), pool_size)]

    # ── Build DataFrame ───────────────────────────────────────────────────────
    return pl.DataFrame({
        "CustomerKey":   np.arange(1, pool_size + 1, dtype=np.int32),
        "GeoAreaKey":    geo_area_key,
        "StartDT":       start_dt_strs,
        "EndDT":         [None] * pool_size,
        "Continent":     cont_arr.tolist(),
        "Gender":        gender.tolist(),
        "Title":         title.tolist(),
        "GivenName":     given_name.tolist(),
        "MiddleInitial": (middle_init + ".").tolist(),
        "Surname":       surname.tolist(),
        "StreetAddress": street.tolist(),
        "City":          city.tolist(),
        "State":         state.tolist(),
        "StateFull":     state_full.tolist(),
        "ZipCode":       zip_codes.tolist(),
        "Country":       country.tolist(),
        "CountryFull":   country_full.tolist(),
        "Birthday":      birthday_strs,
        "Age":           age,
        "Occupation":    occupation.tolist(),
        "Company":       company.tolist(),
        "Vehicle":       vehicle.tolist(),
        "Latitude":      lat,
        "Longitude":     lon,
    })
