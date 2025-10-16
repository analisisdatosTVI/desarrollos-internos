from datetime import datetime
# =============  GLOBAL PARAMETERS ===============================
def number_of_fractions():
    return 8

def weeks_expected_per_year():
    return 365//7

# ============= REGULAR CALENDAR PARAMETERS =======================
def first_day_regular(current_year):
    return datetime(current_year,1,1)

# ============ SNOW BIRD CALENDAR PARAMETERS ======================
def first_day_snow(current_year):
    return datetime(current_year,9,22)