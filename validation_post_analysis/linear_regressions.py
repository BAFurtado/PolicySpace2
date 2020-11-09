#!/usr/bin/env python3
# -*- coding: utf-8 -*-
""" Regression comparison
"""

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import seaborn as sns
import statsmodels.api as sm
# With SM you need to add the constant yourself, basically, I guess
import statsmodels.formula.api as smf


def basic_description(data, cols=None):
    print(f'Number observations: {len(data)}')
    # print(f'Number unique neighborhoods {len(data.neighbor.unique())}')

    for col in data.columns if not cols else cols:
        try:
            print(f'Median values for {col}: {data[col].median():,.4f}')
            print(f'Min values for {col}: {data[col].min():,.4f}')
            print(f'Max values for {col}: {data[col].max():,.4f}')
        except TypeError:
            pass


def normalize_data(data, col):
    mn = data[col].min()
    if mn > 0:
        mn = -mn
    data[col] += mn
    data[col] = data[col]/data[col].max()
    return data


def reg(col, data, optional_col=""):
    """ Função que roda as regressões
        Entre com colunas e com base de dados """
    res = smf.ols("{} ~  {}".format(col, optional_col), data=data).fit()
    sns.distplot(res.resid)
    plt.show()
    return res


def reg2(y, x, name):
    """ Função que roda as regressões
        Entre com x e y"""
    x = sm.add_constant(x)
    res = sm.OLS(y, x).fit()
    sns.distplot(res.resid)
    plt.title(name)
    plt.show()
    return res


def add_columns(f):
    f.columns = ['months', 'id', 'long', 'lat', 'size', 'house_value', 'rent', 'quality', 'qli', 'on_market',
                 'family_id', 'region_id', 'mun_id']
    return f


def cut(f, n=10000):
    f = f.head(n).append(f.tail(n))
    return f


def reg_simulated(data, cols_x, col_y='house_value', name='sales'):
    data = data[data['months'] == '2019-12-01']
    x = data[cols_x]
    y = data[[col_y]]
    regression(x, y, f'simulated_{name}')


def reg_realdata(data, cols_x, col_y='price', name='sales'):
    x = data[cols_x]
    y = data[[col_y]]
    regression(x, y, f'real_{name}')


def regression(x, y, name):
    lm1 = reg2(y, x.astype(np.float), name)
    print(lm1.summary())
    # Gravação de resultados
    with open(f'output/{name}1.md', 'w') as f:
        f.write(lm1.summary().as_text())

    results = pd.DataFrame(lm1.params)
    results.reset_index().to_csv(f'output/{name}_params_results.csv', sep=';', index=False)


def auxiliar_cols_names(data, names):
    for col in data.columns:
        try:
            data.rename(columns={col: '_' + names.loc[int(col.split('_')[-1])]['ap_name']}, inplace=True)
        except:
            pass
    return data


def plot_distribution(data, col, title):
    plt.hist(data[col], bins=200)
    plt.title(title)
    plt.show()


def prepare_simulated_data(loc, year=2010):
    if year == 2010:
        _2010 = True
        names = pd.read_csv('ap_code_name_2010.csv', sep=';').set_index('ap_code')
    else:
        _2010 = False
        names = pd.read_csv('ap_code_name_2000.csv', sep=';').set_index('ap_code')
    data = pd.read_csv(loc, sep=';')
    try:
        data = data.drop(['Unnamed: 0'], axis=1)
    except KeyError:
        pass
    data = add_columns(data)
    spatial = 'region_id'
    # SPATIAL RESTRICTION. Keeping only observations from Brasilia
    data = data[data['region_id'].astype(str).str.startswith('53')]
    data = data.replace({"region_id": names['ap_name']})
    data = pd.get_dummies(data, columns=[spatial])

    # Price per area data
    data['price_area'] = data['house_value'] / data['size']

    # Exclude 'lat', 'long'
    cols = ['size', 'quality']
    print('-------- BASIC DESCRIPTION -- SIMULATED DATA ---------')
    basic_description(data, cols + ['house_value'])
    basic_description(data, ['price_area'])
    data = normalize_data(data, 'house_value')
    for col in cols:
        data = normalize_data(data, col)

    # Adding correct neighborhood names for datasets
    if not _2010:
        asa_sul = 'region_id_asa sul300'
        dummies_cols = [col for col in data if col.startswith(spatial) and col != asa_sul]
    else:
        asa_sul = 'region_id_asa sul'
        # data_sim = auxiliar_cols_names(data_sim, names)
        dummies_cols = [col for col in data if col.startswith(spatial) and col != asa_sul]
    return data, cols + dummies_cols


def plot_basic_data(data):
    plot_distribution(data, 'house_value', 'simulated')
    plot_distribution(data, 'price_area', 'simulated_util')


def prepare_real_data(data):
    # Exclude 'latitute', 'longitude'
    cols = ['n_rooms', 'n_bathrooms', 'parking', 'util']
    data = data.dropna(subset=cols)
    print('-------- BASIC DESCRIPTION -- REAL     DATA ---------')
    basic_description(data, cols + ['price'])
    data.loc[:, 'neighbor'] = data.neighbor.str.replace(' ', '_').str[:12]
    data = pd.get_dummies(data, columns=['neighbor'], drop_first=True)

    # SPATIAL RESTRICTION AND BASELINE
    asa_sul = 'neighbor_asa_sul'
    dummies_cols = [col for col in data if col.startswith('neighbor') and col != asa_sul]
    data = normalize_data(data, 'price')
    data = normalize_data(data, 'price_util')
    for col in cols:
        data = normalize_data(data, col)
    return data, cols + dummies_cols


if __name__ == '__main__':
    # # # # #      S I M U L A T E D     # # # # #
    # Enter file location for simulated data
    file = r'input/reduced_house_rental_.3.csv'
    simulated_data, cols = prepare_simulated_data(file)
    plot_basic_data(simulated_data)

    print('SIMULATED DATA SALES REGRESSION')
    reg_simulated(simulated_data, cols)

    print('SIMULATED DATA RENTAL REGRESSION')
    rent_simulated = simulated_data.dropna()
    reg_simulated(rent_simulated, cols, 'rent', 'rent')

    # # # # #      R  E  A  L     # # # # #
    # Enter file location for REAL data
    n = 300
    print('REAL DATA SALES REGRESSION')
    file = f'sensible_sales_{n}.csv'
    real_sales_data = pd.read_csv(file, sep=';')
    real_sales_data, cols = prepare_real_data(real_sales_data)
    plot_distribution(real_sales_data, 'price', 'real_price')
    plot_distribution(real_sales_data, 'price_util', 'real_price_util')
    reg_realdata(real_sales_data, cols)

    print('REAL DATA RENTAL REGRESSION')
    file = f'sensible_rent_{n}.csv'
    real_rental_data = pd.read_csv(file, sep=';')
    real_rental_data, cols = prepare_real_data(real_rental_data)
    reg_realdata(real_rental_data, cols, 'price', 'rent')
