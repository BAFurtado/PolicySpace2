""" This script reads all databases and rewrites them with columns' names
"""

import os
import pandas as pd

from conf.default import run

pd.set_option('display.max_columns', 13)
pd.set_option('display.max_rows', 240)

files = ['stats', 'regional', 'time', 'firms', 'banks',
         'houses', 'agents', 'families', 'grave', 'construction']

stats = ['month', 'price_index', 'gdp_index', 'gdp_growth', 'unemployment', 'average_workers',
         'families_median_wealth', 'families_wealth', 'families_commuting', 'families_savings',
         'families_helped', 'amount_subsidised', 'firms_wealth', 'firms_profit',
         'gini_index', 'average_utility', 'pct_zero_consumption', 'rent_default', 'inflation', 'average_qli',
         'house_vacancy', 'house_price', 'house_rent', 'affordable', 'p_delinquent', 'equally', 'locally',
         'fpm', 'bank']

banks = ['sim.clock.days', 'bank.taxes', 'bank.balance', 'bank.total_deposits', 'n_active', 'p_delinquent',
         ' mean_age', 'mn', 'mx', 'avg']

construction = ['sim.clock.days', 'firm.id', 'firm.region_id', 'firm.region_id', 'firm.address.x', 'firm.address.y',
                'firm.total_balance', 'firm.num_employees', 'firm.total_quantity', 'len(firm.houses)',
                'firm.mean_house_price', 'firm.n_houses_sold', 'firm.revenue', 'firm.profit', 'firm.wages_paid']

firms =['sim.clock.days', 'firm.id', 'firm.region_id', 'firm.region_id', 'firm.address.x', 'firm.address.y',
        'firm.total_balance', 'firm.num_employees', 'firm.total_quantity', 'firm.amount_produced',
        'firm.inventory[0].price', 'firm.amount_sold', 'firm.revenue', 'firm.profit', 'firm.wages_paid']

regional = ['sim.clock.days', 'mun_id', 'commuting', 'mun_pop', 'mun_gdp', 'mun_gini', 'mun_house_values',
            'mun_unemployment', 'mun_qli', 'GDP_mun_capita', 'mun_cumulative_treasure', 'equally',  'locally', 'fpm',
            'licenses']

families = ['sim.clock.days', 'id', 'region_id', 'house.price', 'house.rent_data', 'total_wage', 'family.savings',
            'num_members']

houses = ['sim.clock.days', 'house.id', 'house.address.x', 'house.address.y', 'house.size', 'house.price',
          'rent_price', 'quality', 'qli',
          'house.on_market', 'house.family_id', 'house.region_id', 'house.mun_id']


def read_allocate_cols(path, cols=None):
    output = pd.read_csv(path, sep=';')
    output.columns = cols
    output.to_csv(path, index=False, sep=';')
    return output


def main(path):
    full_list = ['banks', 'construction', 'families', 'firms', 'houses', 'regional', 'stats']
    cols = [banks, construction, families, firms, houses, regional, stats]
    for i in range(len(full_list)):
        pf = get_path(cols=full_list[i], path=path)
        out = read_allocate_cols(pf, cols[i])
    return out


def get_path(cols='houses', path=None):
    p0 = r'/home/furtadobb/MyModels/PolicySpace2'
    p = run.OUTPUT_PATH
    p3 = r'0/temp_'
    p4 = '.csv'
    return os.path.join(p0, p, path, p3 + cols + p4)


if __name__ == '__main__':
    p = get_path('banks')
