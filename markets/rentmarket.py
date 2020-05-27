import inspect


class RentalMarket:

    def __init__(self):
        self.unoccupied = list()

    def update_list(self, sim, to_rent=None):
        if to_rent is not None:
            self.unoccupied = to_rent
        else:
            # Only rent from families, not firms
            self.unoccupied = [h for h in sim.houses.values()
                               if h.family_id is None and h.family_owner]

    def rental_market(self, families, sim, to_rent=None):
        self.update_list(sim, to_rent)
        teste = inspect.stack()
        print(teste[1][3], teste[2][3], teste[3][3])
        # Sorting. Those with less savings first
        if families:
            families.sort(key=lambda f: f.savings, reverse=True)
            self.unoccupied.sort(key=lambda h: h.price, reverse=True)

            # Match pairs
            for family in families:
                for house in self.unoccupied:
                    # Just checking
                    if house.family_id is None:
                        # Define price
                        price = house.price * sim.PARAMS['INITIAL_RENTAL_PRICE']
                        self.make_move(family, house, sim)
                        # Save information of rental on house
                        house.rent_data = price, sim.clock.days
                        # This family is done
                        break

    def collect_rent(self, houses, sim):
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

    def make_move(self, family, house, sim):
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
