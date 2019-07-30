import math


class Clock:
    """
    Months are considered to contain 21 working days
    As such, weekends (and holidays) are not depicted in the model
    Obviously, if of interest, this could be easily changed
    """
    DAYS_PER_MONTH = 21
    DAYS_PER_QUARTER = 63
    DAYS_PER_YEAR = 252

    def __init__(self, days=0):
        self.days = days

    @property
    def time(self):
        return self.days, self.months, self.quarters, self.years

    @property
    def year(self):
        return 2000 + self.years

    def tick(self):
        self.day += 1

    @property
    def months(self):
        return math.ceil(self.days / self.DAYS_PER_MONTH)

    @property
    def quarters(self):
        return math.ceil(self.days / self.DAYS_PER_QUARTER)

    @property
    def years(self):
        return math.ceil(self.days / self.DAYS_PER_YEAR)

    @property
    def new_month(self):
        return self.days % self.DAYS_PER_MONTH == 0

    @property
    def new_quarter(self):
        return self.days % self.DAYS_PER_QUARTER == 0

    @property
    def new_year(self):
        return self.days % self.DAYS_PER_YEAR == 0

    def __repr__(self):
        return '%.1d year(s), %.1d quarter(s), ' \
               '%.1d month(s), %.1d, day(s)' % (self.years, self.quarters, self.months, self.days)
