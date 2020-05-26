""" This code gives access to output databases. For convenience and columns lables, run `read_data_with_columns.py`
    first """

import os

import pandas as pd

from conf.default import run
pd.set_option('display.max_columns', 13)
pd.set_option('display.max_rows', 240)
pd.set_option('display.float_format', lambda x: '%.4f' % x)


def read(path):
    return pd.read_csv(path, sep=';')


if __name__ == '__main__':
    # all = ['banks', 'construction', 'families', 'firms', 'houses', 'regional', 'stats']

    cols = 'families'
    p0 = r'/home/furtadobb/MyModels/PolicySpace2'
    p = run.OUTPUT_PATH
    p2 = r'run__2020-05-22T18_53_17.538787'
    p3 = r'0/temp_'
    p4 = '.csv'
    pf = os.path.join(p0, p, p2, p3 + cols + p4)
    out = read(pf)
