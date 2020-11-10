from scipy import stats

from post_analysis.plot_comparisons import prepare_data


def ks_test(rvs1, rvs2, significance_level=0.1):
    """kolmogorov-smirnov test. if returns True, then cannot reject the null hypothesis that
    both samples are from the same distribution, else reject
    """
    d, p = stats.ks_2samp(rvs1, rvs2)
    return p > significance_level, p, d


if __name__ == '__main__':
    # Get Data
    # column 5 - house_prices, column 6 - rent
    file = r'../output/run__2020-11-04T16_58_43.402477/0/temp_houses.csv'
    s_sales, r_sales, s_rent, r_rent = prepare_data(file)

    print(ks_test(s_sales['price_util'], r_sales['price_util']))
    print(ks_test(s_rent['price_util'], r_rent['price_util']))
