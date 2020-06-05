""" This code gives access to output databases.
    NOTE: for convenience and columns labels, we rewrite the data with appropriate column names
    """

import pandas as pd
import auxiliary.read_data_with_columns

pd.set_option('display.max_columns', 13)
pd.set_option('display.max_rows', 240)
pd.set_option('display.float_format', lambda x: '%.4f' % x)


def read(path):
    return pd.read_csv(path, sep=';')


def all_data(lst, p):
    result = dict()
    for each in lst:
        result[each] = read(auxiliary.read_data_with_columns.get_path(each, p))
    return result


if __name__ == '__main__':
    p1 = r'run__2020-06-04T14_13_27.012916'
    auxiliary.read_data_with_columns.main(p1)
    all_ = ['banks', 'construction', 'families', 'firms', 'houses', 'regional', 'stats']
    dp = all_data(all_, p1)
