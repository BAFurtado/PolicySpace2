import math

import numpy as np
import pandas as pd
import statsmodels.api as sm


def simplify_pops(pops, params):
    """Simplify population"""
    # Inserting the 0 on the new list of ages
    list_new_age_groups = [0] + params['LIST_NEW_AGE_GROUPS']

    pops_ = {}
    for gender, pop in pops.items():
        # excluding the first column (region ID)
        pop_edit = pop.iloc[:, pop.columns != 'code']

        # Transform the columns ID in integer values (to make easy to select the intervals and sum the pop. by region)
        list_of_ages = [int(x) for x in [int(t) for t in list(pop_edit.columns)]]
        # create the first aggregated age class
        temp = pop_edit.iloc[:, [int(t) <= list_new_age_groups[1] for t in list_of_ages]].sum(axis=1)
        # add the first column with the region ID
        pop_fmt = pd.concat([pop.iloc[:, pop.columns == 'code'], temp], axis=1)
        # excluding the processed columns in the previous age aggregation
        pop_edit = pop_edit.iloc[:, [int(i) > list_new_age_groups[1] for i in list_of_ages]]
        for i in range(1, len(list_new_age_groups) - 1):
            # creating the full new renaming ages list
            list_of_ages = [int(x) for x in [int(t) for t in list(pop_edit.columns)]]
            # selecting the new aggregated age class based on superior limit from list_new_age_groups, SUM by ROW
            temp = pop_edit.iloc[:, [int(t) <= list_new_age_groups[i + 1] for t in list_of_ages]].sum(axis=1)
            # joining to the previous processed age class
            pop_fmt = pd.concat([pop_fmt, temp], axis=1)
            # excluding the processed columns in the previous age aggregation
            pop_edit = pop_edit.iloc[:, [int(age) > list_new_age_groups[i + 1] for age in list_of_ages]]
        # changing the columns names
        pop_fmt.columns = ['code'] + list_new_age_groups[1:len(list_new_age_groups)]
        pops_[gender] = pop_fmt

    return pops_


def format_pops(pops):
    """Rename the columns names to be compatible as the pop simplification modification"""
    list_of_columns = ['code']+[int(x) for x in list(pops[0].columns)[1:len(list(pops[0].columns))]]
    for pop in pops.values():
        pop.columns = list_of_columns
    return pops


def pop_age_data(pop, code, age, percent_pop):
    """Select and return the proportion value of population
    for a given municipality, gender and age"""
    n_pop = pop[pop['code'] == str(code)][age].iloc[0] * percent_pop
    rounded = int(round(n_pop))

    # for small `percent_pop`, sometimes we get 0
    # when it's better to have at least 1 agent
    if rounded == 0 and math.ceil(n_pop) == 1:
        return 1

    return rounded


def load_pops(mun_codes, params):
    """Load populations for specified municipal codes."""
    pops = {}
    for name, gender in [('men', 'male'), ('women', 'female')]:
        pop = pd.read_csv('input/pop_{}.csv'.format(name), sep=';', header=0, decimal=',')
        pop = pop[pop['cod_mun'].isin(mun_codes)]

        # rename from cod_mun b/c we may also have
        # AP codes, not just municipal codes
        pop.rename(columns={'cod_mun': 'code'}, inplace=True)
        pops[gender] = pop

    ap_pops = pd.read_csv('input/num_people_age_gender_AP.csv', sep=';', header=0)
    for code, group in ap_pops.groupby('AREAP'):
        if not int(str(code)[:7]) in mun_codes:
            continue
        for gender, gender_code in [('male', 1), ('female', 2)]:
            df = pops[gender]
            sub_group = group[group.gender == gender_code][['age', 'num_people']].to_records()
            row = [0 for _ in range(101)]
            for idx, age, count in sub_group:
                row[age] = count
            row = [code] + row
            df.loc[df.shape[0]] = row

    for pop in pops.values():
        pop['code'] = pop['code'].astype(np.int64).astype(str)

    total_pop = sum(round(pop.iloc[:, pop.columns != 'code'].sum(axis=1).sum(0) * params['PERCENTAGE_ACTUAL_POP']) for pop in pops.values())
    if params['SIMPLIFY_POP_EVOLUTION']:
        pops = simplify_pops(pops, params)
    else:
        pops = format_pops(pops)

    return pops, total_pop


class PopulationEstimates:
    def __init__(self, fname):
        df = pd.read_csv(fname).set_index('mun_code')

        # Compute linear models to impute
        # missing data. Not always accurate unfortunately,
        # because not all population trends are linear
        self.linear_models = {}
        for mun_code, pops in df.iterrows():
            x = pops.index.values.astype('int')
            y = pops.values
            self.linear_models[mun_code] = sm.OLS(y, x).fit()

        self.data = df.to_dict()

    def estimate_for_year(self, mun_code, year):
        mun_code = int(mun_code)
        estimate = self.data.get(str(year))
        if estimate is None:
            return round(self.linear_models[mun_code].predict([int(year)])[0])
        return estimate[mun_code]


class MarriageData:
    def __init__(self):
        self.data = {'male': {}, 'female': {}}

        for gender, key in [('male', 'men'), ('female', 'women')]:
            for row in pd.read_csv('input/marriage_age_{}.csv'.format(key)).itertuples():
                for age in range(row.low, row.high+1):
                    self.data[gender][age] = row.percentage

    def p_marriage(self, agent):
        return self.data[agent.gender.lower()].get(agent.age, 0)


pop_estimates = PopulationEstimates('input/estimativas_pop.csv')
marriage_data = MarriageData()


def immigration(sim):
    """Adjust population for immigration"""
    year = sim.clock.year

    # Create new agents for immigration
    for mun_code, pop in sim.mun_pops.items():
        estimated_pop = pop_estimates.estimate_for_year(mun_code, year)
        estimated_pop *= sim.PARAMS['PERCENTAGE_ACTUAL_POP']
        immigration = max(estimated_pop - pop, 0)
        immigration *= 1/12
        n_migrants = math.ceil(immigration)
        if not n_migrants:
            continue

        # Create new agents
        new_agents = sim.generator.create_random_agents(n_migrants)

        # Create new families
        n_families = math.ceil(len(new_agents)/sim.PARAMS['MEMBERS_PER_FAMILY'])
        new_families = sim.generator.create_families(n_families)

        # Assign agents to families
        sim.generator.allocate_to_family(new_agents, new_families)

        # Keep track of new agents & families
        for f in new_families.values():
            sim.families[f.id] = f

            # Create and assign homes
            # Choose random region in this municipality
            region_id = sim.seed.choice(sim.mun_to_regions[mun_code])
            region = sim.regions[region_id]
            new_houses = sim.generator.create_houses(1, region)
            sim.generator.allocate_to_households({f.id: f}, new_houses)

        # Has to come after we allocate households
        # so we know where the agents live
        for a in new_agents.values():
            sim.agents[a.id] = a
            sim.update_pop(None, a.region_id)


def marriage(sim):
    """Adjust families for marriages"""
    to_marry = []
    for agent in sim.agents.values():
        # Compute probability that this agent will marry
        # NOTE we don't consider whether or not they are already married
        if sim.seed.random() < agent.p_marriage:
            to_marry.append(agent)

    # Marry individuals
    # NOTE individuals are paired randomly
    sim.seed.shuffle(to_marry)
    to_marry = iter(to_marry)
    for a, b in zip(to_marry, to_marry):
        a_is_alone = a.family.num_members == 1
        b_is_alone = b.family.num_members == 1
        if a_is_alone:
            # If both a and b are alone,
            # one moves in with the other
            # the other family is deleted
            # and the house ownership transfers
            # to a's family.
            if b_is_alone:
                moving_process(a, b, sim)

            # If a is alone and b is not,
            else:
                # Check there is no children left behind
                check_children(a, b, sim)

        # # If b is alone and a is not,
        # # a moves in with b.
        elif b_is_alone:
            if not a_is_alone:
                check_children(b, a, sim)

        # # If neither a and b are alone,
        # # they form a new family
        # # and get a new house.
        else:
            new_family = list(sim.generator.create_families(1).values())[0]
            a.family.remove_agent(a)
            b.family.remove_agent(b)
            new_family.add_agent(a)
            new_family.add_agent(b)
            sim.families[new_family.id] = new_family
            sim.housing.rental.rental_market([new_family], sim)
            a_region_id = a.family.region_id
            b_region_id = b.family.region_id
            sim.update_pop(a_region_id, a.region_id)
            sim.update_pop(b_region_id, b.region_id)


def moving_process(a, b, sim):
    # b moves into a
    houses = b.family.owned_houses
    # Transfer ownership, if any
    for house in houses:
        sim.families[b.family.id].owned_houses.remove(house)
        house.owner_id = a.family.id
        sim.families[a.family.id].owned_houses.append(house)
    old_r_id = b.region_id
    b.family.move_out()
    id = b.family.id
    sim.update_pop(old_r_id, b.region_id)
    members = list(b.family.members.values()).copy()
    for m in members:
        b.family.remove_agent(m)
        a.family.add_agent(m)
    del sim.families[id]


def check_children(a, b, sim):
    # Checking family b
    adults = [m for m in b.family.members.values() if m.age > 21]
    if len(adults) >= 2:
        # b moves in with a
        old_r_id = b.region_id
        b.family.remove_agent(b)
        a.family.add_agent(b)
        sim.update_pop(old_r_id, b.region_id)
    else:
        # a moves in with b
        moving_process(b, a, sim)
