from datetime import timedelta
from .. import hollydays
from .. import parameters

 # ======== Date-related functions ========
def first_day_first_week(year, weekday_calendar_starts): 
    """
    We'll use a calendar that lists its weeks.
    Every week in this calendar begins in monday, tuesday, wednesday,... (or 0,1,2,... according python index)
    January first belongs to the first week of each year.
    This function caculates the date of the first day of the first week of each year and calendar, depending on which weekday it starts on.  
    """
    day = parameters.first_day_regular(year)
    
    shift = (day.weekday() - weekday_calendar_starts) % 7   
    return day - timedelta(days = shift)

def main_day_sequence(year, weekday_calendar_starts):
    """
    This function crafts a dictionarie:
    -Keys are dates.
    -Values are lists, which each one has an unique natural number starting from 0.
    """
    dic = {}
    day = first_day_first_week(year, weekday_calendar_starts)
    edge_day = first_day_first_week(year + 1, weekday_calendar_starts)
    
    for i in range(0,(edge_day - day).days):
        dic[day] = [i]
        day += timedelta(days = 1)
    return dic

def main_day_weeker(year,weekday_calendar_starts):
    """
    This function takes a day index (or value) from main_day_sequence and become it in week index starting from 0.
    """
    dic = main_day_sequence(year,weekday_calendar_starts)
    for day_index in dic.values():
        week_index = (day_index[0] // 7)
        day_index[0] = week_index
    return dic

def new_weekday(year,weekday_calendar_starts):
    """
    This funtion re-define weekday number, depending on which day calendar starts on.
    """
    dic = main_day_sequence(year,weekday_calendar_starts)
    for day_index in dic.values():
        week_index = (day_index[0] % 7)
        day_index[0] = week_index
    return dic

def extra_week_indicator(year,weekday_calendar_starts):
    """
    We expect years have 52 weeks but actually,
    by how we defined the first day of each year,
    some years have a 53rd week.
    This function tell us whether a year have that extra week.
    """
    dic = main_day_weeker(year, weekday_calendar_starts)
    week_list=  []
    for week_index in dic.values():
        if week_index[0] not in week_list:
            week_list.append(week_index[0])
        pass
    count_weeks = len(week_list)
    weeks_expected_per_year = parameters.weeks_expected_per_year()
    if count_weeks > weeks_expected_per_year:
        return True
    return False

def semana_santa_weeker(year, weekday_calendar_starts):
    """
    This functions return us the week index of semana semana each year, 
    depending on which weekday it starts on.
    """
    
    saturday = hollydays.sabado_santo(year)

    calendar = main_day_weeker(year,weekday_calendar_starts)
    return calendar[saturday]

def easter_weeker(year, weekday_calendar_starts):
    """
    This functions return us the week index of easter each year,
    depending on which weekday it starts on.
    """
    saturday = hollydays.easter_saturday(year)
        
    calendar = main_day_weeker(year,weekday_calendar_starts)
    return calendar[saturday]

def thanksgiving_weeker(year, weekday_calendar_starts):
    """
    This functions return us the week index of thanksgiving each year,
    depending on which weekday it starts on.
    """
    date = hollydays.thanksgiving(year)
    calendar = main_day_weeker(year,weekday_calendar_starts)
    return calendar[date]