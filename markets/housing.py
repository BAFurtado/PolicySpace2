"""
This module is where the real estate market takes effect.
Definitions on ownership and actual living residence is made.
"""
from numpy import median
from .rentmarket import RentalMarket, collect_rent


class HousingMarket:
    def __init__(self):
        self.rental = RentalMarket()
        self.for_sale = list()

    @staticmethod
    def process_monthly_rent(sim):
        """ Collection of rental payment due made by households that are renting """
        to_pay_rent = [h for h in sim.houses.values() if h.rent_data is not None]
        collect_rent(to_pay_rent, sim)

    def update_for_sale(self, sim):
        # Using neighborhood_wealth effect as attractive for prices
        neighborhood_wealth = dict()
        if sim.PARAMS['NEIGHBORHOOD_EFFECT']:
            for key in sim.regions.keys():
                neighborhood_wealth[key] = median([f.get_permanent_income()
                                                   for f in sim.families.values()
                                                   if f.house.region_id == key])
            _max, _min = max(neighborhood_wealth.values()), min(neighborhood_wealth.values())
            neighborhood_wealth = {k: (v - _min) / (_max - _min) for k, v in neighborhood_wealth.items()}

        for house in sim.houses.values():
            # Updating all houses values every month
            house.update_price(sim.regions,
                               sim.PARAMS['ON_MARKET_DECAY_FACTOR'],
                               sim.PARAMS['MAX_OFFER_DISCOUNT'],
                               neighborhood_wealth,
                               sim.PARAMS['NEIGHBORHOOD_EFFECT'])

            # If house is empty, and not already on sales list, add it to houses on the market and start counting
            # However, if house is empty and had been empty count one extra month
            if not house.is_occupied:
                if house not in self.for_sale:
                    house.on_market = 0
                    self.for_sale.append(house)
                else:
                    house.on_market += 1

        # Order houses by price most expensive first
        # self.for_sale.sort(key=lambda h: h.price, reverse=True)

    def housing_market(self, sim):
        """Start of the housing market"""
        # Select sample of families looking for houses at this time, given parameter, at the same time,
        # clear list of past houses for sale
        looking = sim.seed.sample(list(sim.families.values()),
                                  int(len(sim.families) * sim.PARAMS['PERCENTAGE_ENTERING_ESTATE_MARKET']))

        # Update prices of all houses in the simulation and status 'on_market' or not
        self.update_for_sale(sim)

        # Run the market
        self.allocate_houses(sim, looking)

    def allocate_houses(self, sim, looking):
        """ This function manipulates both lists for families that are purchasing or renting
            and houses that are available for rent or purchase.
            Families "looking" for houses become either "purchasing" or "renting"
            Houses are either on "for_sale" or "for_rent"
        """
        # If empty lists, stop procedure
        if not looking or not self.for_sale:
            return

        # Families check the bank for potential credit
        for f in looking:
            f.savings_with_loan = f.savings + sim.central.sum_deposits(f) + sim.central.max_loan(f)[0]

        # Sorting. Those with larger savings first
        looking.sort(key=lambda fam: fam.savings_with_loan, reverse=True)

        # Family with the largest savings
        family_maximum_purchasing_power = looking[0].savings_with_loan

        # Only rent from families, not firms
        family_houses_for_rent = [h for h in self.for_sale if h.family_owner]
        for_rent = sim.seed.sample(family_houses_for_rent,
                                   int(len(family_houses_for_rent) * sim.PARAMS['RENTAL_SHARE']))

        # Deduce houses that are to be rented from sales pool and
        # Restrict list of available houses to families' maximum paying ability
        for_sale = [h for h in self.for_sale if (h not in for_rent) and (h.price < family_maximum_purchasing_power)]

        # Create two (local) lists for those families that are Purchasing and those that are Renting
        if not for_sale:
            # Obviously, if there are no houses for sale, all unoccupied are for rentals.
            purchasing = []
            renting = looking
        else:
            # Manipulating lists. Getting list by sampling and by condition
            # Renting families is a share of those moving. Both rich and poor may rent.
            # Rationale for decision on renting in the literature is dependent on loads of future uncertainties.
            renting = sim.seed.sample(looking, int(len(looking) * sim.PARAMS['RENTAL_SHARE']))
            # The families that are not renting, want join the purchasing list
            willing = [f for f in looking if f not in renting]
            # Minimum price on market
            minimum_price = for_sale[-1].price
            # However, families that cannot afford to buy, will have also have to join the renting list...
            [renting.append(f) for f in willing if f.savings_with_loan < minimum_price]
            # ... and only those who remain will join the purchasing list
            purchasing = [f for f in willing if f not in renting]

        # Call Rental market ###############################################################
        if renting and for_rent:
            self.rental.rental_market(renting, sim, for_rent)

        # Second check. If empty lists, stop procedure
        if not purchasing or not for_sale:
            return

        self.sales_market(sim, purchasing, for_sale)

    def sales_market(self, sim, purchasing, for_sale):
        # Proceed to Sales market ###########################################################
        vacancy = sim.stats.calculate_house_vacancy(sim.houses, False)
        # For each family
        for family in purchasing:
            self.negotiating(family, for_sale, sim, vacancy)

    def negotiating(self, family, for_sale, sim, vacancy):
        savings = family.savings + sim.central.sum_deposits(family)
        savings_with_mortgage = family.savings_with_loan
        my_market = sim.seed.sample(for_sale, min(len(for_sale), int(sim.PARAMS['SIZE_MARKET']) * 3))
        my_market.sort(key=lambda h: h.price, reverse=True)
        # If family has enough funds, or successfully gets a loan, it buys the first house of the stack.
        # Only houses that are within savings or savings plus loan compose each family individual market
        # Otherwise, it tries another one.
        for house in my_market:
            cash = 0
            p = house.price
            # A large empty market makes those selling ask for a lower price
            if sim.PARAMS['OFFER_SIZE_ON_PRICE']:
                p = p * (1 - vacancy)
            # If savings is enough, then price is established as the average of the two
            if savings > p:
                # Restrict OFFERs to a maximum of 30% threshold
                if savings/p > sim.PARAMS['CAPPED_TOP_VALUE']:
                    price = p * sim.PARAMS['CAPPED_TOP_VALUE'] / 2
                else:
                    price = (savings + p) / 2
            # If not, check whether loan can help
            elif savings_with_mortgage > p:
                if savings_with_mortgage/p > 1.3:
                    price = p * 1.15
                else:
                    price = (savings_with_mortgage + p) / 2
                # Get loan to make up the difference
                loan_amount = price - savings
                # Check macroprudential policy. If loan to value is above set value, no loan, leave the market.
                if loan_amount / price > sim.PARAMS['MAX_LOAN_TO_VALUE']:
                    return
                # Attempt to actually get the loan from the bank
                success = sim.central.request_loan(family, house, loan_amount)
                if not success:
                    # Just one shot at getting a loan
                    return
                cash += loan_amount
            elif savings/p > sim.PARAMS['CAPPED_LOW_VALUE']:
                if sim.seed.random() < vacancy:
                    price = savings
                else:
                    continue
            else:
                continue
            # Withdraw the money of buying family from the bank and from savings
            cash += family.grab_savings(sim.central, sim.clock.year, sim.clock.months)
            change = round(cash - price, 2)

            # Register the transaction, collect taxes and consider moving
            self.notarial_procedures(family, house, price, change, sim)
            # if the procedures have come this far, it means loan or price have being agreed upon.
            # Clean for_sale list.
            self.for_sale[:] = [h for h in for_sale if h is not house]
            # Having bought a house, then it can move on to the next family
            return

    def notarial_procedures(self, family, house, price, change, sim):
        # Withdraw money from buying family and distribute back the difference
        family.update_balance(change)
        # Collect taxes on transaction
        taxes = price * sim.PARAMS['TAX_ESTATE_TRANSACTION']
        sim.regions[house.region_id].collect_taxes(taxes, 'transaction')

        if house.family_owner:
            # Deposit money on selling family account
            assert (house.owner_id in sim.firms) is False
            sim.families[house.owner_id].update_balance(price - taxes)
            # Transfer ownership
            sim.families[house.owner_id].owned_houses.remove(house)

        # Firm owner
        else:
            # Deposit money on selling firm
            sim.firms[house.owner_id].update_balance(price - taxes, sim.PARAMS['CONSTRUCTION_ACC_CASH_FLOW'],
                                                     sim.clock.days)
            # Transfer ownership
            sim.firms[house.owner_id].houses_for_sale.remove(house)

        # Finish notarial procedures
        house.owner_id = family.id
        house.family_owner = True
        family.owned_houses.append(house)
        house.on_market = 0

        # Decision on moving
        if family.house is None:
            # If previously without a house, move into the new acquired one
            self.make_move(family, house, sim)
        else:
            # Check if there is more than one option and choose
            self.decision(family, sim)

    def decision(self, family, sim):
        """A family decides which house to move into"""
        # Options include only empty houses (those ot rented) or currently occupied by the same family.
        options = [h for h in family.owned_houses if (h.family_id is None) or (h.family_id == family.id)]

        # If options is size 1, it means the only owned house is the one the family currently lives in.
        if len(options) > 1:
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
            family.move_out(sim.funds)
        family.move_in(house)
        # Only after simulation has begun, it is necessary to update population, not at generation time
        try:
            if sim.mun_pops:
                sim.update_pop(old_r_id, family.region_id)
        except AttributeError:
            pass
