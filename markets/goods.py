
def consume(sim):
    firms = list(sim.firms.values())
    for family in sim.families.values():
        family.consume(firms, sim.regions, sim.PARAMS, sim.seed)
