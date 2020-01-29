import json
import os
from collections import defaultdict

import conf

AGENTS_PATH = 'StoragedAgents'
if not os.path.exists(AGENTS_PATH):
    os.mkdir(AGENTS_PATH)

# These are the params which specifically
# affect agent generation.
# We check when these change so
# we know to re-generate the agent population.
GENERATOR_PARAMS = [
    'MEMBERS_PER_FAMILY',
    'HOUSE_VACANCY',
    'SIMPLIFY_POP_EVOLUTION',
    'PERCENTAGE_ACTUAL_POP'
]


class Output:
    """Manages simulation outputs"""

    def __init__(self, sim, output_path):
        files = ['stats', 'regional', 'time', 'firms', 'banks',
                 'houses', 'agents', 'families', 'grave']

        self.sim = sim
        self.times = []
        self.path = output_path
        self.transit_path = os.path.join(self.path, 'transit')
        if not os.path.exists(self.path):
            os.makedirs(self.path)
            os.makedirs(self.transit_path)

        for p in files:
            path = os.path.join(self.path, 'temp_{}.csv'.format(p))
            setattr(self, '{}_path'.format(p), path)

            # reset files for each run
            if os.path.exists(path):
                os.remove(path)

        self.save_name = '{}/{}_states_{}_acps_{}'.format(
            AGENTS_PATH,
            '_'.join([str(self.sim.PARAMS[name]) for name in GENERATOR_PARAMS]),
            '_'.join(sim.geo.states_on_process),
            '_'.join(sim.geo.processing_acps_codes)
        )

    def save_stats_report(self, sim):
        price_index, inflation = sim.stats.update_price(sim.firms)
        gdp_index, gdp_growth = sim.stats.sum_region_gdp(sim.firms, sim.regions)
        unemployment = sim.stats.update_unemployment(sim.agents.values(), True)
        average_workers = sim.stats.calculate_average_workers(sim.firms)
        families_wealth, families_savings = sim.stats.calculate_families_wealth(sim.families)
        firms_wealth = sim.stats.calculate_firms_wealth(sim.firms)
        firms_profit = sim.stats.calculate_firms_profit(sim.firms)
        gini_index = sim.stats.calculate_GINI(sim.families)
        average_utility = sim.stats.calculate_utility(sim.families)
        average_qli = sim.stats.average_qli(sim.regions)

        mun_applied_treasure = defaultdict(int)
        for k in ['equally', 'locally', 'fpm']:
            mun_applied_treasure[k] = sum(r.applied_treasure[k] for r in sim.regions.values())

        report = '{};{:.3f};{:.3f};{:.3f};{:.3f};{:.3f};{:.3f};{:.3f};{:.3f};{:.3f};{:.3f};{:.3f};{:.4f};{:.4f};' \
                 '{:.4f};{:.4f};{:.4f}\n'.format(
                    sim.clock.days, price_index, gdp_index,
                    gdp_growth, unemployment, average_workers,
                    families_wealth, families_savings,
                    firms_wealth, firms_profit, gini_index,
                    average_utility, inflation, average_qli,
            mun_applied_treasure['equally'],
            mun_applied_treasure['locally'],
            mun_applied_treasure['fpm']
        )

        with open(self.stats_path, 'a') as f:
            f.write(report)

    def save_regional_report(self, sim):
        reports = []
        municipalities = defaultdict(list)
        agents_by_mun = defaultdict(list)
        families_by_mun = defaultdict(list)
        for agent in sim.agents.values():
            mun_id = agent.region_id[:7]
            agents_by_mun[mun_id].append(agent)

        for family in sim.families.values():
            # sometimes family.region_id is None?
            if family.region_id:
                mun_id = family.region_id[:7]
                families_by_mun[mun_id].append(family)
            else:
                families_by_mun[family.region_id].append(family)

        # aggregate regions into municipalities,
        # in case they are APs
        for region in sim.regions.values():
            mun_id = region.id[:7]
            municipalities[mun_id].append(region)

        for mun_id, regions in municipalities.items():
            mun_pop = sum(r.pop for r in regions)
            mun_gdp = sum(r.gdp for r in regions)
            mun_agents = agents_by_mun[mun_id]
            mun_families = families_by_mun[mun_id]
            GDP_mun_capita = sim.stats.update_GDP_capita(sim.firms, mun_id, mun_pop)
            commuting = sim.stats.update_commuting(mun_families)
            mun_gini = sim.stats.calculate_regional_GINI(mun_families)
            mun_house_values = sim.stats.calculate_avg_regional_house_price(mun_families)
            mun_unemployment = sim.stats.update_unemployment(mun_agents)
            # region.total_commute = commuting

            mun_cumulative_treasure = 0
            for r in regions:
                mun_cumulative_treasure += sum(r.cumulative_treasure.values())

            mun_applied_treasure = defaultdict(int)
            for k in ['equally', 'locally', 'fpm']:
                mun_applied_treasure[k] = sum(r.applied_treasure[k] for r in regions)

            # average QLI of regions
            mun_qli = sum(r.index for r in regions)/len(regions)

            reports.append('%s;%s;%.3f;%d;%.3f;%.4f;%.3f;%.4f;%.5f;%.3f;%.6f;%.6f;%.6f;%.6f'
                                % (sim.clock.days, mun_id, commuting, mun_pop, mun_gdp, mun_gini, mun_house_values,
                                   mun_unemployment, mun_qli, GDP_mun_capita, mun_cumulative_treasure,
                                   mun_applied_treasure['equally'],
                                   mun_applied_treasure['locally'],
                                   mun_applied_treasure['fpm']))

        with open(self.regional_path, 'a') as f:
            f.write('\n'+'\n'.join(reports))

    def save_data(self, sim):
        # firms data is necessary for plots,
        # so always save
        self.save_firms_data(sim)
        self.save_banks_data(sim)

        for type in conf.RUN['SAVE_DATA']:
            save_fn = getattr(self, 'save_{}_data'.format(type))
            save_fn(sim)

    def save_firms_data(self, sim):
        with open(self.firms_path, 'a') as f:
            [f.write('%s; %s; %s; %.3f; %.3f; %.3f; %s; %.3f; %.3f; %.3f ; %.3f; %.3f; %.3f; %.3f \n' %
                            (sim.clock.days, firm.id, firm.region_id, firm.address.x,
                            firm.address.y, firm.total_balance, firm.num_employees,
                            firm.total_quantity, firm.amount_produced, firm.inventory[0].price,
                            firm.amount_sold, firm.revenue, firm.profit,
                            firm.wages_paid))
            for firm in sim.firms.values()]

    def save_agents_data(self, sim):
        with open(self.agents_path, 'a') as f:
            [f.write('%s;%s;%s;%.3f;%.3f;%d;%d;%d;%s;%s;%.3f;%.3f;%s\n' % (sim.clock.days, agent.region_id,
                                                                           agent.gender, agent.address.x,
                                                                           agent.address.y, agent.id, agent.age,
                                                                           agent.qualification, agent.firm_id,
                                                                           agent.family.id, agent.money, agent.utility,
                                                                           agent.distance))
            for agent in sim.agents.values()]

    def save_grave_data(self, sim):
        with open(self.grave_path, 'a') as f:
            [f.write('%s;%s;%s;%s;%s;%d;%d;%d;%s;%s;%.3f;%.3f;%s\n' % (sim.clock.days, agent.region_id,
                                                                           agent.gender,
                                                                           agent.address.x if agent.address else None,
                                                                           agent.address.y if agent.address else None,
                                                                           agent.id, agent.age,
                                                                           agent.qualification, agent.firm_id,
                                                                           agent.family.id if agent.family else None,
                                                                           agent.money, agent.utility,
                                                                           agent.distance))
            for agent in sim.grave]

    def save_house_data(self, sim):
        with open(self.houses_path, 'a') as f:
            [f.write('%s;%s;%f;%f;%.2f;%.2f;%f;%s;%s\n' % (sim.clock.days,
                                                                house.id,
                                                                house.address.x,
                                                                house.address.y,
                                                                house.size,
                                                                house.price,
                                                                house.on_market,
                                                                house.family_id,
                                                                house.region_id[:7]))
            for house in sim.houses.values()]

    def save_family_data(self, sim):
        with open(self.families_path, 'a') as f:
            [f.write('%s;%s;%s;%s;%s;%s;%s;%s;%.2f;%.2f;%.2f\n' % (sim.clock.days,
                                                            family.id,
                                                            family.house.price if family.house else '',
                                                            family.house.rent_data[0] if family.house.rent_data else '',
                                                            family.house.id if family.house else '',
                                                            family.house.owner_id if family.house else '',
                                                            family.house.family_id if family.house else '',
                                                            family.region_id[:7],
                                                            family.total_wage(),
                                                            family.savings,
                                                            family.num_members))
            for family in sim.families.values()]

    def save_banks_data(self, sim):
        bank = sim.central
        with open(self.banks_path, 'a') as f:
            active = bank.active_loans()
            n_active = len(active)
            mean_age = sum(l.age for l in active)/n_active if n_active else 0
            p_delinquent = len(bank.delinquent_loans())/n_active if n_active else 0
            mn, mx, avg = bank.loan_stats()
            f.write('%s; %.3f; %.3f; %.3f; %.3f; %.3f; %.3f; %.3f; %.3f; %.3f \n' %
                            (sim.clock.days, bank.taxes, bank.balance, bank.total_deposits(),
                             n_active, p_delinquent, mean_age, mn, mx, avg))

    def save_transit_data(self, sim, fname):
        region_ids = conf.RUN['LIMIT_SAVED_TRANSIT_REGIONS']
        firms = {}
        for firm in sim.firms.values():
            if region_ids is None or any(firm.region_id.startswith(r_id) for r_id in region_ids):
                firms[firm.id] = (firm.address.x, firm.address.y)

        houses = {}
        for house in sim.houses.values():
            if region_ids is None or any(house.region_id.startswith(r_id) for r_id in region_ids):
                houses[house.id] = (house.address.x, house.address.y)

        agents = {}
        for agent in sim.agents.values():
            if region_ids is None or any(agent.region_id.startswith(r_id) for r_id in region_ids):
                agents[agent.id] = (agent.address.x, agent.address.y, agent.family.house.id, agent.firm_id,
                                    agent.last_wage)

        path = os.path.join(self.transit_path, '{}.json'.format(fname))
        with open(path, 'w') as f:
            json.dump({
                'firms': firms,
                'houses': houses,
                'agents': agents
            }, f)
