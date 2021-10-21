import os
import datetime
import glob

import matplotlib.pyplot as plt
import pandas as pd

from analysis.output import OUTPUT_DATA_SPEC as cols


def prepare_data(filepaths, labels):
    keys = ['buy', 'rent', 'wage', 'no_policy']
    database = dict()
    for key in keys:
        database[key] = pd.DataFrame()
        for each in filepaths:
            this_key = each.split('=')[1].split('\\')[0]
            if key == this_key:
                d = pd.read_csv(each, header=None, sep=';', names=labels)
                d['month'] = pd.to_datetime(d.month).dt.date
                database[key] = database[key].append(d[d.loc[:, 'month'] > datetime.date(2011, 1, 1)])
    return database


def plot(database, lbls, path, dpi=720, ft='png'):
    colors = {'buy': 'tab:red', 'no_policy': 'tab:orange', 'rent': 'tab:blue', 'wage': 'tab:green'}
    fmts = {'gdp_index': '{:.0f}',
            'gini_index': '{:.3f}',
            'average_qli': '{:.3f}',
            'house_price': '{:.0f}',
            'pct_zero_consumption': '{:.3f}',
            'rent_default': '{:.3f}'}

    for lb in lbls:
        if lb in ['gdp_index', 'gini_index', 'average_qli', 'house_price', 'rent_default',
                  'pct_zero_consumption']:
            if lb not in ['month']:
                fig, ax = plt.subplots(dpi=dpi)
                for i, data in enumerate(database):
                    ax.plot(database[data]['avg']['month'], database[data]['avg'][lb], linewidth=.2,
                            color=colors[data], label=data, alpha=.6)
                    ax.plot(database[data]['upper_table']['month'], database[data]['upper_table'][lb], linewidth=.5,
                            color=colors[data])
                    ax.plot(database[data]['upper_table']['month'], database[data]['lower_table'][lb], linewidth=.5,
                            color=colors[data])
                    ax.fill_between(pd.to_datetime(database[data]['avg']['month']),
                                    database[data]['upper_table'][lb],
                                    database[data]['lower_table'][lb],
                                    facecolor=colors[data], alpha=.5)
                ax.spines['top'].set_visible(False)
                ax.spines['bottom'].set_visible(True)
                ax.spines['right'].set_visible(False)
                ax.spines['left'].set_visible(True)
                ax.get_xaxis().tick_bottom()
                ax.get_yaxis().tick_left()
                # ax.get_legend().remove()
                fmt = fmts[lb] if lb in fmts else '{:.4f}'
                ax.yaxis.set_major_formatter(plt.FuncFormatter(fmt.format))
                ax.set(xlabel='Year')
                plt.grid(True, 'major', 'y', ls='-', lw=.5, c='k', alpha=.3)

                plt.tick_params(axis='both', which='both', bottom=False, top=False,
                                labelbottom=True, left=False, right=False, labelleft=True)
                n = os.path.join(path, f'{lb}.{ft}')
                plt.savefig(f"output/{lb}_R1.{ft}")
                # plt.savefig(n)
                plt.show()
                plt.close(fig)


def transform_into_avg_quartiles(database):
    data = dict()
    for key in database:
        data[key] = dict()
        data[key]['avg'] = database[key].groupby(by='month').agg('mean').reset_index()
        data[key]['upper_table'] = database[key].groupby(by='month').quantile(.75).reset_index()
        data[key]['lower_table'] = database[key].groupby(by='month').quantile(.25).reset_index()
    return data


def organizing_files_avg_policy(path):
    return [f for f in glob.glob(path + '/**/**/temp_stats.csv', recursive=True) if 'avg' not in f]


if __name__ == '__main__':
    p = r'\\storage1\carga\modelo dinamico de simulacao' \
        r'\Exits_python\PS2020\POLICIES__2021-02-19T22_39_56.035769'
    # r'\Exits_python\PS2020\POLICIES__2021-02-25T11_28_10.744348'

    pths = organizing_files_avg_policy(p)
    dat = prepare_data(pths,  cols['stats']['columns'])
    dat = transform_into_avg_quartiles(dat)
    plot(dat,  cols['stats']['columns'], p)
