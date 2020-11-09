import matplotlib.pyplot as plt
import pandas as pd
import seaborn as sns
from scipy.stats import ks_2samp
from sklearn.preprocessing import scale
from statsmodels.graphics.gofplots import qqplot_2samples as qq
from linear_regressions import normalize_data


def plot_qq(x, y):
    # Checking length
    if len(x) > len(y):
        x = x[:len(y)]
    else:
        y = y[:len(x)]
    qq(x, y, line='45')
    plt.show()


def plot_density_test_ks(x, y):
    sns.set()
    plt.figure()
    sns.distplot(x, hist=False)
    sns.distplot(y, hist=False)
    # plt.legend()
    plot_qq(x, y)


def plot_general_real_model(x, y):
    fig, ax = plt.subplots()
    sns.set()
    plt.plot(x, y)
    plt.show()


def prepare_data(file):
    s_sales_price = pd.read_csv(file, sep=';', header=None, usecols=[5])
    s_sales_price = normalize_data(s_sales_price, 5)
    s_rent_price = pd.read_csv(file, sep=';', header=None, usecols=[6])
    s_rent_price = s_rent_price.dropna()
    n = 300
    file = f'sensible_sales_{n}.csv'
    real_sales_data = pd.read_csv(file, sep=';', usecols=['price'])
    real_sales_data = normalize_data(real_sales_data, 'price')
    file = f'sensible_rent_{n}.csv'
    real_rental_data = pd.read_csv(file, sep=';', usecols=['price'])
    real_rental_data = normalize_data(real_rental_data, 'price')
    return s_sales_price, real_sales_data, s_rent_price, real_rental_data


if __name__ == "__main__":
    # Get Data
    # column 5 - house_prices, column 6 - rent
    f = r'../output/run__2020-11-09T18_39_50.100306/0/temp_houses.csv'
    s_sales, r_sales, s_rent, r_rent = prepare_data(f)

    plot_density_test_ks(s_sales[5], r_sales['price'])
    plot_density_test_ks(s_rent[6], r_rent['price'])

    plot_general_real_model(s_sales[5], r_sales['price'])
    plot_general_real_model(s_rent[6], r_rent['price'])
