import calendar
from datetime import datetime, date
from flask import render_template, request

from . import controllers
from models import (
    apartament_maintenance_path,
    apartament_weekday_calendar_starts,
    apartament_type,
)
from utils import (
    regular_fractional_index_maker,
    snow_fractional_index_maker,
    regular_unfractional_dates_list,
    snow_unfractional_dates_list,
    regular_fraction_hunter,
    snow_fraction_hunter,
)
from utils.hollydays import regular_hollydays_dic, snow_hollydays_dic

# shared color palette
fraction_colors = [
    "#CC00CC", "#ADD8E6", "#4472C4", "#FF7514",
    "#C00000", "#CCA9DD", "#00B050", "#FFE5B4"
]


def build_months(year, apt_type):
    cal = calendar.Calendar(firstweekday=0)

    if apt_type == "regular":
        return [
            (m, year, cal.monthdayscalendar(year, m))
            for m in range(1, 13)
        ]

    first_part = [
        (m, year, cal.monthdayscalendar(year, m))
        for m in range(9, 13)
    ]
    second_part = [
        (m, year + 1, cal.monthdayscalendar(year + 1, m))
        for m in range(1, 10)
    ]
    return first_part + second_part


def choose_utils(apartment):
    typ = apartament_type.get(apartment, "regular")
    if typ == "snow":
        return (
            snow_fractional_index_maker,
            snow_unfractional_dates_list,
            snow_fraction_hunter,
        )
    return (
        regular_fractional_index_maker,
        regular_unfractional_dates_list,
        regular_fraction_hunter,
    )


@controllers.route('/')
def index():
    year = request.args.get('year', 2026, type=int)
    apartment = request.args.get('apartament', 205, type=int)

    maintenance_path = apartament_maintenance_path.get(apartment, 1)
    weekday_start = apartament_weekday_calendar_starts.get(apartment, 1)
    idx_maker, unfract_list, _ = choose_utils(apartment)

    # all three years' fractional indices
    frac_curr = idx_maker(year, weekday_start, maintenance_path)
    frac_prev = idx_maker(year - 1, weekday_start, maintenance_path)
    frac_next = idx_maker(year + 1, weekday_start, maintenance_path)

    # all three years' unfractional dates
    unf_curr = unfract_list(year, weekday_start, maintenance_path)
    unf_prev = unfract_list(year - 1, weekday_start, maintenance_path)
    unf_next = unfract_list(year + 1, weekday_start, maintenance_path)

    apt_type = apartament_type.get(apartment, "regular")
    months = build_months(year, apt_type)

    display_cal = calendar.Calendar(firstweekday=0)
    prev_dec = display_cal.monthdayscalendar(year - 1, 12)
    day_names = [calendar.day_abbr[i] for i in range(7)]

    # parse selected fractions
    selected = request.args.getlist('fractions', type=str)
    if 'all' in selected:
        selected = list(range(8)) + ['unfractional', 'all']
    else:
        selected = [int(f) if f.isdigit() else f for f in selected]
    if 'unfractional' not in selected:
        unf_curr = unf_prev = unf_next = []

    # full holiday dictionary
    golden_holidays = (
        snow_hollydays_dic(year) if apt_type == "snow"
        else regular_hollydays_dic(year)
    )

    return render_template(
        'calendar.html.j2',
        year=year,
        today=date.today(),
        apt_type=apt_type,
        apartament=apartment,
        available_apartaments=sorted(apartament_maintenance_path.keys()),
        day_names=day_names,
        calendar=calendar,
        fraction_colors=fraction_colors,
        datetime=datetime,
        months_with_index=months,
        previous_december=prev_dec,
        fractional_indices=frac_curr,
        fractional_indices_prev=frac_prev,
        fractional_indices_next=frac_next,
        unfractional_dates=unf_curr,
        unfractional_dates_prev=unf_prev,
        unfractional_dates_next=unf_next,
        selected_fractions=selected,
        golden_holidays=golden_holidays,
        error_message=request.args.get('error_message')
    )