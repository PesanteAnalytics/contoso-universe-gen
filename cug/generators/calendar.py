"""
DimDate Generator — Extended calendar table with holidays.
Builds a comprehensive date dimension for Power BI / analytics use.
"""

from __future__ import annotations

from datetime import date, timedelta

import polars as pl
import holidays as hol


_MONTH_NAMES = {
    "en": ["January","February","March","April","May","June",
           "July","August","September","October","November","December"],
    "es": ["Enero","Febrero","Marzo","Abril","Mayo","Junio",
           "Julio","Agosto","Septiembre","Octubre","Noviembre","Diciembre"],
    "pt": ["Janeiro","Fevereiro","Março","Abril","Maio","Junho",
           "Julho","Agosto","Setembro","Outubro","Novembro","Dezembro"],
    "fr": ["Janvier","Février","Mars","Avril","Mai","Juin",
           "Juillet","Août","Septembre","Octobre","Novembre","Décembre"],
    "de": ["Januar","Februar","März","April","Mai","Juni",
           "Juli","August","September","Oktober","November","Dezember"],
}

_DAY_NAMES = {
    "en": ["Monday","Tuesday","Wednesday","Thursday","Friday","Saturday","Sunday"],
    "es": ["Lunes","Martes","Miércoles","Jueves","Viernes","Sábado","Domingo"],
    "pt": ["Segunda","Terça","Quarta","Quinta","Sexta","Sábado","Domingo"],
    "fr": ["Lundi","Mardi","Mercredi","Jeudi","Vendredi","Samedi","Dimanche"],
    "de": ["Montag","Dienstag","Mittwoch","Donnerstag","Freitag","Samstag","Sonntag"],
}


def generate_dim_date(
    start: date,
    end: date,
    country: str = "US",
    language: str = "en",
) -> pl.DataFrame:
    """
    Generate an extended DimDate table from start to end (inclusive).

    Columns:
      DateKey         : int YYYYMMDD
      Date            : date
      Year            : int
      Quarter         : int (1-4)
      Month           : int (1-12)
      MonthName       : str (localized)
      MonthNameShort  : str (localized, 3 chars)
      Week            : int (ISO week number)
      DayOfYear       : int
      DayOfMonth      : int
      DayOfWeek       : int (0=Monday, 6=Sunday)
      DayName         : str (localized)
      DayNameShort    : str (localized, 3 chars)
      IsWeekend       : bool
      IsHoliday       : bool
      HolidayName     : str | null
      IsWorkingDay    : bool
      WorkingDayOfMonth : int (sequential working day within month)
      YearMonth       : str "YYYY-MM"
      YearQuarter     : str "YYYY-Q#"
    """
    # Load holidays for country
    try:
        country_holidays = hol.country_holidays(country)
    except Exception:
        country_holidays = {}

    month_names = _MONTH_NAMES.get(language, _MONTH_NAMES["en"])
    day_names   = _DAY_NAMES.get(language, _DAY_NAMES["en"])

    rows = []
    working_day_counters: dict[tuple[int, int], int] = {}  # (year, month) -> count

    current = start
    while current <= end:
        is_weekend = current.weekday() >= 5   # Sat=5, Sun=6
        holiday_name = country_holidays.get(current)
        is_holiday   = holiday_name is not None
        is_working   = not is_weekend and not is_holiday

        ym = (current.year, current.month)
        if is_working:
            working_day_counters[ym] = working_day_counters.get(ym, 0) + 1

        wday = current.weekday()
        month_idx = current.month - 1

        rows.append({
            "DateKey":            int(current.strftime("%Y%m%d")),
            "Date":               current,
            "Year":               current.year,
            "Quarter":            (current.month - 1) // 3 + 1,
            "Month":              current.month,
            "MonthName":          month_names[month_idx] if month_idx < len(month_names) else current.strftime("%B"),
            "MonthNameShort":     (month_names[month_idx][:3] if month_idx < len(month_names) else current.strftime("%b")),
            "Week":               current.isocalendar().week,
            "DayOfYear":          current.timetuple().tm_yday,
            "DayOfMonth":         current.day,
            "DayOfWeek":          wday,
            "DayName":            day_names[wday] if wday < len(day_names) else current.strftime("%A"),
            "DayNameShort":       (day_names[wday][:3] if wday < len(day_names) else current.strftime("%a")),
            "IsWeekend":          is_weekend,
            "IsHoliday":          is_holiday,
            "HolidayName":        holiday_name or None,
            "IsWorkingDay":       is_working,
            "WorkingDayOfMonth":  working_day_counters.get(ym, 0) if is_working else 0,
            "YearMonth":          f"{current.year}-{current.month:02d}",
            "YearQuarter":        f"{current.year}-Q{(current.month - 1) // 3 + 1}",
        })

        current += timedelta(days=1)

    return pl.DataFrame(rows).with_columns([
        pl.col("DateKey").cast(pl.Int32),
        pl.col("Date").cast(pl.Date),
        pl.col("Year").cast(pl.Int32),
        pl.col("Quarter").cast(pl.Int32),
        pl.col("Month").cast(pl.Int32),
        pl.col("Week").cast(pl.Int32),
        pl.col("DayOfYear").cast(pl.Int32),
        pl.col("DayOfMonth").cast(pl.Int32),
        pl.col("DayOfWeek").cast(pl.Int32),
        pl.col("IsWeekend").cast(pl.Boolean),
        pl.col("IsHoliday").cast(pl.Boolean),
        pl.col("IsWorkingDay").cast(pl.Boolean),
        pl.col("WorkingDayOfMonth").cast(pl.Int32),
    ])
