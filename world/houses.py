import math
from collections import defaultdict


def update_housing_supply(sim):
    house_vacancy = sim.PARAMS['HOUSE_VACANCY']
    region_houses = defaultdict(int)
    region_vacancies = defaultdict(int)
    for h in sim.houses.values():
        # house is vacant
        if h.family_id is None:
            region_vacancies[h.region_id] += 1
        region_houses[h.region_id] += 1

    for region_id, n_houses in region_houses.items():
        region = sim.regions[region_id]
        vacant = region_vacancies[region_id]
        p_vacant = vacant/n_houses
        if p_vacant < house_vacancy:
            n_new = ((house_vacancy * n_houses) - vacant)/(1 - house_vacancy)
            n_new = math.ceil(n_new)
            new_houses = sim.generator.create_houses(n_new, region)
            sim.generator.randomly_assign_houses(new_houses.values(), sim.families.values())
