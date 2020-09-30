from enum import Enum
from math import e


class Owner(Enum):
    FAMILY = 0
    FIRM = 1


class House:
    """Holds the fixed households.
    They may have changing owners and changing occupancy."""
    Owner = Owner

    def __init__(self, _id, address, size, price, region_id, quality, family_id=None, owner_id=None,
                 owner_type=Owner.FAMILY):
        self.id = _id
        self.address = address
        self.size = size
        self.price = price
        self.region_id = region_id
        self.quality = quality
        # Owner may be the occupant or the house may be vacant or rented
        self.family_id = family_id
        self.owner_id = owner_id
        self.owner_type = owner_type
        self.rent_data = None
        self.on_market = 0
        # Cache firm distances, since houses never change address
        self._firm_distances = {}

    def update_price(self, regions, k, bound, neighborhood, value):
        """Compute new price for the house"""
        self.price = self.size * self.quality * regions[self.region_id].index
        # Update for too long in the market
        self.price *= (1 - bound) * e ** (k * self.on_market) + bound
        if neighborhood:
            # If neighborhood is 0 (False), price is unchanged.
            # If 1 (True) or higher, neighborhood effect is the value multiplier which increasingly impacts prices
            self.price *= (1 + value * neighborhood[self.region_id])

    def empty(self):
        """Remove current family"""
        self.family_id = None
        self.rent_data = None

    @property
    def is_occupied(self):
        return self.family_id is not None

    def pay_property_tax(self, sim):
        # Calculate taxes due of property paid in monthly in twelve installments
        tax = self.price * sim.PARAMS['TAX_PROPERTY'] / 12
        # Withdraw from paying family or firm (current occupant or owner when unoccupied)
        # Only paying taxes when money is available
        if self.family_id is None:
            if self.owner_type is House.Owner.FAMILY:
                payer = sim.families[self.owner_id]
            else:
                payer = sim.firms[self.owner_id]
        else:
            payer = sim.families[self.family_id]

        if payer.get_total_balance() > tax:
            payer.update_balance(-tax)

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

    @property
    def family_owner(self):
        return self.owner_type is Owner.FAMILY

    @family_owner.setter
    def family_owner(self, bool):
        if bool:
            self.owner_type = Owner.FAMILY
        else:
            self.owner_type = Owner.FIRM
