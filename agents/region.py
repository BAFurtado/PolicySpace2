import json
from shapely.geometry import Point, shape
from collections import defaultdict


class Region:
    """Collects taxes and applies to ameliorate quality of life"""

    def __init__(self, region, index=1, gdp=0, pop=0, total_commute=0, licenses=0):
        # A region is an OSGEO object that contains Fields and Geometry
        self.address_envelope = region.geometry().GetEnvelope()
        self.addresses = region.geometry()
        self.id = str(region.id)
        self.addresses = shape(json.loads(self.addresses.ExportToJson()))
        self.index = index
        self.gdp = gdp
        self.pop = pop
        self.licenses = licenses
        self.total_commute = total_commute
        self.cumulative_treasure = defaultdict(int)
        self.treasure = defaultdict(int)
        self.applied_treasure = defaultdict(int)
        self.registry = defaultdict(list)

    @property
    def license_price(self):
        return self.index

    @property
    def total_treasure(self):
        return sum(self.treasure.values())

    def collect_taxes(self, amount, key):
        self.treasure[key] += amount

    def save_and_clear_treasure(self):
        for key in self.treasure.keys():
            self.cumulative_treasure[key] += self.treasure[key]
            self.treasure[key] = 0

    def transfer_treasure(self):
        treasure = self.treasure.copy()
        self.save_and_clear_treasure()
        return treasure

    def update_index_pop(self, proportion_pop):
        """First term of QLI update, relative to change in population within its territory"""
        self.index *= proportion_pop

    def update_applied_taxes(self, amount, key):
        self.applied_treasure[key] += amount

    def update_index(self, value):
        """Index is updated per capita for current population"""
        self.index += value

    def __repr__(self):
        return '%s \n QLI: %.2f, \t GDP: %.2f, \t Pop: %s, Commute: %.2f' % (self.name, self.index, self.gdp,
                                                                             self.pop, self.total_commute)
