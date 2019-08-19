import datetime
from collections import defaultdict
from functools import partial


class House:
    """Holds the fixed households.
    They may have changing owners and changing occupancy."""

    def __init__(self, id, address, size, price, region_id, quality, family_id=None, owner_id=None):
        self.id = id
        self.address = address
        self.size = size
        self.price = price
        self.region_id = region_id
        self.quality = quality
        self.family_id = family_id # owner may be the occupant or the house may be vacant
        self.owner_id = owner_id
        self.rent = False
        self.rent_data = None

        # cache firm distances
        # since houses never change address
        self._firm_distances = {}

    def update_price(self, regions):
        """Compute new price for the house"""
        self.price = self.size * self.quality * regions[self.region_id].index

    def empty(self):
        """Remove current family"""
        self.family_id = None

    @property
    def is_occupied(self):
        return self.family_id is not None

    def pay_property_tax(self, sim):
        # Calculate taxes due of property paid in monthly in twelve installments
        tax = self.price * sim.PARAMS['TAX_PROPERTY'] / 12
        # Withdraw from paying family (current occupant or owner when unoccupied)
        # Only paying taxes when money is available
        if self.family_id is None:
            family = sim.families[self.owner_id]
        else:
            family = sim.families[self.family_id]
        if family.get_total_balance() > tax:
            family.update_balance(-tax)
            # Transfer to region
            sim.regions[self.region_id].collect_taxes(tax, 'property')

    def __repr__(self):
        return 'House ID %s, Family ID %s, Owner ID %s, Size %s, Price$ %s, Region %s' % (self.id, self.family_id,
                                                                                           self.owner_id, self.size,
                                                                                           self.price, self.region_id)

    def distance_to_firm(self, firm):
        if firm.id not in self._firm_distances:
            self._firm_distances[firm.id] = self.calculate_distance(firm.address)
        return self._firm_distances[firm.id]

    def calculate_distance(self, address):
        return self.address.distance(address)
