import datetime
from math import ceil


class Clock:
    """
    Clock has been updated to generate actual date times
    """

    def __init__(self, days=datetime.date(2000, 1, 1)):
        self.days = days

    @property
    def time(self):
        return self.days.day, self.days.month, self.quarters, self.year

    @property
    def year(self):
        return self.days.year

    def tick(self):
        self.days + datetime.timedelta(days=1)

    @property
    def months(self):
        return self.days.month

    @property
    def quarters(self):
        return "Q%d_%d" % (ceil(self.days.month / 3), self.days.year)

    @property
    def new_month(self):
        return self.days.day == 1

    @property
    def new_quarter(self):
        return (self.days.day == 1) and (self.days.month in {1, 5, 9})

    @property
    def new_year(self):
        return (self.days.day == 1) and (self.days.month == 1)

    def __repr__(self):
        return '{}'.format(self.days)
