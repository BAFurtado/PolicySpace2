import pandas as pd
from .geography import STATES_CODES, state_string
from collections import defaultdict


class Funds:
    def __init__(self, sim):
        self.sim = sim
        if sim.PARAMS['FPM_DISTRIBUTION']:
            self.fpm = {
                state: pd.read_csv('input/fpm/%s.csv' % state, sep=',', header=0, decimal='.', encoding='latin1')
                for state in self.sim.geo.states_on_process}
        if sim.PARAMS['POLICY_COEFFICIENT']:
            # Gather the money by municipality. Later gather the families and act upon policy!
            self.policy_money = defaultdict(float)

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
            # POLICY: GET MONEY OUT OF VALUE
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
            # POLICY: GET MONEY OUT OF AMOUNT
            amount = value * pop_t[id] / pop_total
            # Separating money for policy
            if self.sim.PARAMS['POLICY_COEFFICIENT']:
                self.policy_money[id[:7]] += amount * self.sim.PARAMS['POLICY_COEFFICIENT']
                amount *= 1 - self.sim.PARAMS['POLICY_COEFFICIENT']
            region.update_index(amount * self.sim.PARAMS['MUNICIPAL_EFFICIENCY_MANAGEMENT'])
            region.update_applied_taxes(amount, 'equally')

    def invest_taxes(self, year, bank_taxes):
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
        if self.sim.PARAMS['ALTERNATIVE0']:
            v_equal = sum([treasure[key]['consumption'] for key in treasure.keys()]) * \
                      self.sim.PARAMS['TAXES_STRUCTURE']['consumption_equal']
            mun_code = self.sim.mun_to_regions
            for mun in mun_code.keys():
                v_local[mun] += sum(treasure[r]['consumption'] for r in mun_code[mun]) * \
                                (1 - self.sim.PARAMS['TAXES_STRUCTURE']['consumption_equal'])
                v_local[mun] += sum(treasure[r]['transaction'] for r in mun_code[mun])
                v_local[mun] += sum(treasure[r]['property'] for r in mun_code[mun])
            self.locally(v_local, regions, mun_code, pop_t, pop_mun_t)
        else:
            v_equal = 0
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
