import os
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import seaborn as sns
from scipy import stats
from statsmodels.graphics.gofplots import qqplot_2samples as qq

from linear_regressions import normalize_data
plt.rcParams['svg.fonttype'] = 'none'


def plot_hist(x, y, name=None, params=None):
    sns.set()
    sns.set_palette("viridis")
    fig = plt.figure()
    # fig.suptitle(params, fontsize=9)
    # fig.subplots_adjust(top=0.85)
    for key in x:
        sns.distplot(x[key], hist=False, kde=True)
    ax = sns.distplot(y, hist=True, kde=True, label='empirical data')
    ax.set(xlabel='Normalized prices per square meter')
    # plt.legend(frameon=False)
    if name:
        # plt.savefig(f'output/{name}.png')
        plt.savefig(f'output/{name}_ps2_book.svg', format='svg', dpi=600)
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
        # plt.savefig(f'output/{name}.png')
        plt.savefig(f'output/{name}_ps2book.svg', format='svg', dpi=600)
    else:
        plt.show()
    plt.close()


def restrict_quantile(data, col, max_q=.9, min_q=.1):
    tmp = data[data[col] < data[col].quantile(max_q)]
    tmp = tmp[tmp[col] > tmp[col].quantile(min_q)]
    return tmp


def prepare_data(folder, real_sales_data=None, real_rental_data=None):
    files = [fi for fi in os.listdir(folder) if fi.isdigit()]
    s_sales_price = dict()
    for file in files:
        path = os.path.join(folder, file, 'temp_houses.csv')
        table = pd.read_csv(path, sep=';', header=None, usecols=[0, 4, 5])
        table = table[table[0] == '2019-12-01']
        table['price_util'] = table[5]/table[4]
        table = table.dropna(subset=['price_util'])
        table = restrict_quantile(table, 'price_util', .97, .03)
        table = normalize_data(table, 'price_util')
        table = table[['price_util']]
        s_sales_price[file] = table

    s_rent_price = pd.read_csv(os.path.join(folder, '0', 'temp_houses.csv'), sep=';', header=None, usecols=[0, 4, 6])
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
    """kolmogorov-smirnov test. if p value is high cannot reject the null hypothesis that
    both samples are from the same distribution, else reject

    'So the null-hypothesis for the KT test is that the distributions are the same.
    'Thus, the lower your p value the greater the statistical evidence you have to reject the null hypothesis
    'and conclude the distributions are different.
    
    """
    ks, p = stats.ks_2samp(rvs1, rvs2)
    return f"{'different' if p < significance_level else 'cannot say is the same'}", \
           f'p_value {p:.4f}', f'ks statistic {ks:.4f}'


def main(file):
    params = os.path.join(file, 'conf.json')

    s_sales, r_sales, s_rent, r_rent = prepare_data(file)

    plot_qq(s_sales['price_util'], r_sales['price_util'], name='qq_sales_' + params[-16:-10], params=params)
    # plot_qq(s_rent['price_util'], r_rent['price_util'], name='qq_rent_' + params[-16:-10], params=params)

    plot_hist(s_sales, r_sales['price_util'], name='h_sales_' + params[-16:-10], params=params)
    # plot_hist(s_rent['price_util'], r_rent['price_util'], name='h_rent_' + params[-16:-10], params=params)

    # print('SALES')
    # print(ks_test(s_sales['price_util'], r_sales['price_util']))
    # print('RENT')
    # print(ks_test(s_rent['price_util'], r_rent['price_util']))


if __name__ == "__main__":
    # Get Data
    # column 5 - house_prices, column 6 - rent, column 4 - size
    # f = sys.argv[1] if sys.argv[1] else f

    f = r'\\storage1\carga\modelo dinamico de simulacao\Exits_python\PS2020\run__2021-07-14T16_10_39.876864'

    main(f)
