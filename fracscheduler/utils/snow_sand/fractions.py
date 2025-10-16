from flask import Blueprint

controllers = Blueprint('controllers', __name__)

# register all sub-modules so their routes hook into `controllers`
from datetime import datetime
from . import calendar as cd
from .. import parameters
from .. import hollydays

#============= Global Variables =====================
fractions_quantity = parameters.number_of_fractions()
weeks_expected_per_year = parameters.weeks_expected_per_year()

# ======== Fractions-related functions ========
def holly_weeks(
    current_year,
    weekday_calendar_starts
):
    """
    Some weeks have special hollydays which no one want to miss them. 
    Those hollydays could be deterministic or probabilistic.
    """

    def deterministic_holly_weeks(
        current_year,
        weekday_calendar_starts
    ):
        """
        Deterministic hollydays are those which have an specific rule to determinate them,
        for example mexican revolution day is third monday of each november, so this funcion return us 
        the list of those weeks which have these hollydays.
        """

        semana_santa = hollydays.sabado_santo(current_year + 1)
        thanks = hollydays.thanksgiving(current_year)
        newyear = hollydays.new_year(current_year + 1)
        christ = hollydays.christmas(current_year)
        special_dates = [semana_santa,thanks,newyear,christ]

        calendar = cd.main_day_weeker(current_year, weekday_calendar_starts)
        week_index = []

        for i in special_dates:
            week = calendar[i]
            week_index.append(week)

        return week_index

    def probabilistic_holly_weeks(
        current_year,
        weekday_calendar_starts
    ):
        """
        Others hollydays don't let us get sure about whether the week which contains the date will the week when the date will celebrated.
        For example, figure out independence day takes on tuesday and owr fractional week begins also in tusday but people wants to celecrate in previous momday.
        It's worth to say, according the earlier case, if we take the weeks which have these hollydays and we take the previous week, we cover all the cases.
        So, you can intuit what this function does.
        """
       
        special_dates = []

        calendar = cd.main_day_weeker(current_year, weekday_calendar_starts)
        week_index = []

        for i in special_dates:
            week = calendar[i]
            week_index.append(week)
        
        before_week_index = []
        for k in week_index:
            before_week_index.append([k[0] - 1])

        return week_index + before_week_index

    regular = deterministic_holly_weeks(current_year, weekday_calendar_starts)
    irregular = probabilistic_holly_weeks(current_year, weekday_calendar_starts)

    gold = []                       # This block is looking for clean the list up.
    for i in regular + irregular:
        if i not in gold:
            gold.append(i)
    gold_num = [k[0] for k in gold]
    gold_num.sort()
    gold = [[k] for k in gold_num]

    return gold

def maintenance_weeks_list(
    current_year, 
    weekday_calendar_starts, 
    maintenance_path
):
    """
    Select week indices for maintenance based on a path and the year characteristics.
    """
    weeks_per_fraction = weeks_expected_per_year // fractions_quantity
    reserved_weeks = weeks_expected_per_year - fractions_quantity * weeks_per_fraction
    
    def maintenance_weeks_paths(
        current_year,
        weekday_calendar_starts,
        reserved_weeks
    ):
        """
        This function crafts a dictionarie with no hollyweeks in its keys (datetimes),
        and also it bounds the dictionarie particulary.
        """
        maintenance_list = [[18],[25],[34],[47]]
        if cd.extra_week_indicator(current_year,weekday_calendar_starts):
            reserved_weeks += 1
            maintenance_list.append([52])
        calendar = cd.main_day_weeker(current_year, weekday_calendar_starts)

        regular = {k:v for (k,v) in calendar.items() if v in maintenance_list}
        list = [[i//7] for i in range(len(regular.values()))]
        regular = dict(zip(regular.keys(),list))
        bound = len(regular.keys()) // 7
        max_regular_len = bound // reserved_weeks * reserved_weeks
        dic = {k: v for k, v in regular.items() if v[0] < max_regular_len}

        return {k:[(v[0] + (current_year % fractions_quantity)) % (max_regular_len // reserved_weeks)] for (k,v) in dic.items()}

    maintenance_deserved_weeks = maintenance_weeks_paths(current_year, weekday_calendar_starts,reserved_weeks)
    lenght = len(maintenance_deserved_weeks.values()) // 7 // reserved_weeks
    matching_keys = [k for (k,v) in maintenance_deserved_weeks.items() if v[0] == maintenance_path % lenght]

    calendar = cd.main_day_weeker(current_year,weekday_calendar_starts)

    dirty_list = []
    for i in matching_keys:
        dirty_list.append(calendar[i])

    maintenance_weeks = []
    for r in dirty_list:
        if r not in maintenance_weeks:
            maintenance_weeks.append(r)
        
    return maintenance_weeks
    
def fractional_day_weeker(
    current_year, 
    weekday_calendar_starts, 
    maintenance_path
):
    """
    This function lists weeks which are able to distribute their to fraction's owners.
    """
    semana_santa_index = cd.semana_santa_weeker(current_year,weekday_calendar_starts)
    easter_index = cd.easter_weeker(current_year,weekday_calendar_starts)
    maintenance_weeks = maintenance_weeks_list(current_year,weekday_calendar_starts, maintenance_path)
    

    special_weeks = []
    special_weeks.append(semana_santa_index)
    special_weeks.append(easter_index)

    day_week_indexes_dic = cd.main_day_weeker(current_year,weekday_calendar_starts)  
    week_indexes_after_maintenance = {k: v for k,v in day_week_indexes_dic.items() if v not in maintenance_weeks}
    unspecial_week_indexes = {k: v for k,v in week_indexes_after_maintenance.items() if v not in special_weeks}

    recerved_fractional_week_indexes = [24,26]
    total_fractional_weeks = weeks_expected_per_year - len(maintenance_weeks)

    reorder_list = [[a] for a in range(total_fractional_weeks + 1) if a not in recerved_fractional_week_indexes]
    expanded_reorder_list = [a for a in reorder_list for _ in range(7)]
    week_fractional_indexes =  dict(zip(unspecial_week_indexes.keys(),expanded_reorder_list))

    for date in day_week_indexes_dic.keys():
        if day_week_indexes_dic[date] == semana_santa_index:
            week_fractional_indexes[date] = [recerved_fractional_week_indexes[0]]
        elif day_week_indexes_dic[date] == easter_index:
            week_fractional_indexes[date] = [recerved_fractional_week_indexes[1]]
        else:
            pass
    
    return week_fractional_indexes
    

def fractional_index_maker(
    current_year, 
    weekday_calendar_starts, 
    maintenance_path
):
    """
    Indexes each date with its corresponding fraction index.
    """
    def calculate_fraction_index(
        week_index, offset, 
        season_fraction_count, 
        season_week_count
    ):
        return ((week_index - offset) % season_week_count) % season_fraction_count

    def build_fraction_map(
        week_dict, 
        transform_func, 
        offset=0, 
        base_index=0
    ):
        return {
            k: [calculate_fraction_index(transform_func(v[0]), offset, season_fractions_quantity, season_fractional_weeks_quantity) + base_index]
            for k, v in week_dict.items()
        }

    fractional_calendar_week_indexed = fractional_day_weeker(current_year, weekday_calendar_starts, maintenance_path)
    total_fractional_weeks_quantity = weeks_expected_per_year // fractions_quantity * fractions_quantity

    season_fractional_weeks_quantity = total_fractional_weeks_quantity // 2
    season_fractions_quantity = fractions_quantity // 2
    mid_point = len(fractional_calendar_week_indexed) // 2

    # Snow season
    snow_weeks = {
        k: v for k, v in fractional_calendar_week_indexed.items() if v[0] < mid_point
    }
    snow_fractional = build_fraction_map(
        snow_weeks,
        lambda w: w // 6,
        offset=current_year % season_fractions_quantity
    )

    # Sand season ranges
    sand_ranges = {
        'first': range(24, 32),
        'second': range(32, 44),
        'third': range(44, 48)
    }

    sand_fractionals = []

    for label, week_range in sand_ranges.items():
        weeks = {
            k: v for k, v in fractional_calendar_week_indexed.items() if v[0] in week_range
        }

        if label == 'second':
            transform = lambda w: (w - min(week_range)) // 3
        else:
            transform = lambda w: w - min(week_range)

        sand_fractionals.append(
            build_fraction_map(
                weeks,
                transform,
                offset=current_year % season_fractions_quantity,
                base_index=4
            )
        )

    # Combine all
    final_map = snow_fractional
    for partial_map in sand_fractionals:
        final_map.update(partial_map)

    return final_map

def fraction_hunter(
    wishful_year, 
    wishful_month,
    wishful_day,
    weekday_calendar_starts, 
    maintenance_path
):
    """
    Busca la fracción del día pedido dentro de la temporada de snow-bird que
    empieza el 22 de septiembre. Si la fecha es anterior al 22-Sep del año
    dado, cae en la temporada que arrancó el año anterior.
    """
    wishful_date = datetime(wishful_year, wishful_month, wishful_day)

    # Fecha de inicio “oficial” de temporada en el año dado
    season_start = parameters.first_day_snow(wishful_year)

    # Si piden algo antes del 22-Sep, pertenece a la temporada del año anterior
    if wishful_date < season_start:
        season_year = wishful_year - 1
    else:
        season_year = wishful_year

    # Construimos calendario fraccional de esa temporada y la siguiente
    current_calendar = fractional_index_maker(
        season_year, weekday_calendar_starts, maintenance_path
    )
    next_calendar = fractional_index_maker(
        season_year + 1, weekday_calendar_starts, maintenance_path
    )

    # Unificamos ambas tablas y buscamos la fecha
    fraction_spot = {**current_calendar, **next_calendar}

    try:
        return fraction_spot[wishful_date]
    except KeyError:
        return "So sorry, your wishful date isn't available due our current schedule"

def unfractional_dates_list(
    current_year,
    weekday_calendar_starts, 
    maintenance_path
):
    """
    This funcion has as goal crafting a list with no fractional hollydays, such that,
    this list must have the rest of the hollydays of each year.
    """
    whole_calendar = cd.main_day_sequence(current_year, weekday_calendar_starts)
    fractional_calendar = fractional_index_maker(current_year, weekday_calendar_starts, maintenance_path)

    hollydays = list(whole_calendar.keys())
    fractional_dates = set(fractional_calendar.keys())  # We choose set instead of list for faster searching

    return [i for i in hollydays if i not in fractional_dates]