import conf
import logging
import numpy as np
from collections import defaultdict

logger = logging.getLogger('stats')

if conf.RUN['PRINT_STATISTICS_AND_RESULTS_DURING_PROCESS']:
    logger.setLevel(logging.INFO)
else:
    logger.setLevel(logging.ERROR)


class Statistics(object):
    """
    The statistics class is just a bundle of functions together without a permanent instance of data.
    Thus, every time it is called Statistics() it is initiated anew.
    The functions include average price of the firms, regional GDP - based on FIRMS' revenues, GDP per
    capita, unemployment, families' wealth, GINI, regional GINI and commuting information.
    """
    def __init__(self):
        self.previous_month_price = 0
        self.global_unemployment_rate = .05

    def update_price(self, firms):
        """Compute average price and inflation"""
        dummy_average_price = 0
        dummy_num_products = 0
        for firm in firms:
            for key in list(firms[firm].inventory.keys()):
                if firms[firm].inventory[key].quantity == 0 or firms[firm].num_employees == 0:
                    break
            dummy_average_price += firms[firm].inventory[key].price
            dummy_num_products += 1
        if dummy_average_price == 0 or dummy_num_products == 0:
            average_price = 0
        else:
            average_price = dummy_average_price / dummy_num_products

        # Use saved price to calculate inflation
        if self.previous_month_price != 0:
            inflation = (average_price - self.previous_month_price) / self.previous_month_price
        else:
            inflation = 0

        logger.info('Price average: %.3f, Monthly inflation: %.3f' % (average_price, inflation))

        # Save current prices to be used next month
        self.previous_month_price = average_price
        return average_price, inflation

    def calculate_region_GDP(self, firms, region):
        """GDP based on FIRMS' revenues"""
        # Added value for all firms in a given period
        region_GDP = np.sum([firms[firm].revenue for firm in firms.keys() if firms[firm].region_id
                             == region.id])
        region.gdp = region_GDP
        return region_GDP

    def calculate_avg_regional_house_price(self, regional_families):
        return np.average([f.house.price for f in regional_families if f.num_members > 0])

    def update_GDP_capita(self, firms, mun_id, mun_pop):
        dummy_gdp = np.sum([firms[firm].revenue for firm in firms.keys()
                            if firms[firm].region_id[:7] == mun_id])
        if mun_pop > 0:
            dummy_gdp_capita = dummy_gdp / mun_pop
        else:
            dummy_gdp_capita = dummy_gdp
        return dummy_gdp_capita

    def update_unemployment(self, agents, global_u=False):
        dummy_out_workforce = 0
        dummy_employed = 0
        dummy_unemployed = 0

        for agent in agents:
            if agent.is_minor or agent.is_retired:
                dummy_out_workforce += 1
            else:
                if agent.is_employed:
                    dummy_employed += 1
                else:
                    dummy_unemployed += 1

        if (dummy_unemployed + dummy_employed) == 0:
            dummy_temp = 0
        else:
            dummy_temp = (dummy_unemployed / (dummy_unemployed + dummy_employed)) * 100

        logger.info('Unemployment rate: %.2f' % dummy_temp)

        if global_u:
            self.global_unemployment_rate = dummy_temp
        return dummy_temp

    def calculate_average_workers(self, firms):
        dummy_avg_workers = np.sum([firms[firm].num_employees for firm in firms.keys()])
        return dummy_avg_workers / len(firms)

    # Calculate wealth: families, firms and profits
    def calculate_families_median_wealth(self, families):
        return np.median([family.get_total_balance() for family in families])

    def calculate_families_wealth(self, families):
        dummy_wealth = np.sum([families[family].get_total_balance() for family in families.keys()])
        dummy_savings = np.sum([families[family].savings for family in families.keys()])
        return dummy_wealth, dummy_savings

    def calculate_firms_wealth(self, firms):
        return np.sum([firms[firm].total_balance for firm in firms.keys()])

    def calculate_firms_median_wealth(self, firms):
        return np.median([firms[firm].total_balance for firm in firms.keys()])

    def calculate_firms_profit(self, firms):
        return np.sum([firms[firm].profit for firm in firms.keys()])

    # Calculate inequality (GINI)
    def calculate_utility(self, families):
        return np.average([families[family].average_utility for family in families.keys()
                           if families[family].num_members > 0])

    def calculate_GINI(self, families):
        family_data = [families[family].average_utility for family in families.keys()
                       if families[family].num_members > 0]

        # Sort smallest to largest
        cumm = np.sort(family_data)

        # Find cumulative totals
        index = np.arange(1, cumm.shape[0] + 1)
        n = cumm.shape[0]
        assert(n > 0), 'Empty list of values'
        giniIdx = ((np.sum((2 * index - n - 1) * cumm)) / (n * np.sum(cumm)))

        logger.info('GINI: %.3f' % (giniIdx))
        return giniIdx

    def calculate_regional_GINI(self, families):
        family_data = [family.average_utility for family in families if family.num_members > 0]

        # Sort smallest to largest
        cumm = np.sort(family_data)

        # Find cumulative totals
        index = np.arange(1, cumm.shape[0] + 1)
        n = cumm.shape[0]
        if n == 0:
            return 0
        giniIdx = ((np.sum((2 * index - n - 1) * cumm)) / (n * np.sum(cumm)))
        return giniIdx

    def update_commuting(self, families):
        """Total commuting distance"""
        dummy_total = 0.
        for family in families:
            for member in family.members.values():
                if member.is_employed:
                    dummy_total += member.commute
        return dummy_total

    def average_qli(self, regions):
        # group by municipality
        mun_regions = defaultdict(list)
        for id, region in regions.items():
            mun_code = id[:7]
            mun_regions[mun_code].append(region.index)

        average = 0
        for indices in mun_regions.values():
            mun_qli = sum(indices)/len(indices)
            average += mun_qli
        return average / len(mun_regions)

    def sum_region_gdp(self, firms, regions):
        gdp = 0
        _gdp = 0
        for region in regions.values():
            _gdp += region.gdp
            region_gdp = self.calculate_region_GDP(firms, region)
            gdp += region_gdp
        if gdp == 0:
            gdp_growth = 1
        else:
            gdp_growth = ((gdp - _gdp)/gdp) * 100
        logger.info('GDP index variation: {:.2f}%'.format(gdp_growth))
        return gdp, gdp_growth
