

class RentalMarket:

    def rental_market(self, houses, families, sim):
        # Sorting. Those with less savings first
        families.sort(key=lambda f: f.savings, reverse=True)
        houses.sort(key=lambda h: h.price, reverse=True)

        # Match pairs
        for family in families:
            for house in houses:
                # Just checking
                if house.family_id is None:
                    # Define price
                    price = house.price * sim.PARAMS['INITIAL_RENTAL_PRICE']
                    sim.housing.make_move(house, family)
                    # Save information of rental on house
                    house.rental = True
                    house.rent_data = price, sim.clock.days
                    # This family is done
                    break
        print('Checking if families without house')

    def collect_rent(self, house, family):
        pass
