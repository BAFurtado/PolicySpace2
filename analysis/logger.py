import conf
import logging


class Logger:
    """Manages simulation logging"""
    def __init__(self, id):
        self.logger = logging.getLogger('SIM:{}'.format(id))

    def log_outcomes(self, sim):
        print('\nAgents out of the game:')
        for agent in sim.grave[:10]:
            print(agent)

        print('\nFamilies')
        for item in list(sim.families.values())[:10]:
            print(item)

        print('\nFirms')
        for item in list(sim.firms.values())[:10]:
            print(item)

        print('\nHouses')
        for item in list(sim.houses.values())[:10]:
            print(item)

        print('\nFinal Results for the following municipalities for this simulation are:')
        for region in sim.regions.values():
            print(region)

    def info(self, msg):
        self.logger.info(msg)
