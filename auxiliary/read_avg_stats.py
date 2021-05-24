import pandas as pd
from analysis.output import OUTPUT_DATA_SPEC

if __name__ == '__main__':
    file = r'\\storage1\carga\modelo dinamico de simulacao' \
           r'\Exits_python\PS2020\run__2021-02-19T21_03_54.541893\avg\temp_stats.csv'
    out = pd.read_csv(file, sep=';', header=None, names=OUTPUT_DATA_SPEC['stats']['columns'])
