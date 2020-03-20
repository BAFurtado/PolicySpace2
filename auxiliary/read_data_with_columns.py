import pandas as pd

from conf.default import run


files = ['stats', 'regional', 'time', 'firms', 'banks',
         'houses', 'agents', 'families', 'grave', 'construction']

stats = ['sim.clock.days', 'price_index', 'gdp_index', 'gdp_growth', 'unemployment', 'average_workers',
         'families_wealth', 'families_savings', 'firms_wealth', 'firms_profit', 'gini_index', 'average_utility',
         'inflation', 'average_qli',  'equally', 'locally', 'fpm']

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
          'house.on_market', 'house.family_id', 'house.region_id', 'house.region_id']


def read_allocate_cols(path, cols):
    output = pd.read_csv(path, sep=';')
    output.columns = cols
    output.to_csv(path, index=False, sep=';')
    return output


if __name__ == '__main__':
    all = ['banks', 'construction', 'families', 'firms', 'houses', 'regional', 'stats']
    cols = [banks, construction, families, firms, houses, regional, stats]
    # all = ['stats']
    # cols = [stats]
    p = run.OUTPUT_PATH
    p2 = r'\run__2020-03-20T13_14_17.548359'
    p3 = r'\0\temp_'
    p4 = '.csv'
    for i in range(len(all)):
        out = read_allocate_cols(p + p2 + p3 + all[i] + p4, cols[i])
