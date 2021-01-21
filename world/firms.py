from collections import defaultdict

import numpy as np
import pandas as pd


class FirmData:
    """ Firm growth is estimated from a monthly value of growth observed between the years of 2000 and 2012 """
    def __init__(self, year):
        # Using APs code of year 2000 (they are not compatible with year 2010 APs)
        # If year == 2000, data refers to years 2002 and 2012
        # If year == 2010, data refers to years 2010 and 2017
        self.num_emp_t0 = self._load(f'input/firms_by_APs{year}_t0_full.csv')
        self.num_emp_t1 = self._load(f'input/firms_by_APs{year}_t1_full.csv')

        self.deltas = {}
        self.avg_monthly_deltas = {}
        for mun_code, num_emp_t0 in self.num_emp_t0.items():
            num_emp_t1 = self.num_emp_t1[mun_code]
            delta = num_emp_t1 - num_emp_t0
            self.deltas[mun_code] = delta
            if year == 2000:
                num_months = 12 * 10
            else:
                num_months = 12 * 7
            self.avg_monthly_deltas[mun_code] = delta/num_months

    def _load(self, fname):
        """ Returns the sum of firms of each AP by municipality (all APs summed) """
        num_emp_aps = pd.read_csv(fname, sep=';')
        num_emp = defaultdict(int)
        for idx, row in num_emp_aps.iterrows():
            mun_code = int(str(row['AP'])[:7])
            num_emp[mun_code] += row['num_firms']
            num_emp[int(row['AP'])] = row['num_firms']
        return num_emp


def firm_growth(sim):
    """ Create new firms according to average historical growth
        Location within the municipality is more likely on regions with growth of profit and employees
        """

    # Group firms by region
    firms_by_region = defaultdict(list)
    for firm in sim.firms.values():
        firms_by_region[firm.region_id].append(firm)

    # For each municipality
    for mun_code, regions in sim.mun_to_regions.items():
        # Get growth based on historical data
        growth = sim.generator.firm_data.avg_monthly_deltas[int(mun_code)] * sim.PARAMS['PERCENTAGE_ACTUAL_POP']
        growth = int(round(growth))

        # Ignoring shrinkage for now
        if growth <= 0:
            continue

        # Calculate average profit and number of employees for firms in each region
        avg_profit, avg_n_emp = {}, {}
        for region_id in regions:
            firms = firms_by_region[region_id]
            if firms:
                # keep non-negative for probabilities
                avg_profit[region_id] = max(0, sum(f.profit for f in firms)/len(firms))
                avg_n_emp[region_id] = max(0, sum(f.num_employees for f in firms)/len(firms))
            else:
                avg_profit[region_id] = 0
                avg_n_emp[region_id] = 0

        # Compute probabilities that a firm starts in a region, based on that regions' average
        # profit and number of employees
        region_ps = []
        sum_profit = sum(avg_profit.values())
        sum_n_emp = sum(avg_n_emp.values())
        for region_id in regions:
            if sum_profit == 0 and sum_n_emp == 0:
                # Small non-zero probability
                region_ps.append(0.0001)
            else:
                # Equally weight probability from profit and number of employees
                p_profit = avg_profit[region_id]/sum_profit if sum_profit != 0 else 0
                p_n_emp = avg_n_emp[region_id]/sum_n_emp if sum_n_emp != 0 else 0
                region_ps.append((p_profit + p_n_emp)/2)

        # Normalize probabilities
        region_ps = region_ps/np.sum(region_ps)

        # For each new firm, randomly select its region based on the probabilities we computed
        # and then create the new firm
        for _ in range(growth):
            region_id = sim.seed.choices(regions, weights=region_ps)
            region = sim.regions[region_id[0]]
            firm = list(sim.generator.create_firms(1, region).values())[0]
            firm.create_product()
            sim.firms[firm.id] = firm
