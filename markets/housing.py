"""
This module is where the real estate market takes effect.
Definitions on ownership and actual living residence is made.
"""


def allocate_houses(sim):
    """Allocation of houses on the market"""
    houses = sim.houses
    families = sim.families
    regions = sim.regions

    # Selling market, Select available houses, not_occupied and update values
    # EMPTY AVAILABLE HOUSES
    on_sale = []
    for house in houses.values():
        if not house.is_occupied:
            house.update_price(regions)
            on_sale.append(house)

    # BUYING FAMILIES
    # Select sample of families looking for houses at this time, given parameter
    family_on_the_look = sim.seed.sample(list(families.keys()),
                                         int(len(families) * sim.PARAMS['PERCENTAGE_CHECK_NEW_LOCATION']))

    # # Given the endogenous formation of families, some families may contain no members, excluding those
    family_on_the_look = [families[f] for f in family_on_the_look if families[f].members]

    if not family_on_the_look or not on_sale:
        return

    # Ranking houses by price and families by saving
    # Sorting. Those houses cheaper first
    on_sale.sort(key=lambda h: h.price, reverse=True)
    # Sorting. Those with less savings first
    family_on_the_look.sort(key=lambda f: f.savings, reverse=True)

    # Minimum price on market
    minimum_price = on_sale[-1].price

    # Family with larger savings
    maximum_purchasing_power = family_on_the_look[0].savings

    # Shortening the lists
    family_on_the_look = [f for f in family_on_the_look if f.savings > minimum_price]
    on_sale = [h for h in on_sale if h.price < maximum_purchasing_power]

    if not family_on_the_look or not on_sale:
        return

    # For each family
    for family in family_on_the_look:
        move = False
        to_remove = []
        for house in on_sale:
            if house in to_remove:
                # skip to next house
                continue

            s = family.savings
            p = house.price
            if s > p:
                # Then PRICE is established as the average of the two
                price = (s + p) / 2

                # Buy
                # Withdraw money from buying family
                family.update_balance(family.grab_savings() - price)

                # Collect taxes on transaction
                taxes = price * sim.PARAMS['TAX_ESTATE_TRANSACTION']
                regions[house.region_id].collect_taxes(taxes, 'transaction')

                # Deposit money on selling family
                families[house.owner_id].update_balance(price - taxes)

                old_owner = house.owner_id

                # Transfer ownership
                house.owner_id = family.id
                families[old_owner].owned_houses.remove(house)
                family.owned_houses.append(house)

                # Update house index
                sim.house_index[old_owner].remove(house)
                sim.house_index[house.owner_id].add(house)

                # Withdraw from available houses
                to_remove.append(house)

                # Decision on moving
                destin, move = decision(family, houses)
                break

        # Make the move
        if move:
            old_r_id = family.region_id
            family.move_out()
            family.move_in(house)
            sim.update_pop(old_r_id, family.region_id)

        for house in to_remove:
            on_sale.remove(house)


def decision(family, houses):
    """A family decides which house to move into"""
    options = [h for h in houses.values() if h.owner_id == family.id]
    prop_employed = family.prop_employed()
    if len(options) > 1:
        # Sort by price, which captures quality, size, and location
        # This puts the cheapest house first
        options.sort(key=lambda h: h.price, reverse=False)
        # If family does not live in the worst house
        # and no one in the family is employed, move to the worst house
        if options[0].family_id != family.id and prop_employed == 0:
            move = True
            destin = options[0]

        # Else if they live in the worst house
        # but are not all unemployed, move to a better house
        elif options[0].family_id == family.id and prop_employed > 0:
            move = True
            destin = options[-1]
        else:
            move = False
            destin = None
    else:
        move = False
        destin = None
    return destin, move
