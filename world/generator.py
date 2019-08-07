"""
This is the module that uses input data to generate the artificial entities (instances)
used in the model. First, regions - the actual municipalities - are created using
shapefile input of real limits and real urban/rural areas.
Then, Agents are created and bundled into families, given population measures.
Then, houses and firms are created and families are allocated to their first houses.
"""
import os
import conf
import random
import shapely
import logging
import binascii
import pandas as pd
from .firms import FirmData
from .shapes import prepare_shapes
from .population import pop_age_data
from agents import Agent, Family, Firm, Region, House, Central

logger = logging.getLogger('generator')

# Necessary input Data
prop_urban = pd.read_csv('input/prop_urban_rural_2000.csv', sep=';', header=0,
                         decimal=',').apply(pd.to_numeric, errors='coerce')

idhm = pd.read_csv('input/idhm_1991_2010.txt', sep=',', header=0,
                   decimal='.').apply(pd.to_numeric, errors='coerce')
idhm = idhm.loc[idhm['year'] == conf.RUN['YEAR_TO_START']]

# load qualifications data, combining municipal-level with AP-level
quali = pd.read_csv('input/qualification_2000.csv', sep=';', header=0,
                    decimal=',').apply(pd.to_numeric, errors='coerce')
quali = quali.drop('Unnamed: 0', 1)

# rename from cod_mun b/c we may also have
# AP codes, not just municipal codes
quali.rename(columns={'cod_mun': 'code'}, inplace=True)
quali_aps = pd.read_csv('input/qualification_APs.csv', sep=';', header=0,
                      decimal=',').apply(pd.to_numeric, errors='coerce')
for code, group in quali_aps.groupby('AREAP'):
    group = group[['qual', 'perc_qual_AP']]
    row = {'code': code}
    for idx, qual, percent in group.to_records():
        row[str(qual)] = percent
    row = [row.get(col, 0) for col in quali.columns]
    quali.loc[quali.shape[0]] = row
quali.set_index('code', inplace=True)
quali_sum = quali.cumsum(axis=1)


single_ap_muns = pd.read_csv('input/single_aps.csv', sep=';')
single_ap_muns = single_ap_muns['mun_code'].tolist()


def gen_id(bytes=6):
    """Generate a random id that should
    avoid collisions"""
    return binascii.hexlify(os.urandom(bytes)).decode('utf8')


class Generator:
    def __init__(self, sim):
        self.sim = sim
        self.seed = sim.seed
        self.urban, self.shapes = prepare_shapes(sim.geo)
        self.firm_data = FirmData()
        self.central = Central('central')

    def create_regions(self):
        """Create regions"""
        regions = {}
        for item in self.shapes:
            r = Region(item)

            # mun code is always first 7 digits of id,
            # if it's a municipality shape or an AP shape
            mun_code = r.id[:7]
            r.index = idhm[idhm['cod_mun'] == int(mun_code)]['idhm'].iloc[0]
            regions[r.id] = r
        return regions

    def create_all(self, regions):
        """Based on regions and population data,
        create agents, families, houses, and firms"""
        my_agents = {}
        my_families = {}
        my_houses = {}
        my_firms = {}

        for region_id, region in regions.items():
            logger.info('Generating region {}'.format(region_id))
            num_houses = 0

            regional_agents = self.create_agents(region)
            num_houses += len(regional_agents)
            for agent in regional_agents.keys():
                my_agents[agent] = regional_agents[agent]

            num_families = int(num_houses / self.sim.PARAMS['MEMBERS_PER_FAMILY'])
            num_houses = int(num_houses / self.sim.PARAMS['MEMBERS_PER_FAMILY'] * (1 + self.sim.PARAMS['HOUSE_VACANCY']))
            num_firms = int(self.firm_data.num_emp_2000[int(region.id)] * self.sim.PARAMS['PERCENTAGE_ACTUAL_POP'])

            regional_families = self.create_families(num_families)
            regional_houses = self.create_houses(num_houses, region)
            regional_firms = self.create_firms(num_firms, region)

            for family in regional_families.keys():
                my_families[family] = regional_families[family]

            for house in regional_houses.keys():
                my_houses[house] = regional_houses[house]

            for firm in regional_firms.keys():
                my_firms[firm] = regional_firms[firm]

            regional_agents, regional_families = self.allocate_to_family(regional_agents, regional_families)

            # Allocating houses
            regional_families = self.allocate_to_households(regional_families, regional_houses)

            # Set ownership of remaining houses for random families
            self.randomly_assign_houses(regional_houses.values(), regional_families.values())

        return my_agents, my_houses, my_families, my_firms

    def randomly_assign_houses(self, houses, families):
        families = list(families)
        for house in houses:
            if house.owner_id is None:
                family = self.seed.choice(families)
                house.owner_id = family.id
                family.owned_houses.append(house)

    def create_agents(self, region):
        agents = {}
        pops = self.sim.pops
        pop_cols = list(list(pops.values())[0].columns)
        if not self.sim.PARAMS['SIMPLIFY_POP_EVOLUTION']:
            list_of_possible_ages = pop_cols[1:]
        else:
            list_of_possible_ages = [0] + pop_cols[1:]

        loop_age_control = list(list_of_possible_ages)
        loop_age_control.pop(0)

        for age in loop_age_control:
            for gender in ['male', 'female']:
                code = region.id
                pop = pop_age_data(pops[gender], code, age, self.sim.PARAMS['PERCENTAGE_ACTUAL_POP'])
                for individual in range(pop):
                    # Qualification
                    # To see a histogram check test:
                    qualification = self.qual(code)
                    r_age = self.seed.randint(list_of_possible_ages[(list_of_possible_ages.index(age, ) - 1)] + 1,
                                                age)
                    money = self.seed.randrange(50, 100)
                    month = self.seed.randrange(1, 13, 1)
                    agent_id = gen_id()
                    a = Agent(agent_id, gender, r_age, qualification, money, month)
                    agents[agent_id] = a
        return agents

    def create_random_agents(self, n_agents):
        """Create random agents by sampling the existing
        agent population and creating clones of the sampled agents"""
        new_agents = {}
        sample = random.sample(list(self.sim.agents.values()), n_agents)
        for a in sample:
            agent_id = gen_id()
            new_agent = Agent(agent_id, a.gender, a.age, a.qualification, a.money, a.month)
            new_agents[agent_id] = new_agent
        return new_agents

    def create_families(self, num_families):
        community = {}
        for _ in range(num_families):
            family_id = gen_id()
            community[family_id] = Family(family_id)
        return community

    def allocate_to_family(self, agents, families):
        """Allocate agents to families"""
        agents = list(agents.values())
        self.seed.shuffle(agents)
        fams = list(families.values())
        # Separate adults to make sure all families have at least one adult
        adults = [a for a in agents if a.age > 21]
        chd = [a for a in agents if a not in adults]
        # Assume there are more adults than families
        # First, distribute adults as equally as possible
        # Including +1 to avoid division by zero
        for i in range(len(adults)):
            if not adults[i].belongs_to_family:
                fams[i % len(fams)].add_agent(adults[i])

        # Allocate children into random families
        for agent in chd:
            family = self.seed.choice(fams)
            if not agent.belongs_to_family:
                family.add_agent(agent)
        assert len([f for f in fams if len(f.members) == 0]) == 0
        return agents, families

    # Address within the region
    # Additional details so that address fall in urban areas, given percentage
    def get_random_point_in_polygon(self, region, urban=True):
        while True:
            lat = self.seed.uniform(region.address_envelope[0],
                            region.address_envelope[1])
            lng = self.seed.uniform(region.address_envelope[2],
                            region.address_envelope[3])
            address = shapely.geometry.Point(lat,lng)
            if urban:
                mun_code = region.id[:7]
                item = self.urban[mun_code]
                if item.contains(address):
                    return address
            elif region.addresses.contains(address):
                return address

    def create_houses(self, num_houses, region):
        """Create houses for a region"""
        neighborhood = {}

        # only use urban/rural distinction
        # for municipalities with one AP
        mun_code = int(region.id[:7])
        if mun_code in single_ap_muns:
            probability_urban = prop_urban[prop_urban['cod_mun'] == int(mun_code)]['prop_urb'].iloc[0]
        else:
            probability_urban = 0

        for _ in range(num_houses):
            urban = self.seed.random() < probability_urban
            address = self.get_random_point_in_polygon(region, urban=urban)
            size = self.seed.randrange(20, 120)
            # Price is given by 4 quality levels
            quality = self.seed.choice([1, 2, 3, 4])
            price = size * quality * region.index
            house_id = gen_id()
            h = House(house_id, address, size, price, region.id, quality)
            neighborhood[house_id] = h
        return neighborhood

    def allocate_to_households(self, families, households):
        """Allocate houses to families"""
        unclaimed = list(households)
        self.seed.shuffle(unclaimed)
        house_id = None
        for family in families.values():
            if house_id is None:
                house_id = unclaimed.pop(0)
            house = households[house_id]
            if not house.is_occupied:
                family.move_in(house)
                house.owner_id = family.id
                family.owned_houses.append(house)
                house_id = None
        return families

    def create_firms(self, num_firms, region):
        sector = {}
        for _ in range(num_firms):
            address = self.get_random_point_in_polygon(region)
            total_balance = self.seed.betavariate(1.5, 10) * 100000
            firm_id = gen_id()
            f = Firm(firm_id, address, total_balance, region.id)
            sector[f.id] = f
        return sector

    def qual(self, cod):
        sel = quali_sum > self.seed.random()
        idx = sel.idxmax(1)
        loc = idx.loc[int(cod)]
        return int(loc)
