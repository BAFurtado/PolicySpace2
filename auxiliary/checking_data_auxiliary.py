""" This code gives access to output databases.
    NOTE: for convenience and columns lables, run `read_data_with_columns.py` first """


import os

import pandas as pd

from conf.default import run
pd.set_option('display.max_columns', 13)
pd.set_option('display.max_rows', 240)
pd.set_option('display.float_format', lambda x: '%.4f' % x)


def read(path):
    return pd.read_csv(path, sep=';')


def all_data(l, p):
    result = dict()
    for each in l:
        result[each] = read(get_path(each, p))
    return result


def get_path(cols='houses', path=None):
    p0 = r'/home/furtadobb/MyModels/PolicySpace2'
    p = run.OUTPUT_PATH
    path = path
    p3 = r'0/temp_'
    p4 = '.csv'
    return os.path.join(p0, p, path, p3 + cols + p4)


if __name__ == '__main__':
    p1 = r'run__2020-05-22T18_53_17.538787'
    p2 = r'run__2020-05-29T15_06_05.615645'
    all_ = ['banks', 'construction', 'families', 'firms', 'houses', 'regional', 'stats']
    dt = all_data(all_, p2)
    dp = all_data(all_, p1)
