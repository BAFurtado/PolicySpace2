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

    def calculate_house_vacancy(self, houses, log=True):
        vacants = np.sum([1 for h in houses if houses[h].family_id is None])
        num_houses = len(houses)
        if log:
            logger.info(f'Vacant houses {vacants:,.0f}')
            logger.info(f'Total houses {num_houses:,.0f}')
        return vacants / num_houses

    def calculate_house_price(self, houses):
        return np.average([h.price for h in houses.values()])

    def calculate_rent_price(self, houses):
        return np.average([h.rent_data[0] for h in houses.values() if h.rent_data is not None])

    def calculate_affordable_rent(self, families):
        affordable = np.sum([1 if family.is_renting
                          and family.get_permanent_income() != 0
                          and (family.house.rent_data[0] / family.get_permanent_income()) < .3 else 0
                          for family in families.values()])
        renting = np.sum([family.is_renting for family in families.values()])
        return affordable / renting

    def update_GDP_capita(self, firms, mun_id, mun_pop):
        dummy_gdp = np.sum([firms[firm].revenue for firm in firms.keys()
                            if firms[firm].region_id[:7] == mun_id])
        if mun_pop > 0:
            dummy_gdp_capita = dummy_gdp / mun_pop
        else:
            dummy_gdp_capita = dummy_gdp
        return dummy_gdp_capita

    def update_unemployment(self, agents, global_u=False):
        employable = [m for m in agents if 16 < m.age < 70]
        temp = len([m for m in employable if m.firm_id is None])/len(employable) if employable else 0
        logger.info(f'Unemployment rate: {temp * 100:.2f}')
        if global_u:
            self.global_unemployment_rate = temp
        return temp

    def calculate_average_workers(self, firms):
        dummy_avg_workers = np.sum([firms[firm].num_employees for firm in firms.keys()])
        return dummy_avg_workers / len(firms)

    # Calculate wealth: families, firms and profits
    def calculate_families_median_wealth(self, families):
        return np.median([family.get_permanent_income() for family in families.values()])

    def calculate_families_wealth(self, families):
        dummy_wealth = np.sum([families[family].get_permanent_income() for family in families.keys()])
        dummy_savings = np.sum([families[family].savings for family in families.keys()])
        return dummy_wealth, dummy_savings

    def calculate_rent_default(self, families):
        return np.sum([1 for family in families.values() if family.rent_default == 1 and family.is_renting]) / \
               np.sum([1 for family in families.values() if family.is_renting])

    def calculate_firms_wealth(self, firms):
        return np.sum([firms[firm].total_balance for firm in firms.keys()])

    def calculate_firms_median_wealth(self, firms):
        return np.median([firms[firm].total_balance for firm in firms.keys()])

    def zero_consumption(self, families):
        return np.sum([1 for family in families.values() if family.average_utility == 0]) / len(families)

    def calculate_firms_profit(self, firms):
        return np.sum([firms[firm].profit for firm in firms.keys()])

    # Calculate inequality (GINI)
    def calculate_utility(self, families):
        return np.average([families[family].average_utility for family in families.keys()
                           if families[family].num_members > 0])

    def calculate_GINI(self, families):
        family_data = [families[family].get_permanent_income() for family in families.keys()]
        # Sort smallest to largest
        cumm = np.sort(family_data)
        # Values cannot be 0
        cumm += .0000001
        # Find cumulative totals
        n = cumm.shape[0]
        index = np.arange(1, n + 1)
        gini = ((np.sum((2 * index - n - 1) * cumm)) / (n * np.sum(cumm)))
        logger.info(f'GINI: {gini:.3f}')
        return gini

    def calculate_regional_GINI(self, families):
        family_data = [family.get_permanent_income() for family in families]
        # Sort smallest to largest
        cumm = np.sort(family_data)
        # Values cannot be 0
        cumm += .0000001
        # Find cumulative totals
        n = cumm.shape[0]
        index = np.arange(1, n + 1)
        if n == 0:
            return 0
        gini = ((np.sum((2 * index - n - 1) * cumm)) / (n * np.sum(cumm)))
        return gini

    def update_commuting(self, families):
        """Total commuting distance"""
        dummy_total = 0.
        for family in families:
            for member in family.members.values():
                if member.is_employed:
                    dummy_total += member.distance
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
