from datetime import datetime, timedelta

def gauss_easter(year):
    """
    Gauss' model for calculating the date of easter's beginning
    """
    a = year % 19
    b = year // 100
    c = year % 100
    d = b // 4
    e = b % 4
    f = (b + 8) // 25
    g = (b - f + 1) // 3
    h = (19 * a + b - d - g + 15) % 30
    i = c // 4
    k = c % 4
    l = (32 + 2 * e + 2 * i - h - k) % 7
    m = (a + 11 * h + 22 * l) // 451
    easter_month = (h + l - 7 * m + 114) // 31
    easter_day = ((h + l - 7 * m + 114) % 31) + 1
    return datetime(year, easter_month, easter_day)

# ========== Mexican Holidays ==========
def sabado_santo(year):
    """
    Function for calculating Sabado santo (Samana Santa's Saturday)
    """
    return gauss_easter(year) - timedelta(days=1)

def easter_saturday(year):
    """
    Function for calculation easter's saturday.
    """
    return gauss_easter(year) + timedelta(days=6)

def new_year(current_year):
    return datetime(current_year, 1, 1)

def christmas(current_year):
    return datetime(current_year, 12, 25)

def constitution_day(current_year):
    """
    First Monday of each February.
    """
    for day in range(1, 8):
        date = datetime(current_year, 2, day)
        if date.weekday() == 0:
            return date

def benito_juarez_birthday(current_year):
    """
    Third Monday of each March.
    """
    count = 0
    for day in range(1, 32):
        date = datetime(current_year, 3, day)
        if date.weekday() == 0:
            count += 1
            if count == 3:
                return date

def mexican_revolution_day(current_year):
    """
    Third monday of november in each year.
    """
    count = 0
    for day in range(1, 31):
        date = datetime(current_year, 11, day)
        if date.weekday() == 0:
            count += 1
            if count == 3:
                return date

def father_day(current_year):
    """
    Third Sunday of each june.
    """
    count = 0
    for day in range(1, 31):
        date = datetime(current_year, 6, day)
        if date.weekday() == 6:
            count += 1
            if count == 3:
                return date

def valentines_day(current_year):
    return datetime(current_year, 2, 14)

def mothers_day(current_year):
    return datetime(current_year, 5, 10)

def work_day(current_year):
    return datetime(current_year, 5, 1)

def independence_day(current_year):
    return datetime(current_year, 9, 16)

# ========== US Holidays ==========
def thanksgiving(current_year):
    """
    Fourth thursday of each november
    """
    count = 0
    for day in range(1, 31):
        date = datetime(current_year, 11, day)
        if date.weekday() == 3:
            count += 1
            if count == 4:
                return date

def mlk_day(current_year):
    """
    Third Monday of each January.
    """
    count = 0
    for day in range(1, 32):
        date = datetime(current_year, 1, day)
        if date.weekday() == 0:  # Monday
            count += 1
            if count == 3:
                return date

def presidents_day(current_year):
    """
    Third Monday of each February.
    """
    count = 0
    for day in range(1, 29):
        date = datetime(current_year, 2, day)
        if date.weekday() == 0:  # Monday
            count += 1
            if count == 3:
                return date

def memorial_day(current_year):
    """
    Last Monday of each May.
    """
    last_monday = None
    for day in range(1, 32):
        date = datetime(current_year, 5, day)
        if date.weekday() == 0:  # Monday
            last_monday = date
    return last_monday

def juneteenth(current_year):
    """
    June 19th.
    """
    return datetime(current_year, 6, 19)

def us_independence_day(current_year):
    """
    July 4th.
    """
    return datetime(current_year, 7, 4)

def us_labor_day(current_year):
    """
    First Monday of each September.
    """
    for day in range(1, 8):
        date = datetime(current_year, 9, day)
        if date.weekday() == 0:  # Monday
            return date

# ========= Hollydays Dics ====
def regular_hollydays_dic(current_year):
    # This dictionary now contains an 'origin' key for styling
    holidays = {
        # Mexican Holidays
        sabado_santo(current_year): {"name": "Holy Week Weekend", "origin": "MX"},
        easter_saturday(current_year): {"name": "Easter Weekend", "origin": "MX"},
        new_year(current_year): {"name": "New Year's Day", "origin": "MX"},
        christmas(current_year): {"name": "Christmas Day", "origin": "MX"},
        christmas(current_year - 1): {"name": "Christmas Day", "origin": "MX"},
        constitution_day(current_year): {"name": "Mexican Constitution Weekend", "origin": "MX"},
        benito_juarez_birthday(current_year): {"name": "Benito Juárez Weekend", "origin": "MX"},
        mexican_revolution_day(current_year): {"name": "Mexican Revolution Weekend", "origin": "MX"},
        father_day(current_year): {"name": "Father's Day", "origin": "MX"},
        valentines_day(current_year): {"name": "Valentine's Day", "origin": "MX"},
        mothers_day(current_year): {"name": "Mother's Day", "origin": "MX"},
        work_day(current_year): {"name": "Labor Day", "origin": "MX"},
        independence_day(current_year): {"name": "Mexican Independence Day", "origin": "MX"},
        
        # US Holidays
        mlk_day(current_year): {"name": "Martin Luther King Jr. Day", "origin": "US"},
        presidents_day(current_year): {"name": "Presidents' Day", "origin": "US"},
        memorial_day(current_year): {"name": "Memorial Day", "origin": "US"},
        juneteenth(current_year): {"name": "Juneteenth", "origin": "US"},
        us_independence_day(current_year): {"name": "U.S. Independence Day", "origin": "US"},
        us_labor_day(current_year): {"name": "Labor Day", "origin": "US"},
        thanksgiving(current_year): {"name": "Thanksgiving Day", "origin": "US"},
    }
    return holidays

def snow_hollydays_dic(current_year):
    # This dictionary now contains an 'origin' key for styling
    holidays = {
        # Mexican Holidays
        sabado_santo(current_year + 1): {"name": "Holy Week Weekend", "origin": "MX"},
        easter_saturday(current_year + 1): {"name": "Easter Weekend", "origin": "MX"},
        new_year(current_year + 1): {"name": "New Year's Day", "origin": "MX"},
        christmas(current_year): {"name": "Christmas Day", "origin": "MX"},
        constitution_day(current_year + 1): {"name": "Mexican Constitution Weekend", "origin": "MX"},
        benito_juarez_birthday(current_year + 1): {"name": "Benito Juárez Weekend", "origin": "MX"},
        mexican_revolution_day(current_year): {"name": "Mexican Revolution Weekend", "origin": "MX"},
        father_day(current_year + 1): {"name": "Father's Day", "origin": "MX"},
        valentines_day(current_year + 1): {"name": "Valentine's Day", "origin": "MX"},
        mothers_day(current_year + 1): {"name": "Mother's Day", "origin": "MX"},
        work_day(current_year + 1): {"name": "Labor Day", "origin": "MX"},
        independence_day(current_year): {"name": "Mexican Independence Day", "origin": "MX"},
        independence_day(current_year + 1): {"name": "Mexican Independence Day", "origin": "MX"},
        
        # US Holidays
        thanksgiving(current_year): {"name": "Thanksgiving Day", "origin": "US"},
        mlk_day(current_year + 1): {"name": "Martin Luther King Jr. Day", "origin": "US"},
        presidents_day(current_year + 1): {"name": "Presidents' Day", "origin": "US"},
        memorial_day(current_year + 1): {"name": "Memorial Day", "origin": "US"},
        juneteenth(current_year + 1): {"name": "Juneteenth", "origin": "US"},
        us_independence_day(current_year + 1): {"name": "U.S. Independence Day", "origin": "US"},
        us_labor_day(current_year): {"name": "Labor Day", "origin": "US"},
    }
    return holidays

# ======== Test Block ========
if __name__ == "__main__":
    print(thanksgiving(2027))