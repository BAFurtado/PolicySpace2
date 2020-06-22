def make_move(family, house, sim):
    # Make the move
    old_r_id = family.region_id
    if family.house:
        family.move_out()
    family.move_in(house)
    # Only after simulation has begun, it is necessary to update population, not at generation time
    try:
        if sim.mun_pops:
            sim.update_pop(old_r_id, family.region_id)
    except AttributeError:
        pass


def collect_rent(houses, sim):
    for house in houses:
        rent = house.rent_data[0]
        tenant = sim.families[house.family_id]
        landperson = sim.families[house.owner_id]

        # Collect taxes on transaction
        taxes = rent * sim.PARAMS['TAX_LABOR']
        sim.regions[house.region_id].collect_taxes(taxes, 'labor')

        # Withdraw money from family members
        money = sum(m.grab_money() for m in tenant.members.values())
        # Deposit change
        tenant.update_balance(money - rent)

        # Deposit money on selling family
        landperson.update_balance(rent - taxes)


class RentalMarket:

    def __init__(self):
        self.unoccupied = list()

    def update_list(self, sim, to_rent=None):
        if to_rent is not None:
            self.unoccupied = to_rent
        else:
            # Only rent from families, not firms
            self.unoccupied = [h for h in sim.houses.values() if h.family_id is None and h.family_owner]

    def rental_market(self, families, sim, to_rent=None):
        # TODO: improve general rationality for wishing to enter the market
        # TODO: sales -- excess wealth
        # TODO: rent -- burdensome rent
        base_price = sim.PARAMS['INITIAL_PRICE_RENT']
        self.update_list(sim, to_rent)
        if families:
            families.sort(key=lambda f: f.last_permanent_income, reverse=True)
            for family in families:
                # Matching
                my_market = sim.seed.sample(self.unoccupied, min(len(self.unoccupied), sim.PARAMS['SIZE_MARKET'] * 3))
                in_budget = [h for h in my_market if h.price * base_price < family.last_permanent_income]
                if in_budget:
                    sim.seed.shuffle(in_budget)
                    house = in_budget[0]
                    price = house.price * base_price
                else:
                    my_market.sort(key=lambda h: h.price)
                    house = my_market[0]
                    # Ask for reduced price, because out of budget. Varying according to number of available houses
                    price = house.price * (base_price - len(my_market) / 100000)
                # Just checking
                if house.family_id is None:
                    # Define price
                    make_move(family, house, sim)
                    # Save information of rental on house
                    house.rent_data = price, sim.clock.days
