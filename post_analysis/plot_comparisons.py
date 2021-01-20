import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import seaborn as sns
from scipy import stats
from statsmodels.graphics.gofplots import qqplot_2samples as qq

from linear_regressions import normalize_data
import sys

def plot_hist(x, y, name=None, params=None):
    sns.set()
    fig = plt.figure()
    fig.suptitle(params, fontsize=9)
    fig.subplots_adjust(top=0.85)
    sns.distplot(x, hist=True, kde=True, label='simulated')
    sns.distplot(y, hist=True, kde=True, label='real')
    plt.legend()
    if name:
        plt.savefig(f'output/{name}.png')
    else:
        plt.show()
    plt.close()


def plot_qq(x, y, name=None, params=None):
    # Checking length
    sns.set()
    if len(x) > len(y):
        x = np.random.choice(x, len(y))
    else:
        y = y[:len(x)]
    fig = qq(x, y, line='45')
    fig.suptitle(params, fontsize=9)
    fig.subplots_adjust(top=0.85)
    labels = ['simulated', 'real']
    plt.legend(labels, frameon=False)
    if name:
        plt.savefig(f'output/{name}.png')
    else:
        plt.show()
    plt.close()


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
        file = r'../post_analysis/sensible_sales_300.csv'
        real_sales_data = pd.read_csv(file, sep=';', usecols=['price_util'])
        real_sales_data = normalize_data(real_sales_data, 'price_util')
        file = r'../post_analysis/sensible_rent_300.csv'
        real_rental_data = pd.read_csv(file, sep=';', usecols=['price_util'])
        real_rental_data = normalize_data(real_rental_data, 'price_util')
    return s_sales_price, real_sales_data, s_rent_price, real_rental_data


def ks_test(rvs1, rvs2, significance_level=0.1):
    """kolmogorov-smirnov test. if returns True, then cannot reject the null hypothesis that
    both samples are from the same distribution, else reject
    """
    d, p = stats.ks_2samp(rvs1, rvs2)
    return p > significance_level, p, d


def main(file):
    params = file[:-17] + 'conf.json'

    s_sales, r_sales, s_rent, r_rent = prepare_data(file)

    plot_qq(s_sales['price_util'], r_sales['price_util'], name='qq_sales_' + params[-16:-10], params=params)
    plot_qq(s_rent['price_util'], r_rent['price_util'], name='qq_rent_' + params[-16:-10], params=params)

    plot_hist(s_sales['price_util'], r_sales['price_util'], name='h_sales_' + params[-16:-10], params=params)
    plot_hist(s_rent['price_util'], r_rent['price_util'], name='h_rent_' + params[-16:-10], params=params)

    print(ks_test(s_sales['price_util'], r_sales['price_util']))
    print(ks_test(s_rent['price_util'], r_rent['price_util']))


if __name__ == "__main__":
    # Get Data
    # column 5 - house_prices, column 6 - rent, column 4 - size
    f = r'//storage1/carga/modelo dinamico de simulacao/exits_python/ps2020/' \
        r'LOAN_TO_VALUE__2021-01-12T14_07_23.738101\LOAN_TO_VALUE=0.1/0/temp_houses.csv'
    # f = sys.argv[1] if sys.argv[1] else f
    main(f)
