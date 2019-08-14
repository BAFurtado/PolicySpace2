"""
This module is where the real estate market takes effect.
Definitions on ownership and actual living residence is made.
"""
from .rental import RentalMarket


class HousingMarket:
    def __init__(self):
        self.rental = RentalMarket()
        self.looking = list()
        self.on_sale = list()
        self.for_rent = list()
        self.purchasing = list()
        self.renting = list()

    def update_on_sale(self, sim):
        for house in sim.houses.values():
            # Updating all houses values every month
            house.update_price(sim.regions)

            if not house.is_occupied:
                if house not in self.on_sale:
                    self.on_sale.append(house)
        # Ranking houses by price and families by saving
        # Sorting. Those houses cheaper first
        self.on_sale.sort(key=lambda h: h.price, reverse=True)

    def make_move(self, family, house, sim):
        # Make the move
        old_r_id = family.region_id
        family.move_out()
        family.move_in(house)
        sim.update_pop(old_r_id, family.region_id)

    def allocate_houses(self, sim):

        self.update_on_sale(sim)

        """Allocation of houses on the market"""
        families = sim.families
        regions = sim.regions

        # BUYING FAMILIES
        # Select sample of families looking for houses at this time, given parameter
        self.looking = sim.seed.sample(list(families.values()),
                                       int(len(families) * sim.PARAMS['PERCENTAGE_CHECK_NEW_LOCATION']))

        # If empty lists, stop procedure
        if not self.looking or not self.on_sale:
            return

        # Sorting. Those with less savings first
        self.looking.sort(key=lambda f: f.savings, reverse=True)

        # Minimum price on market
        minimum_price = self.on_sale[-1].price

        # Family with larger savings
        maximum_purchasing_power = self.looking[0].savings

        # Families that can afford to buy, remain on the list
        # Those without funds, try the rental market.
        # TODO: Introduce other decision mechanisms

        [self.purchasing.append(f) if f.savings > minimum_price else self.renting.append(f)
         for f in self.looking]

        # Extract houses to rental market from sales pool
        self.rental = sim.seed.sample(self.on_sale, len(self.renting))
        self.on_sale[:] = [h for h in self.on_sale if h not in self.for_rent]

        # Call Rental market ###############################################################
        if self.renting and self.for_rent:
            self.rental.rental_market(self.renting, self.for_rent, sim)

        self.on_sale[:] = [h for h in self.on_sale if h.price < maximum_purchasing_power]

        # Second check. If empty lists, stop procedure
        if not self.purchasing or not self.on_sale:
            return

        # For each family
        # Necessary to save in another list because you cannot delete an element while iterating over the list

        for family in self.purchasing:
            for house in self.on_sale:
                s = family.savings
                p = house.price

                if s > p:
                    # Then PRICE is established as the average of the two
                    price = (s + p) / 2

                    # Buy
                    # Withdraw money from buying family and distribute back the difference
                    family.update_balance(family.grab_savings(sim.central,
                                                              sim.clock.year,
                                                              ((sim.clock.months % 12) + 1)) - price)

                    # Collect taxes on transaction
                    taxes = price * sim.PARAMS['TAX_ESTATE_TRANSACTION']
                    regions[house.region_id].collect_taxes(taxes, 'transaction')

                    # Deposit money on selling family
                    families[house.owner_id].update_balance(price - taxes)

                    # Transfer ownership
                    families[house.owner_id].owned_houses.remove(house)
                    house.owner_id = family.id

                    family.owned_houses.append(house)

                    # Decision on moving
                    self.decision(family, sim)

                    # Cleaning up list
                    self.on_sale[:] = [h for h in self.on_sale if h is not house]

                    # This family has solved its problem. Go to next family
                    break

                # Shortening the loop, in case the savings won't be enough for available houses
                elif s < self.on_sale[-1].price:
                    break

    def decision(self, family, sim):
        """A family decides which house to move into"""
        options = family.owned_houses
        prop_employed = family.prop_employed()
        if len(options) > 1:
            # Sort by price, which captures quality, size, and location
            # This puts the cheapest house first
            options.sort(key=lambda h: h.price, reverse=False)
            # If family does not live in the worst house
            # and no one in the family is employed, move to the worst house
            if options[0].family_id != family.id and prop_employed == 0:
                self.make_move(family, options[0], sim)

            # Else if they live in the worst house
            # but are not all unemployed, move to a better house
            elif options[0].family_id == family.id and prop_employed > 0:
                self.make_move(family, options[-1], sim)
