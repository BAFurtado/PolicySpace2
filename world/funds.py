import datetime
from collections import defaultdict

import pandas as pd
import numpy as np

from markets.housing import HousingMarket
from .geography import STATES_CODES, state_string


class Funds:
    def __init__(self, sim):
        self.sim = sim
        self.families_subsided = 0
        self.money_applied_policy = 0
        if sim.PARAMS['FPM_DISTRIBUTION']:
            self.fpm = {
                state: pd.read_csv('input/fpm/%s.csv' % state, sep=',', header=0, decimal='.', encoding='latin1')
                for state in self.sim.geo.states_on_process}
        if sim.PARAMS['POLICY_COEFFICIENT']:
            # Gather the money by municipality. Later gather the families and act upon policy!
            self.policy_money = defaultdict(float)
            self.policy_families = defaultdict(list)
            self.temporary_houses = defaultdict(list)

    def update_policy_families(self):
        # Entering the list this month
        incomes = [f.get_permanent_income() for f in self.sim.families.values()]
        quantile = np.quantile(incomes, self.sim.PARAMS['POLICY_QUANTILE'])
        for region in self.sim.regions.values():
            # Unemployed, Default on rent from the region
            self.sim.regions[region.id].registry[self.sim.clock.days] += [f for f in self.sim.families.values()
                                                                          if f.get_permanent_income() < quantile
                                                                          and f.house.region_id == region.id]
        if self.sim.clock.days < self.sim.PARAMS['STARTING_DAY'] + datetime.timedelta(360):
            return
        # Entering the policy list. Includes families for past months as well
        for region in self.sim.regions.values():
            for keys in region.registry:
                if keys > self.sim.clock.days - datetime.timedelta(self.sim.PARAMS['POLICY_DAYS']):
                    self.policy_families[region.id[:7]] += region.registry[keys]
        for mun in self.policy_families.keys():
            # Make sure families on the list are still valid families, residing at the municipality
            self.policy_families[mun] = [f for f in self.policy_families[mun]
                                         if f.id in self.sim.families.keys() and f.house.region_id[:7] == mun]
            self.policy_families[mun] = list(set(f for f in self.policy_families[mun]))
            self.policy_families[mun] = sorted(self.policy_families[mun], key=lambda f: f.get_permanent_income())

    def apply_policies(self):
        if self.sim.PARAMS['POLICIES'] not in ['buy', 'rent', 'wage']:
            # Baseline scenario. Do nothing!
            return
        # Reset indicator every month to reflect subside in a given month, not cumulatively
        self.families_subsided = 0
        self.update_policy_families()
        # Implement policies only after first year of simulation run
        if self.sim.clock.days < self.sim.PARAMS['STARTING_DAY'] + datetime.timedelta(360):
            return
        if self.sim.PARAMS['POLICIES'] == 'buy':
            self.buy_houses_give_to_families()
        elif self.sim.PARAMS['POLICIES'] == 'rent':
            self.pay_families_rent()
        else:
            self.distribute_funds_to_families()
        # Resetting lists for next month
        self.policy_families = defaultdict(list)
        self.temporary_houses = defaultdict(list)

    def pay_families_rent(self):
        for mun in self.policy_money.keys():
            self.policy_families[mun] = [f for f in self.policy_families[mun] if not f.owned_houses]
            for family in self.policy_families[mun]:
                if family.house.rent_data:
                    if self.policy_money[mun] > 0 and family.house.rent_data[0] * 24 < self.policy_money[mun]:
                        if not family.rent_voucher:
                            # Paying rent for a given number of months, independent of rent value.
                            family.rent_voucher = 24
                            self.policy_money[mun] -= family.house.rent_data[0] * 24
                            self.money_applied_policy += family.house.rent_data[0] * 24
                            self.families_subsided += 1

    def distribute_funds_to_families(self):
        for mun in self.policy_money.keys():
            if self.policy_families[mun] and self.policy_money[mun] > 0:
                # Registering subsidies
                self.money_applied_policy += self.policy_money[mun]
                self.families_subsided += len(self.policy_families[mun])
                # Amount is proportional to available funding and families
                amount = self.policy_money[mun] / len(self.policy_families[mun])
                [f.update_balance(amount) for f in self.policy_families[mun]]
                # Reset fund because it has been totally expended.
                self.policy_money[mun] = 0

    def buy_houses_give_to_families(self):
        # Families are sorted in self.policy_families. Buy and give as much as money allows
        for mun in self.policy_money.keys():
            for firm in self.sim.firms.values():
                if firm.type == 'CONSTRUCTION':
                    # Get the list of the houses for sale within the municipality
                    self.temporary_houses[mun] += [h for h in firm.houses_for_sale if h.region_id[:7] == mun]
            # Sort houses and families by cheapest, poorest.
            # Considering # houses is limited, help as many as possible earlier.
            # Although families in sucession gets better and better houses. Then nothing.
            self.temporary_houses[mun] = sorted(self.temporary_houses[mun], key=lambda h: h.price)
            # Exclude families who own any house. Exclusively for renters
            self.policy_families[mun] = [f for f in self.policy_families[mun] if not f.owned_houses]
            if self.policy_families[mun]:
                for house in self.temporary_houses[mun]:
                    # While money is good.
                    if self.policy_money[mun] > 0 and self.policy_families[mun] \
                            and house.price < self.policy_money[mun]:
                        # Getting poorest family first, given permanent income
                        family = self.policy_families[mun].pop(0)
                        # Transaction taxes help reduce the price of the bulk buying by the municipality
                        taxes = house.price * self.sim.PARAMS['TAX_ESTATE_TRANSACTION']
                        self.sim.regions[house.region_id].collect_taxes(taxes, 'transaction')
                        # Register subsidies
                        self.money_applied_policy += house.price
                        self.families_subsided += 1
                        # Pay construction company
                        self.sim.firms[house.owner_id].update_balance(house.price - taxes,
                                                                      self.sim.PARAMS['CONSTRUCTION_ACC_CASH_FLOW'],
                                                                      self.sim.clock.days)
                        # Deduce from municipality fund
                        self.policy_money[mun] -= house.price
                        # Transfer ownership
                        self.sim.firms[house.owner_id].houses_for_sale.remove(house)
                        # Finish notarial procedures
                        house.owner_id = family.id
                        house.family_owner = True
                        family.owned_houses.append(house)
                        house.on_market = 0
                        # Move out. Move in
                        HousingMarket.make_move(family, house, self.sim)
                    else:
                        break

        # Clean up list for next month
        self.temporary_houses = defaultdict(list)

    def distribute_fpm(self, value, regions, pop_t, pop_mun_t, year):
        """Calculate proportion of FPM per region, in relation to the total of all regions.
        Value is the total value of FPM to distribute"""
        if float(year) > 2016:
            year = str(2016)

        # Dictionary that keeps actual FPM received to be used as a proportion parameter
        # to simulated FPM to be distributed
        fpm_region = {}
        states_numbers = [state_string(state, STATES_CODES) for state in self.sim.geo.states_on_process]
        for i, state in enumerate(self.sim.geo.states_on_process):
            for id, region in regions.items():
                if region.id[:2] == states_numbers[i]:
                    mun_code = region.id[:7]
                    fpm_region[id] = self.fpm[state][(self.fpm[state].ano == float(year)) &
                                                     (self.fpm[state].cod == float(mun_code))].fpm.iloc[0]

        for id, region in regions.items():
            mun_code = region.id[:7]
            regional_fpm = fpm_region[id] / sum(set(fpm_region.values())) * value * pop_t[id] / pop_mun_t[mun_code]

            # Separating money for policy
            if self.sim.PARAMS['POLICY_COEFFICIENT']:
                self.policy_money[mun_code] += regional_fpm * self.sim.PARAMS['POLICY_COEFFICIENT']
                regional_fpm *= 1 - self.sim.PARAMS['POLICY_COEFFICIENT']

            # Actually investing the FPM
            region.update_index(regional_fpm * self.sim.PARAMS['MUNICIPAL_EFFICIENCY_MANAGEMENT'])
            region.update_applied_taxes(regional_fpm, 'fpm')

    def locally(self, value, regions, mun_code, pop_t, pop_mun_t):
        for mun in mun_code.keys():
            for id in mun_code[mun]:
                amount = value[mun] * pop_t[id] / pop_mun_t[mun]

                # Separating money for policy
                if self.sim.PARAMS['POLICY_COEFFICIENT']:
                    self.policy_money[mun] += amount * self.sim.PARAMS['POLICY_COEFFICIENT']
                    amount *= 1 - self.sim.PARAMS['POLICY_COEFFICIENT']

                regions[id].update_index(amount * self.sim.PARAMS['MUNICIPAL_EFFICIENCY_MANAGEMENT'])
                regions[id].update_applied_taxes(amount, 'locally')

    def equally(self, value, regions, pop_t, pop_total):
        for id, region in regions.items():
            amount = value * pop_t[id] / pop_total
            # Separating money for policy
            if self.sim.PARAMS['POLICY_COEFFICIENT']:
                self.policy_money[id[:7]] += amount * self.sim.PARAMS['POLICY_COEFFICIENT']
                amount *= 1 - self.sim.PARAMS['POLICY_COEFFICIENT']
            region.update_index(amount * self.sim.PARAMS['MUNICIPAL_EFFICIENCY_MANAGEMENT'])
            region.update_applied_taxes(amount, 'equally')

    def invest_taxes(self, year, bank_taxes):
        if self.sim.PARAMS['POLICIES'] not in ['buy', 'rent', 'wage']:
            self.sim.PARAMS['POLICY_COEFFICIENT'] = 0
        # Collect and UPDATE pop_t-1 and pop_t
        regions = self.sim.regions
        pop_t_minus_1, pop_t = {}, {}
        pop_mun_minus = defaultdict(int)
        pop_mun_t = defaultdict(int)
        treasure = defaultdict(dict)
        for id, region in regions.items():
            pop_t_minus_1[id] = region.pop
            pop_mun_minus[id[:7]] += region.pop
            # Update
            region.pop = self.sim.reg_pops[id]
            pop_t[id] = region.pop
            pop_mun_t[id[:7]] += region.pop

            # BRING treasure from regions to municipalities
            treasure[id] = region.transfer_treasure()

        # Update proportion of index coming from population variation
        for id, region in regions.items():
            m_id = id[:7]
            region.update_index_pop(pop_mun_minus[m_id]/pop_mun_t[m_id])

        v_local = defaultdict(int)
        v_equal = 0
        if self.sim.PARAMS['ALTERNATIVE0']:
            # Dividing proortion of consumption into equal and local (state, municipality)
            # And adding local part of consumption plus transaction and property to local
            v_equal += sum([treasure[key]['consumption'] for key in treasure.keys()]) * \
                      self.sim.PARAMS['TAXES_STRUCTURE']['consumption_equal']
            mun_code = self.sim.mun_to_regions
            for mun in mun_code.keys():
                v_local[mun] += sum(treasure[r]['consumption'] for r in mun_code[mun]) * \
                                (1 - self.sim.PARAMS['TAXES_STRUCTURE']['consumption_equal'])
                v_local[mun] += sum(treasure[r]['transaction'] for r in mun_code[mun])
                v_local[mun] += sum(treasure[r]['property'] for r in mun_code[mun])
            # The only case in which local funds are distributed
            self.locally(v_local, regions, mun_code, pop_t, pop_mun_t)
        else:
            for each in ['consumption', 'property', 'transaction']:
                v_equal += sum([treasure[key][each] for key in treasure.keys()])

        if self.sim.PARAMS['FPM_DISTRIBUTION']:
            v_fpm = (sum([treasure[key]['labor'] for key in treasure.keys()]) +
                     sum([treasure[key]['firm'] for key in treasure.keys()]))
            self.distribute_fpm(v_fpm * self.sim.PARAMS['TAXES_STRUCTURE']['fpm'], regions, pop_t, pop_mun_t, year)
            v_equal += v_fpm * (1 - self.sim.PARAMS['TAXES_STRUCTURE']['fpm'])
        else:
            v_equal += (sum([treasure[key]['labor'] for key in treasure.keys()]) +
                        sum([treasure[key]['firm'] for key in treasure.keys()]))
        # Taxes charged from interests paid by the bank are equally distributed
        v_equal += bank_taxes
        self.equally(v_equal, regions, pop_t, sum(pop_mun_t.values()))
