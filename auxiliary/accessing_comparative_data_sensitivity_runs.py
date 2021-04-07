import os
from shutil import copyfile

import numpy as np
import pandas as pd

from analysis.output import OUTPUT_DATA_SPEC as cols
import read_meta_json


def moving_files(path1, path2):
    path = os.path.join(path1, path2)
    dirs = os.listdir(path)
    for each in dirs:
        if '=' in each and '.csv' not in each:
            t_path = os.path.join(path, each, 'avg', 'temp_stats.csv')
            destination = f'{path}/{each}.csv'
            copyfile(t_path, destination)


def reading_summarizing_tables(path1, path2, col='families_helped'):
        d = pd.read_csv(os.path.join(path1, path2, t), sep=';', names=cols['stats']['columns'])
        return f'{t}: avg {col} {np.mean(d[col]):.2f}\n'


if __name__ == '__main__':
    p1 = r'\\storage1\carga\modelo dinamico de simulacao\Exits_python\PS2020'
    fls = os.listdir(p1)
    interest = [f for f in fls if f.startswith('POLICIES')]
    for run in interest:
        try:
            moving_files(p1, run)
        except FileNotFoundError:
            continue
        with open(f'{p1}/Report_{run}.txt', 'a') as f:
            f.write(read_meta_json.read_meta(p1, run))
            for each in cols['stats']['columns'][1:]:
                tables = [f for f in os.listdir(os.path.join(p1, run)) if f.endswith('.csv')]
                for t in tables:
                    f.write(reading_summarizing_tables(p1, run, each))
                f.write('_____________\n')
