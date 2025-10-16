import calendar
from datetime import datetime, date

from flask import render_template, request

from . import controllers
from .calendar_view import choose_utils, build_months, fraction_colors
from models import (
    apartament_maintenance_path,
    apartament_weekday_calendar_starts,
    apartament_type,
)
from utils.hollydays import regular_hollydays_dic, snow_hollydays_dic


@controllers.route('/hunt_fraction')
def hunt_fraction():
    date_str = request.args.get('hunter_date')
    apartment = request.args.get('apartament', 204, type=int)

    # Inicializar variables
    error_message = None
    selected_fractions = []

    # Validar fecha de deseo
    if date_str:
        try:
            wish = datetime.strptime(date_str, "%Y-%m-%d").date()
        except ValueError:
            error_message = "Invalid wishful date"
            wish = date.today()
    else:
        error_message = "No wishful date provided"
        wish = date.today()

    # Parámetros del apartamento
    maintenance_path = apartament_maintenance_path.get(apartment, 1)
    weekday_start = apartament_weekday_calendar_starts.get(apartment, 1)
    idx_maker, unfract_list, hunter = choose_utils(apartment)

    # Determinar año de ciclo para snow
    apt_type = apartament_type.get(apartment, "regular")
    cycle_year = wish.year
    if apt_type == "snow" and 1 <= wish.month <= 8:
        cycle_year = wish.year - 1

    # Ejecutar hunter solo si no hubo error de parseo
    if not error_message:
        result = hunter(
            wish.year, wish.month, wish.day,
            weekday_start, maintenance_path
        )
        if isinstance(result, str):
            error_message = result
        else:
            selected_fractions = [result[0]]

    # Reconstruir datos del calendario usando cycle_year
    months = build_months(cycle_year, apt_type)

    frac_idx = idx_maker(cycle_year, weekday_start, maintenance_path)
    frac_prev = idx_maker(cycle_year - 1, weekday_start, maintenance_path)
    frac_next = idx_maker(cycle_year + 1, weekday_start, maintenance_path)

    unf_curr = unfract_list(cycle_year, weekday_start, maintenance_path)
    unf_prev = unfract_list(cycle_year - 1, weekday_start, maintenance_path)
    unf_next = unfract_list(cycle_year + 1, weekday_start, maintenance_path)

    display_cal = calendar.Calendar(firstweekday=0)
    prev_dec = display_cal.monthdayscalendar(cycle_year - 1, 12)
    day_names = [calendar.day_abbr[i] for i in range(7)]

    golden_holidays = (
        snow_hollydays_dic(cycle_year) if apt_type == "snow"
        else regular_hollydays_dic(cycle_year)
    )

    return render_template(
        'calendar.html.j2',
        year=cycle_year,
        apt_type=apt_type,
        apartament=apartment,
        available_apartaments=sorted(apartament_maintenance_path.keys()),
        day_names=day_names,
        calendar=calendar,
        fraction_colors=fraction_colors,
        datetime=datetime,
        months_with_index=months,
        previous_december=prev_dec,
        fractional_indices=frac_idx,
        fractional_indices_prev=frac_prev,
        fractional_indices_next=frac_next,
        unfractional_dates=unf_curr,
        unfractional_dates_prev=unf_prev,
        unfractional_dates_next=unf_next,
        selected_fractions=selected_fractions,
        golden_holidays=golden_holidays,
        error_message=error_message
    )