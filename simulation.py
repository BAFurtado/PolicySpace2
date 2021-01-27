import datetime
import json
import math
import os
import pickle
import random
import sys
from collections import defaultdict

import numpy as np
import pandas as pd

import analysis
import conf
import markets
from world import Generator, demographics, clock, population
from world.firms import firm_growth
from world.funds import Funds
from world.geography import Geography, STATES_CODES, state_string


class Simulation:
    def __init__(self, params, output_path):
        self.PARAMS = params
        self.geo = Geography(params, self.PARAMS['STARTING_DAY'].year)
        self.funds = Funds(self)
        self.clock = clock.Clock(self.PARAMS['STARTING_DAY'])
        self.output = analysis.Output(self, output_path)
        self.stats = analysis.Statistics()
        self.logger = analysis.Logger(hex(id(self))[-5:])
        self._seed = random.randrange(sys.maxsize) if conf.RUN['KEEP_RANDOM_SEED'] else conf.RUN.get('SEED', 0)
        self.seed = random.Random(self._seed)
        self.generator = Generator(self)

        # Read necessary files
        self.m_men, self.m_women, self.f = {}, {}, {}
        for state in self.geo.states_on_process:
            self.m_men[state] = pd.read_csv('input/mortality/mortality_men_%s.csv' % state,
                                            sep=';', header=0, decimal='.').groupby('age')
            self.m_women[state] = pd.read_csv('input/mortality/mortality_women_%s.csv' % state,
                                              sep=';', header=0, decimal='.').groupby('age')
            self.f[state] = pd.read_csv('input/fertility/fertility_%s.csv' % state,
                                        sep=';', header=0, decimal='.').groupby('age')

        # Interest
        # Average interest rate - Earmarked new operations - Households - Real estate financing - Market rates
        # PORT. Taxa média de juros das operações de crédito com recursos direcionados - Pessoas físicas -
        # Financiamento imobiliário com taxas de mercado. BC series 433. 25497. 4390.
        # Values before 2011-03-01 when the series began are set at the value of 2011-03-01. After, mean.
        interest = pd.read_csv(f"input/interest_{self.PARAMS['INTEREST']}.csv", sep=';')
        interest.date = pd.to_datetime(interest.date)
        self.interest = interest.set_index('date')

    def update_pop(self, old_region_id, new_region_id):
        if old_region_id is not None:
            self.mun_pops[old_region_id[:7]] += 1
            self.reg_pops[old_region_id] += 1
        if new_region_id is not None:
            self.mun_pops[new_region_id[:7]] += 1
            self.reg_pops[new_region_id] += 1

    def generate(self):
        """Spawn or load regions, agents, houses, families, and firms"""
        save_file = '{}.agents'.format(self.output.save_name)
        if not os.path.isfile(save_file) or conf.RUN['FORCE_NEW_POPULATION']:
            self.logger.logger.info('Creating new agents')
            regions = self.generator.create_regions()
            agents, houses, families, firms = self.generator.create_all(regions)
            agents = {a: agents[a] for a in agents.keys() if agents[a].address is not None}
            with open(save_file, 'wb') as f:
                pickle.dump([agents, houses, families, firms, regions], f)
        else:
            self.logger.logger.info('Loading existing agents')
            with open(save_file, 'rb') as f:
                 agents, houses, families, firms, regions = pickle.load(f)

        # Count populations for each municipality and region
        self.mun_pops = {}
        self.reg_pops = {}
        for agent in agents.values():
            r_id = agent.region_id
            mun_code = r_id[:7]
            if r_id not in self.reg_pops:
                self.reg_pops[r_id] = 0
            if mun_code not in self.mun_pops:
                self.mun_pops[mun_code] = 0
            self.mun_pops[mun_code] += 1
            self.reg_pops[r_id] += 1

        return regions, agents, houses, families, firms, self.generator.central

    def run(self):
        """Runs the simulation"""
        self.logger.logger.info('Starting run.')
        self.logger.logger.info('Output: {}'.format(self.output.path))
        self.logger.logger.info('Params: {}'.format(json.dumps(self.PARAMS, default=str)))
        self.logger.logger.info('Seed: {}'.format(self._seed))

        self.logger.logger.info('Running...')
        while self.clock.days < self.PARAMS['STARTING_DAY'] + datetime.timedelta(days=self.PARAMS['TOTAL_DAYS']):
            self.daily()
            if self.clock.months == 1 and conf.RUN['SAVE_TRANSIT_DATA']:
                self.output.save_transit_data(self, 'start')
            if self.clock.new_month:
                self.monthly()
            if self.clock.new_quarter:
                self.quarterly()
            if self.clock.new_year:
                self.yearly()
            self.clock.days += datetime.timedelta(days=1)

        if conf.RUN['PRINT_FINAL_STATISTICS_ABOUT_AGENTS']:
            self.logger.log_outcomes(self)

        if conf.RUN['SAVE_TRANSIT_DATA']:
            self.output.save_transit_data(self, 'end')
        self.logger.logger.info('Simulation completed.')

    def initialize(self):
        """Initiating simulation"""
        self.logger.logger.info('Initializing...')
        self.grave = []

        self.labor_market = markets.LaborMarket(self.seed)
        self.housing = markets.HousingMarket()
        self.pops, self.total_pop = population.load_pops(self.geo.mun_codes, self.PARAMS, self.geo.year)
        self.regions, self.agents, self.houses, self.families, self.firms, self.central = self.generate()
        self.construction_firms = {f.id: f for f in self.firms.values() if f.type == 'CONSTRUCTION'}
        self.consumer_firms = {f.id: f for f in self.firms.values() if f.type == 'CONSUMER'}

        # Group regions into their municipalities
        self.mun_to_regions = defaultdict(set)
        for region_id in self.regions.keys():
            mun_code = region_id[:7]
            self.mun_to_regions[mun_code].add(region_id)
        for mun_code, regions in self.mun_to_regions.items():
            self.mun_to_regions[mun_code] = list(regions)

        # Beginning of simulation, generate a product
        for firm in self.firms.values():
            firm.create_product()

        # First jobs allocated
        # Create an existing job market
        # Leave only 5% residual unemployment as of simulation starts
        self.labor_market.look_for_jobs(self.agents)
        total = actual = self.labor_market.num_candidates
        actual_unemployment = self.stats.global_unemployment_rate / 100
        # Simple average of 6 Metropolitan regions Brazil January 2000
        while actual / total > .086:
            self.labor_market.hire_fire(self.firms, self.PARAMS['LABOR_MARKET'])
            self.labor_market.assign_post(actual_unemployment, None, self.PARAMS)
            self.labor_market.look_for_jobs(self.agents)
            actual = self.labor_market.num_candidates
        self.labor_market.reset()

        # Update initial pop
        for region in self.regions.values():
            region.pop = self.reg_pops[region.id]

    def daily(self):
        pass

    def monthly(self):
        # Set interest rates
        i = self.interest[self.interest.index.date == self.clock.days]['interest'].iloc[0]
        m = self.interest[self.interest.index.date == self.clock.days]['mortgage'].iloc[0]
        self.central.set_interest(i, m)

        current_unemployment = self.stats.global_unemployment_rate / 100

        # Create new land licenses
        for region in self.regions.values():
            if self.PARAMS['T_LICENSES_PER_REGION'] == 'random':
                region.licenses += self.seed.choice([True, False])
            else:
                region.licenses += self.PARAMS['T_LICENSES_PER_REGION']

        # Create new firms according to average historical growth
        firm_growth(self)

        # Update firm products
        for firm in self.firms.values():
            firm.update_product_quantity(self.PARAMS['PRODUCTIVITY_EXPONENT'],
                                         self.PARAMS['PRODUCTIVITY_MAGNITUDE_DIVISOR'])

        # Call demographics
        # Update agent life cycles
        for state in self.geo.states_on_process:
            mortality_men = self.m_men[state]
            mortality_women = self.m_women[state]
            fertility = self.f[state]

            state_str = state_string(state, STATES_CODES)

            birthdays = defaultdict(list)
            for agent in self.agents.values():
                if self.clock.months == agent.month and agent.region_id[:2] == state_str:
                    birthdays[agent.age].append(agent)

            demographics.check_demographics(self, birthdays, self.clock.year,
                                            mortality_men, mortality_women, fertility)

        # Adjust population for immigration
        population.immigration(self)

        # Adjust families for marriages
        population.marriage(self)

        # Firms initialization
        for firm in self.firms.values():
            firm.present = self.clock
            firm.amount_sold = 0
            if firm.type is not 'CONSTRUCTION':
                firm.revenue = 0

        # FAMILIES CONSUMPTION -- using payment received from previous month
        # Equalize money within family members
        # Tax consumption when doing sales are realized
        markets.goods.consume(self)

        # Collect loan repayments
        self.central.collect_loan_payments(self)

        # FIRMS
        for firm in self.firms.values():
            # Tax workers when paying salaries
            firm.make_payment(self.regions, current_unemployment,
                              self.PARAMS['PRODUCTIVITY_EXPONENT'],
                              self.PARAMS['TAX_LABOR'],
                              self.PARAMS['WAGE_IGNORE_UNEMPLOYMENT'])
            # Tax firms before profits: (revenue - salaries paid)
            firm.pay_taxes(self.regions, self.PARAMS['TAX_FIRM'])
            # Profits are after taxes
            firm.calculate_profit()
            # Check whether it is necessary to update prices
            firm.update_prices(self.PARAMS['STICKY_PRICES'], self.PARAMS['MARKUP'], self.seed)

        # Construction firms
        vacancy = self.stats.calculate_house_vacancy(self.houses, False)
        vacancy_value = None
        # Probability depends on size of market
        if self.PARAMS['OFFER_SIZE_ON_PRICE']:
            vacancy_value = 1 - (vacancy * self.PARAMS['OFFER_SIZE_ON_PRICE'])
            if vacancy_value < self.PARAMS['MAX_OFFER_DISCOUNT']:
                vacancy_value = self.PARAMS['MAX_OFFER_DISCOUNT']
        for firm in self.construction_firms.values():
            # See if firm can build a house
            firm.plan_house(self.regions.values(), self.houses.values(), self.PARAMS, self.seed, vacancy_value)
            # See whether a house has been completed. If so, register. Else, continue
            house = firm.build_house(self.regions, self.generator)
            if house is not None:
                self.houses[house.id] = house

        # Initiating Labor Market
        # AGENTS
        self.labor_market.look_for_jobs(self.agents)

        # FIRMS
        # Check if new employee needed (functions below)
        # Check if firing is necessary
        self.labor_market.hire_fire(self.firms, self.PARAMS['LABOR_MARKET'])

        # Job Matching
        # Sample used only to calculate wage deciles
        sample_size = math.floor(len(self.agents) * 0.5)
        last_wages = [self.agents[a].last_wage
                      for a in self.seed.sample(self.agents.keys(), sample_size)
                      if self.agents[a].last_wage is not None]
        wage_deciles = np.percentile(last_wages, np.arange(0, 100, 10))
        self.labor_market.assign_post(current_unemployment, wage_deciles, self.PARAMS)

        # Initiating Real Estate Market
        self.logger.logger.info(f'Available licenses: {sum([r.licenses for r in self.regions.values()]):,.0f}')
        # Tax transaction taxes (ITBI) when selling house
        # Property tax (IPTU) collected. One twelfth per month
        # self.central.calculate_monthly_mortgage_rate()
        self.housing.housing_market(self)
        self.housing.process_monthly_rent(self)
        for house in self.houses.values():
            house.pay_property_tax(self)

        # Family investments
        for fam in self.families.values():
            fam.invest(self.central.interest, self.central, self.clock.year, self.clock.months)

        # Using all collected taxes to improve public services
        bank_taxes = self.central.collect_taxes()

        # Separate funds for region index update and separate for the policy case
        self.funds.invest_taxes(self.clock.year, bank_taxes)

        # Apply policies if percentage is different than 0
        if self.PARAMS['POLICY_COEFFICIENT']:
            self.funds.apply_policies()

        # Pass monthly information to be stored in Statistics
        self.output.save_stats_report(self, bank_taxes)

        # Getting regional GDP
        self.output.save_regional_report(self)

        if conf.RUN['SAVE_AGENTS_DATA'] == 'MONTHLY':
            self.output.save_data(self)

        if conf.RUN['PRINT_STATISTICS_AND_RESULTS_DURING_PROCESS']:
            self.logger.info(self.clock.days)

    def quarterly(self):
        if conf.RUN['SAVE_AGENTS_DATA'] == 'QUARTERLY':
            self.output.save_data(self)

    def yearly(self):
        if conf.RUN['SAVE_AGENTS_DATA'] == 'ANNUALLY':
            self.output.save_data(self)
