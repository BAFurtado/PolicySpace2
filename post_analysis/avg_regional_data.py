""" Replicating it here because average over regional data was not chosen at running time. """

import os
import pandas as pd

from glob import glob
from collections import defaultdict
from analysis.output import OUTPUT_DATA_SPEC as cols

mun_list = pd.read_csv('../input/names_and_codes_municipalities.csv', header=0, sep=';', decimal=',')
mun_list.columns = ['name', 'mun_id', 'state']


def average_run_data(path, avg='mean'):
    """Average the run data for a specified output path"""
    output_path = os.path.join(path, 'avg')
    if not os.path.exists(output_path):
        os.makedirs(output_path)

    # group by filename
    file_groups = defaultdict(list)
    keep_files = {'temp_{}.csv'.format(k): k for k in ['regional']}
    for file in glob(os.path.join(path, '**/*.csv')):
        fname = os.path.basename(file)
        if fname in keep_files:
            file_groups[fname].append(file)

    # merge
    for fname, files in file_groups.items():
        spec = cols[keep_files[fname]]
        dfs = []
        for f in files:
            df = pd.read_csv(f,  sep=';', decimal='.', header=None)
            dfs.append(df)
        df = pd.concat(dfs)
        df.columns = spec['columns']

        # Saving date before averaging
        avg_cols = spec['avg']['columns']
        if avg_cols == 'ALL':
            avg_cols = [c for c in spec['columns'] if c not in spec['avg']['groupings']]

        # Ensure these columns are numeric
        df[avg_cols] = df[avg_cols].apply(pd.to_numeric)

        dfg = df.groupby(spec['avg']['groupings'])
        dfg = dfg[avg_cols]
        df = getattr(dfg, avg)()
        # "ungroup" by
        df = df.reset_index()
        df.to_csv(os.path.join(output_path, fname), header=False, index=False, sep=';')
    return output_path


def get_output(path, col='regional_gini', file='regional', month='2019-12-01'):
    data = pd.read_csv(path, sep=';')
    data.columns = cols[file]['columns']
    data = data[data.month == month]
    data = data[['mun_id', col]]
    data = pd.merge(data, mun_list, on='mun_id')
    return data[['name', col]]


if __name__ == '__main__':
    c = 'regional_gini'
    out = pd.DataFrame(columns=['name', c])
    for each in ['buy', 'wage', 'no_policy', 'rent']:
        p = r'\\storage1\carga\MODELO DINAMICO DE SIMULACAO\Exits_python\PS2020' \
            fr'\POLICIES__2021-02-19T22_39_56.035769\POLICIES={each}'
        average_run_data(p)
        p2 = r'\\storage1\carga\MODELO DINAMICO DE SIMULACAO\Exits_python\PS2020' \
            fr'\POLICIES__2021-02-19T22_39_56.035769\POLICIES={each}\avg\temp_regional.csv'
        d = get_output(p2, col=c)
        d[each] = d[c]
        d = d[['name', each]]
        out = pd.concat([out, d], axis=1)
    out.to_csv(f'output/policy_{c}.csv', sep=';', encoding='latin-1')


