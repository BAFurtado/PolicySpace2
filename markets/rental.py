

class RentalMarket:

    def __init__(self, sim):
        self.unoccupied = list()

    def update_list(self, sim, to_rent=None):
        if to_rent:
            self.unoccupied = to_rent
        else:
            self.unoccupied = [h for h in sim.houses.values() if h.family_id is None]

    def rental_market(self, families, sim, to_rent=None):
        self.update_list(sim, to_rent)
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
                        sim.housing.make_move(family, house, sim)
                        # Save information of rental on house
                        house.rental = True
                        house.rent_data = price, sim.clock.days
                        # This family is done
                        break

    def collect_rent(self, house, family):
        pass
