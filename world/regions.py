REGION_CACHE = {
    'centers': {},
    'firm_distances': {}
}


def distance_to_firm(region_id, firm):
    if firm.id not in REGION_CACHE['firm_distances'][region_id]:
        center = REGION_CACHE['centers'][region_id]
        REGION_CACHE['firm_distances'][region_id][firm.id] = center.distance(firm.address)
    return REGION_CACHE['firm_distances'][region_id][firm.id]
