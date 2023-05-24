

def collect_rent(houses, sim):
    for house in houses:
        if house.rent_data:
            rent = house.rent_data[0]
            tenant = sim.families[house.family_id]
            landfamily = sim.families[house.owner_id]

            # Collect taxes on transaction
            taxes = rent * sim.PARAMS['TAX_LABOR']
            sim.regions[house.region_id].collect_taxes(taxes, 'labor')

            # If family belongs to rent policy programme, rent is paid for
            if tenant.rent_voucher:
                # Money has been deducted from municipal balance when voucher was conceded.
                payment = house.rent_data[0].copy()
                tenant.rent_voucher -= 1
            else:
                # Withdraw money from family members
                payment = sum(m.grab_money() for m in tenant.members.values())

            # If cash is not enough to pay rent
            if payment < rent:
                difference = rent - payment
                # Try savings
                if tenant.savings > difference:
                    # Withdraw difference from savings
                    tenant.savings -= difference
                    # And add to payemnt made
                    payment += difference
                # If money still not enough, try deposits in the bank
                if payment < rent:
                    if sim.central.wallet[tenant]:
                        cash = tenant.grab_savings(sim.central, sim.clock.year, sim.clock.months)
                        difference = payment - rent
                        if cash > difference:
                            tenant.savings += cash - difference
                            payment += difference
                        else:
                            payment += cash

            tenant.rent_default = 1 if payment == 0 else 0
            # Deposit change, if any. If payment is not enough in the end, landfamily gets the loss
            # and does not receive payment.
            if payment > rent:
                tenant.update_balance(round(payment - rent, 2))

            # Deposit money on landfamily. Taxes are due only when below payment made. Otherwise, no rent id owed.
            if payment > taxes:
                landfamily.update_balance(round(payment - taxes, 2))


class RentalMarket:

    def __init__(self):
        self.unoccupied = list()

    def update_list(self, sim, to_rent=None):
        if to_rent is not None:
            self.unoccupied = to_rent
        else:
            # Only rent from families, not firms
            self.unoccupied = [h for h in sim.houses.values() if h.family_id is None and h.family_owner]

    def maybe_move(self, family, house, price, sim):
        # Make the move
        old_r_id = family.region_id
        if family.house:
            # Families who are already settled, will move into rental only if better quality (that is, price)
            if family.house.price > house.price:
                return
            family.move_out(sim.funds)
        family.move_in(house)
        self.unoccupied.remove(house)
        # Save information of rental on house
        house.rent_data = price, sim.clock.days

        # Only after simulation has begun, it is necessary to update population, not at generation time
        try:
            if sim.mun_pops:
                sim.update_pop(old_r_id, family.region_id)
        except AttributeError:
            pass

    def rental_market(self, families, sim, to_rent=None):
        # Families that come here without a house (from marriage or immigration) need to move in or give up their plans
        # In that case, the list of houses is any unoccupied houses. Not a sample list separated for the rental market
        try:
            vacancy = sim.stats.calculate_house_vacancy(sim.houses, False)
        # When houses have not generated yet, at time 0
        except AttributeError:
            vacancy = 0
        base_proportion = sim.PARAMS['INITIAL_RENTAL_PRICE']
        self.update_list(sim, to_rent)
        if families:
            families.sort(key=lambda f: f.get_permanent_income(), reverse=True)
            for family in families:
                # Make sure list of vacant houses is up-to-date
                self.unoccupied = [h for h in self.unoccupied if h.family_id is None]
                # Matching
                my_market = sim.seed.sample(self.unoccupied, min(len(self.unoccupied),
                                                                 int(sim.PARAMS['SIZE_MARKET']) * 3))
                in_budget = [h for h in my_market if h.price * base_proportion < family.get_permanent_income()]
                if in_budget:
                    house = sim.seed.choice(in_budget)
                    price = house.price * base_proportion
                else:
                    if my_market:
                        my_market.sort(key=lambda h: h.price)
                        house = my_market[0]
                    elif self.unoccupied:
                        self.unoccupied.sort(key=lambda h: h.price)
                        house = self.unoccupied[0]
                    else:
                        # Family may go without a house. Try next month if there are vacancies
                        return
                    # Ask for reduced price, because out of budget. Varying according to number of available houses
                    price = house.price * round((base_proportion - (len(my_market) / 100000)), 6)
                if sim.PARAMS['OFFER_SIZE_ON_PRICE']:
                    vacancy_value = 1 - (vacancy * sim.PARAMS['OFFER_SIZE_ON_PRICE'])
                    if vacancy_value < sim.PARAMS['MAX_OFFER_DISCOUNT']:
                        vacancy_value = sim.PARAMS['MAX_OFFER_DISCOUNT']
                    price *= vacancy_value
                # Decision on moving. If no house, move, else, consider. If worse quality, give up on renting.
                self.maybe_move(family, house, price, sim)
