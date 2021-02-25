import datetime
import os

import matplotlib.pyplot as plt
import pandas as pd

from analysis.output import OUTPUT_DATA_SPEC as cols


def prepare_data(file, labels):
    database = dict()
    for each in os.listdir(file):
        d = pd.read_csv(os.path.join(file, each), header=None, sep=';', names=labels)
        d['month'] = pd.to_datetime(d.month).dt.date
        d = d[d.loc[:, 'month'] > datetime.date(2011, 1, 1)]
        database[each.split('.')[0][9:]] = d
    return database


def plot(database, lbls, dpi=720, ft='png'):
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
            n = f'output/{lb}.{ft}'
            plt.savefig(n)
            plt.show()


if __name__ == '__main__':
    dta = pd.read_csv('../output/run__2021-02-19T22_04_55.601592_temp_stats.csv', sep=';', header=None)
    dta.columns = cols['stats']['columns']

    # dta.gdp_index.plot()
    # plt.show()

    f = r'../PS_text/policy_data'
    data = prepare_data(f, dta.columns)
    # plot(prepare_data(f, dta.columns), cols['stats']['columns'])
