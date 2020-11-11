import numpy as np
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import seaborn as sns
from scipy import stats
from statsmodels.graphics.gofplots import qqplot_2samples as qq

from post_analysis.linear_regressions import normalize_data


def plot_hist(x, y):
    sns.set()
    plt.figure()
    sns.distplot(x, hist=True, label='simulated')
    sns.distplot(y, hist=True, label='real')
    plt.legend()
    plt.show()


def plot_qq(x, y):
    # Checking length
    plt.figure()
    if len(x) > len(y):
        x = np.random.choice(x, len(y))
    else:
        y = y[:len(x)]
    qq(x, y, line='45')
    labels = ['simulated', 'real']
    plt.legend(labels)
    plt.show()


def restrict_quantile(data, col, max_q=.9, min_q=.1):
    tmp = data[data[col] < data[col].quantile(max_q)]
    tmp = tmp[tmp[col] > tmp[col].quantile(min_q)]
    return tmp


def prepare_data(file, real_sales_data=None, real_rental_data=None):
    s_sales_price = pd.read_csv(file, sep=';', header=None, usecols=[0, 4, 5])
    s_sales_price = s_sales_price[s_sales_price[0] == '2019-12-01']
    s_sales_price['price_util'] = s_sales_price[5] / s_sales_price[4]
    s_sales_price = restrict_quantile(s_sales_price, 'price_util')
    s_sales_price = normalize_data(s_sales_price, 'price_util')
    s_sales_price = s_sales_price[['price_util']]
    s_rent_price = pd.read_csv(file, sep=';', header=None, usecols=[0, 4, 6])
    s_rent_price = s_rent_price[s_rent_price[0] == '2019-12-01']
    s_rent_price = s_rent_price.dropna()
    s_rent_price['price_util'] = s_rent_price[6]/s_rent_price[4]
    s_rent_price = restrict_quantile(s_rent_price, 'price_util')
    s_rent_price = normalize_data(s_rent_price, 'price_util')
    s_rent_price = s_rent_price[['price_util']]
    if real_sales_data is None:
        file = r'C:\Users\R1702898\Documents\PolicySpace2\post_analysis/sensible_sales_300.csv'
        real_sales_data = pd.read_csv(file, sep=';', usecols=['price_util'])
        real_sales_data = normalize_data(real_sales_data, 'price_util')
        file = r'C:\Users\R1702898\Documents\PolicySpace2\post_analysis/sensible_rent_300.csv'
        real_rental_data = pd.read_csv(file, sep=';', usecols=['price_util'])
        real_rental_data = normalize_data(real_rental_data, 'price_util')
    return s_sales_price, real_sales_data, s_rent_price, real_rental_data


def ks_test(rvs1, rvs2, significance_level=0.1):
    """kolmogorov-smirnov test. if returns True, then cannot reject the null hypothesis that
    both samples are from the same distribution, else reject
    """
    d, p = stats.ks_2samp(rvs1, rvs2)
    return p > significance_level, p, d


if __name__ == "__main__":
    # Get Data
    # column 5 - house_prices, column 6 - rent, column 4 - size
    f = r'../output/run__2020-11-11T12_35_02.282507/0/temp_houses.csv'
    s_sales, r_sales, s_rent, r_rent = prepare_data(f)

    plot_qq(s_sales['price_util'], r_sales['price_util'])
    plot_qq(s_rent['price_util'], r_rent['price_util'])

    plot_hist(s_sales['price_util'], r_sales['price_util'])
    plot_hist(s_rent['price_util'], r_rent['price_util'])

    print(ks_test(s_sales['price_util'], r_sales['price_util']))
    print(ks_test(s_rent['price_util'], r_rent['price_util']))