import os
import datetime
import glob

import matplotlib.pyplot as plt
import pandas as pd

from analysis.output import OUTPUT_DATA_SPEC as cols


def prepare_data(filepaths, labels):
    database = dict()
    for each in filepaths:
        key = each.split('=')[1].split('\\')[0]
        d = pd.read_csv(each, header=None, sep=';', names=labels)
        d['month'] = pd.to_datetime(d.month).dt.date
        d = d[d.loc[:, 'month'] > datetime.date(2011, 1, 1)]
        database[key] = d
    return database


def plot(database, lbls, path, dpi=720, ft='png'):
    colors = {'buy': 'tab:red', 'no_policy': 'tab:orange', 'rent': 'tab:blue', 'wage': 'tab:green'}
    fmts = {'gdp_index': '{:.0f}',
            'families_median_wealth': '{:.2f}',
            'gini_index': '{:.3f}',
            'average_utility': '{:.2f}'}

    for lb in lbls:
        # if lb in ['gdp_index', 'families_median_wealth', 'gini_index', 'average_utility']:
        if lb not in ['month']:
            fig, ax = plt.subplots(dpi=dpi)
            for i, data in enumerate(database):
                database[data].plot('month', lb, ax=ax, linewidth=2, color=colors[data])
            ax.spines['top'].set_visible(False)
            ax.spines['bottom'].set_visible(True)
            ax.spines['right'].set_visible(False)
            ax.spines['left'].set_visible(True)
            ax.get_xaxis().tick_bottom()
            ax.get_yaxis().tick_left()
            ax.get_legend().remove()
            fmt = fmts[lb] if lb in fmts else '{:.2f}'
            ax.yaxis.set_major_formatter(plt.FuncFormatter(fmt.format))
            ax.set(xlabel='Year')
            plt.grid(True, 'major', 'y', ls='-', lw=.5, c='k', alpha=.3)

            plt.tick_params(axis='both', which='both', bottom=False, top=False,
                            labelbottom=True, left=False, right=False, labelleft=True)
            n = os.path.join(path, f'{lb}.{ft}')
            plt.savefig(n)
            # plt.show()


def organizing_files_avg_policy(path):
    return [f for f in glob.glob(path + '/**/avg/temp_stats.csv', recursive=True)]


if __name__ == '__main__':
    dta = pd.read_csv(r'\\storage1\carga\modelo dinamico de simulacao\Exits_python\PS2020'
                      r'\run__2021-02-19T21_03_54.541893/0/temp_stats.csv', sep=';', header=None)
    dta.columns = cols['stats']['columns']

    # dta.gdp_index.plot()
    # plt.show()
    p = r'\\storage1\carga\modelo dinamico de simulacao\Exits_python\PS2020' \
        r'\POLICIES__2021-02-19T22_39_56.035769'
    pths = organizing_files_avg_policy(p)
    data = prepare_data(pths, dta.columns)
    plot(data, dta.columns, p)
