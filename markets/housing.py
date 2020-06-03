"""
This module is where the real estate market takes effect.
Definitions on ownership and actual living residence is made.
"""
from .rentmarket import RentalMarket


class HousingMarket:
    def __init__(self):
        self.rental = RentalMarket()
        self.on_sale = list()

    def process_monthly_rent(self, sim):
        """ Collection of rental payment due made by households that are renting """
        to_pay_rent = [h for h in sim.houses.values() if h.rent_data is not None]
        self.rental.collect_rent(to_pay_rent, sim)

    def update_on_sale(self, sim):
        for house in sim.houses.values():
            # Updating all houses values every month
            house.update_price(sim.regions)

            # If house is empty, add not already on sales list, add it to houses on the market and start counting
            # However, if house is empty and had been empty count one extra month
            if not house.is_occupied:
                if house not in self.on_sale:
                    house.on_market = 0
                    self.on_sale.append(house)
                else:
                    house.on_market += 1

        # Order houses by price most expensive first
        self.on_sale.sort(key=lambda h: h.price, reverse=True)

    def housing_market(self, sim):
        """Allocation of houses on the market"""
        # Clear list of past houses for sale
        # BUYING FAMILIES: select sample of families looking for houses at this time, given parameter
        looking = sim.seed.sample(list(sim.families.values()),
                                  int(len(sim.families) * sim.PARAMS['PERCENTAGE_CHECK_NEW_LOCATION']))

        # Update prices of all houses in the simulation and status 'on_market' or not
        self.update_on_sale(sim)

        # Run the market
        self.allocate_houses(sim, looking)

    def allocate_houses(self, sim, looking, for_living_only=False):
        # If empty lists, stop procedure
        if not looking or not self.on_sale:
            return

        # Check the bank for potential credit
        for f in looking:
            f.savings_with_loan = f.savings + sim.central.max_loan(f)

        # Sorting. Those with larger savings first
        looking.sort(key=lambda fam: fam.savings_with_loan, reverse=True)

        # Family with the largest savings
        family_maximum_purchasing_power = looking[0].savings_with_loan

        # Only rent from families, not firms
        family_houses_for_rent = [h for h in self.on_sale if h.family_owner]
        for_rent = sim.seed.sample(family_houses_for_rent, int(len(family_houses_for_rent) * sim.PARAMS['RENTAL_SHARE']))

        # Deduce houses that are to be rented from sales pool
        self.on_sale = [h for h in self.on_sale if h not in for_rent]

        # Continue procedures for purchasing market. Restrict list of available houses to families' price range
        month_listing = [h for h in self.on_sale if h.price < family_maximum_purchasing_power]

        # Create two (local) lists for those families that are Purchasing and those that are Renting
        if not month_listing:
            # Obviously, if there are no houses for sale, all unoccupied are for rentals.
            purchasing = []
            renting = looking
        else:
            # Minimum price on market
            minimum_price = month_listing[-1].price
            # Families that can afford to buy, remain on the list
            # Those without funds, try the rental market.
            # TODO: increase the rationale for renting
            purchasing, renting = list(), list()
            [purchasing.append(f) if f.savings_with_loan > minimum_price else renting.append(f) for f in looking]

        # Call Rental market ###############################################################
        if renting and for_rent:
            self.rental.rental_market(renting, sim, for_rent)

        # Second check. If empty lists, stop procedure
        if not purchasing or not month_listing:
            return

        # Families in search of houses to buy
        # For each family
        # Necessary to save in another list because you cannot delete an element while iterating over the list
        for family in purchasing:
            for house in month_listing:
                # Skip houses that are being rented
                if for_living_only and house.rent_data is not None:
                    continue

                s = family.savings
                S = family.savings_with_loan
                p = house.price

                if s > p:
                    # Then PRICE is established as the average of the two
                    price = (s + p) / 2

                elif S > p:
                    price = (S + p) / 2

                else:
                    continue

                # Withdraw the money of buying family from the bank
                savings = family.grab_savings(sim.central,
                                              sim.clock.year,
                                              ((sim.clock.months % 12) + 1))

                # Get loan to make up the difference
                if savings < price:
                    loan_amount = price - savings
                    success = sim.central.request_loan(family, loan_amount, sim.seed)
                    change = 0
                    if not success:
                        continue
                else:
                    change = savings - price

                # Buying procedures
                # Withdraw money from buying family and distribute back the difference
                family.update_balance(change)
                # Collect taxes on transaction
                taxes = price * sim.PARAMS['TAX_ESTATE_TRANSACTION']
                sim.regions[house.region_id].collect_taxes(taxes, 'transaction')

                if house.family_owner:
                    # Deposit money on selling family account
                    sim.families[house.owner_id].update_balance(price - taxes)

                    # Transfer ownership
                    sim.families[house.owner_id].owned_houses.remove(house)

                # Firm owner
                else:
                    # Deposit money on selling firm
                    sim.firms[house.owner_id].update_balance(price - taxes, sim.PARAMS['CONSTRUCTION_ACC_CASH_FLOW'])

                    # Transfer ownership
                    sim.firms[house.owner_id].houses_inventory.remove(house)

                # Finish notarial procedures
                house.owner_id = family.id
                house.family_owner = True
                family.owned_houses.append(house)
                house.on_market = 0

                # Decision on moving
                self.decision(family, sim)

                # Cleaning up list
                month_listing[:] = [h for h in month_listing if h is not house]

                # This family has solved its problem. Go to next family
                break

        # Taking houses not sold this month into the next one
        self.on_sale = month_listing.copy()

    def decision(self, family, sim):
        """A family decides which house to move into"""
        # Leave only empty houses or currently occupied by the same family. Exclude rentals
        options = [h for h in family.owned_houses if (h.family_id is None) or (h.family_id == family.id)]

        # Include first-time mover
        if len(options) > 1 or family.house is None:
            # Sort by price, which captures quality, size, and location
            # This puts the cheapest house first
            options.sort(key=lambda h: h.price, reverse=False)
            # If family does not live in the worst house, but nobody is employed, move to the worst house
            prop_employed = family.prop_employed()
            if options[0].family_id != family.id and prop_employed == 0:
                self.make_move(family, options[0], sim)

            # Else if they live in the worst house, but at least one member is working, move to a better house
            elif options[0].family_id == family.id and prop_employed > 0:
                self.make_move(family, options[-1], sim)

    @staticmethod
    def make_move(family, house, sim):
        # Make the move
        old_r_id = family.region_id
        if family.house is not None:
            family.move_out()
        family.move_in(house)
        # Only after simulation has begun, it is necessary to update population, not at generation time
        try:
            if sim.mun_pops:
                sim.update_pop(old_r_id, family.region_id)
        except AttributeError:
            pass
