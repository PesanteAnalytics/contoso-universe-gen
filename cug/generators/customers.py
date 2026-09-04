"""
Customer Generator — 100% vectorized with NumPy + pre-built lookup tables.
Generates 100K customers in under a second from static lookup tables.
Schema aligned to Contoso Data Generator V2.
"""

from __future__ import annotations

from collections.abc import Sequence

import numpy as np
import polars as pl

from ..config import INACTIVE_SEGMENT, CustomerSegmentConfig, default_customer_segments
from ..i18n.geography import _CONTINENTS, _GEO_BY_LANG

# ─── Pre-built name / geo lookup tables ──────────────────────────────────────
# Static lists keep the whole draw vectorized

_FIRST_NAMES_M_BY_LANG: dict[str, list[str]] = {
    "es": [
        "Carlos", "Miguel", "José", "Juan", "Luis", "Pedro", "Andrés", "Roberto",
        "Fernando", "Jorge", "Ricardo", "Eduardo", "Francisco", "Alejandro", "Sergio",
        "David", "Daniel", "Pablo", "Antonio", "Javier", "Héctor", "Raúl", "Mario",
        "Gustavo", "Ernesto", "Manuel", "Arturo", "Gabriel", "Rodrigo", "Enrique",
    ],
    "en": [
        "James", "John", "Robert", "Michael", "William", "David", "Richard", "Joseph",
        "Thomas", "Charles", "Chris", "Kevin", "Brian", "George", "Edward", "Ronald",
        "Liam", "Noah", "Oliver", "Elijah", "Aiden", "Caden", "Ethan", "Mason",
    ],
    "pt": [
        "João", "Pedro", "Lucas", "Mateus", "Rafael", "Felipe", "Bruno", "Thiago",
        "Carlos", "Miguel", "José", "Luís", "António", "Francisco", "Diogo", "Tiago",
    ],
    "fr": [
        "Jean", "Pierre", "Louis", "Jacques", "Michel", "Philippe", "François", "Alain",
        "Nicolas", "Christophe", "Julien", "Thomas", "Alexandre", "Guillaume", "Maxime",
        "Antoine", "Benoît", "Laurent", "Stéphane", "Olivier", "Frédéric", "Éric",
        "Thierry", "Patrick", "Bernard", "Claude", "Henri", "René", "Paul", "Marcel",
    ],
}
_FIRST_NAMES_M = _FIRST_NAMES_M_BY_LANG["en"]  # fallback

_FIRST_NAMES_F_BY_LANG: dict[str, list[str]] = {
    "es": [
        "María", "Ana", "Laura", "Sofía", "Valeria", "Gabriela", "Fernanda", "Daniela",
        "Alejandra", "Carolina", "Paola", "Claudia", "Verónica", "Leticia", "Sandra",
        "Karla", "Diana", "Patricia", "Lucía", "Isabel", "Elena", "Rosa", "Teresa",
        "Mónica", "Silvia", "Adriana", "Natalia", "Carmen", "Beatriz", "Rebeca",
    ],
    "en": [
        "Jennifer", "Lisa", "Sandra", "Ashley", "Dorothy", "Kimberly", "Emily", "Donna",
        "Michelle", "Carol", "Amanda", "Melissa", "Deborah", "Stephanie", "Rebecca",
        "Emma", "Olivia", "Ava", "Isabella", "Sophia", "Charlotte", "Amelia", "Mia",
    ],
    "pt": [
        "Ana", "Beatriz", "Camila", "Daniela", "Eduarda", "Fernanda", "Gabriela",
        "Maria", "Juliana", "Patrícia", "Carolina", "Inês", "Mariana", "Leonor",
    ],
    "fr": [
        "Marie", "Isabelle", "Catherine", "Nathalie", "Sophie", "Monique", "Sylvie",
        "Françoise", "Martine", "Christine", "Valérie", "Sandrine", "Stéphanie", "Céline",
        "Aurélie", "Émilie", "Camille", "Chloé", "Manon", "Léa", "Juliette", "Louise",
        "Adèle", "Marguerite", "Colette", "Simone", "Jacqueline", "Madeleine", "Yvonne", "Renée",
    ],
}
_FIRST_NAMES_F = _FIRST_NAMES_F_BY_LANG["en"]  # fallback

_LAST_NAMES_BY_LANG: dict[str, list[str]] = {
    "es": [
        "García", "Martínez", "López", "Hernández", "González", "Pérez", "Rodríguez",
        "Sánchez", "Ramírez", "Torres", "Flores", "Rivera", "Gómez", "Díaz", "Cruz",
        "Morales", "Reyes", "Gutiérrez", "Ortiz", "Chávez", "Ramos", "Mendoza",
        "Ruiz", "Álvarez", "Castillo", "Jiménez", "Vargas", "Moreno", "Romero",
    ],
    "en": [
        "Smith", "Johnson", "Williams", "Brown", "Jones", "Miller", "Wilson",
        "Moore", "Taylor", "Anderson", "Thomas", "Jackson", "White", "Harris",
        "Kim", "Park", "Lee", "Choi", "Zhang", "Wang", "Li", "Chen", "Liu",
        "Müller", "Schmidt", "Weber", "Meyer", "Wagner", "Becker", "Schulz",
    ],
    "pt": [
        "Silva", "Santos", "Oliveira", "Souza", "Lima", "Ferreira", "Pereira",
        "Rodrigues", "Almeida", "Nascimento", "Carvalho", "Ribeiro", "Martins", "Costa",
    ],
    "fr": [
        "Martin", "Bernard", "Dubois", "Thomas", "Robert", "Richard", "Petit",
        "Durand", "Leroy", "Moreau", "Simon", "Laurent", "Lefebvre", "Michel",
        "Garcia", "David", "Bertrand", "Roux", "Vincent", "Fournier", "Morel",
        "Girard", "André", "Mercier", "Dupont", "Lambert", "Bonnet", "François",
        "Martinez", "Léger",
    ],
}
_LAST_NAMES = _LAST_NAMES_BY_LANG["en"]  # fallback

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

def generate_dim_customer(
    pool_size: int,
    language: str = "en",
    seed: int = 42,
    active_pct: float = 1.0,
    segments: Sequence[CustomerSegmentConfig] | None = None,
) -> pl.DataFrame:
    """
    Generate a Customer table — 100% NumPy vectorized.
    Generates roughly 1M customers per second.

    `active_pct` is the slice of the pool that ever buys anything; the rest are
    registered but dormant, which is what a real CRM looks like. The active
    slice is then cut into `segments` (Key Account / Large / Medium / Small by
    default), written out as the `CustomerSegment` column. The sales generator
    reads that column back to weight who appears on an order, so the two stay
    in agreement without DimCustomer carrying generator internals.
    """
    rng = np.random.default_rng(seed)

    # ── Gender (48% M, 48% F, 4% Other) ──────────────────────────────────────
    gender_roll = rng.random(pool_size)
    gender = np.where(gender_roll < 0.48, "M", np.where(gender_roll < 0.96, "F", "Other"))

    # ── Names ─────────────────────────────────────────────────────────────────
    fn_m_pool = _FIRST_NAMES_M_BY_LANG.get(language, _FIRST_NAMES_M_BY_LANG["en"])
    fn_f_pool = _FIRST_NAMES_F_BY_LANG.get(language, _FIRST_NAMES_F_BY_LANG["en"])
    ln_pool   = _LAST_NAMES_BY_LANG.get(language, _LAST_NAMES_BY_LANG["en"])

    fn_m = np.array(fn_m_pool)
    fn_f = np.array(fn_f_pool)
    ln   = np.array(ln_pool)
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

    # ── Segmentation: active vs dormant, then tier within the active base ─────
    segs = list(segments) if segments else default_customer_segments()
    seg_names  = np.array([s.name for s in segs], dtype=object)
    seg_shares = np.array([s.share for s in segs], dtype=float)
    seg_shares = seg_shares / seg_shares.sum()

    is_active = rng.random(pool_size) < active_pct
    seg_pick  = rng.choice(len(segs), size=pool_size, p=seg_shares)
    segment   = np.where(is_active, seg_names[seg_pick], INACTIVE_SEGMENT)

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
        "CustomerSegment": segment.tolist(),
        "Latitude":      lat,
        "Longitude":     lon,
    })
