import matplotlib.pyplot as plt
import pandas as pd
import seaborn as sns
import numpy as np
from scipy.stats import ks_2samp
from sklearn.preprocessing import scale
from statsmodels.graphics.gofplots import qqplot_2samples as qq
from linear_regressions import normalize_data


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


def prepare_data(file):
    s_sales_price = pd.read_csv(file, sep=';', header=None, usecols=[4, 5])
    s_sales_price['price_util'] = s_sales_price[5] / s_sales_price[4]
    s_sales_price = restrict_quantile(s_sales_price, 'price_util')
    s_sales_price = normalize_data(s_sales_price, 'price_util')
    s_sales_price = s_sales_price[['price_util']]
    s_rent_price = pd.read_csv(file, sep=';', header=None, usecols=[4, 6])
    s_rent_price = s_rent_price.dropna()
    s_rent_price['price_util'] = s_rent_price[6]/s_rent_price[4]
    s_rent_price = restrict_quantile(s_rent_price, 'price_util')
    s_rent_price = normalize_data(s_rent_price, 'price_util')
    s_rent_price = s_rent_price[['price_util']]
    n = 300
    file = f'sensible_sales_{n}.csv'
    real_sales_data = pd.read_csv(file, sep=';', usecols=['price_util'])
    real_sales_data = normalize_data(real_sales_data, 'price_util')
    file = f'sensible_rent_{n}.csv'
    real_rental_data = pd.read_csv(file, sep=';', usecols=['price_util'])
    real_rental_data = normalize_data(real_rental_data, 'price_util')
    return s_sales_price, real_sales_data, s_rent_price, real_rental_data


if __name__ == "__main__":
    # Get Data
    # column 5 - house_prices, column 6 - rent, column 4 - size
    f = r'../output/run__2020-11-04T16_58_43.402477/0/temp_houses.csv'
    s_sales, r_sales, s_rent, r_rent = prepare_data(f)

    plot_qq(s_sales['price_util'], r_sales['price_util'])
    plot_qq(s_rent['price_util'], r_rent['price_util'])

    plot_hist(s_sales['price_util'], r_sales['price_util'])
    plot_hist(s_rent['price_util'], r_rent['price_util'])
