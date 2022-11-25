import os

import matplotlib.pyplot as plt
import pandas as pd
import matplotlib.dates as mdates
from matplotlib.dates import DateFormatter

from analysis.output import OUTPUT_DATA_SPEC as cols


def plot(database, lbls, path, dpi=360, ft='png'):
    for lb in lbls:
        if lb not in ['month']:
            fig, ax = plt.subplots(dpi=dpi)
            for i, data in enumerate(database):
                ax.plot(pd.to_datetime(database[data]['month']), database[data]['avg'], linewidth=2,
                        color=colors[data], label=data)
                ax.plot(pd.to_datetime(database[data]['month']), database[data]['upper_table'], linewidth=.6,
                        color=colors[data])
                ax.plot(pd.to_datetime(database[data]['month']), database[data]['lower_table'], linewidth=.6,
                        color=colors[data])
                ax.fill_between(pd.to_datetime(database[data]['month']),
                                database[data]['upper_table'],
                                database[data]['lower_table'],
                                facecolor=colors[data], alpha=.7)
            ax.spines['top'].set_visible(False)
            ax.spines['bottom'].set_visible(True)
            ax.spines['right'].set_visible(False)
            ax.spines['left'].set_visible(True)
            ax.get_xaxis().tick_bottom()
            ax.get_yaxis().tick_left()
            ax.legend(frameon=False)
            # ax.get_legend().remove()
            fmt = fmts[lb] if lb in fmts else '{:.0f}'
            date_form = DateFormatter("%Y")
            ax.xaxis.set_major_formatter(date_form)
            ax.yaxis.set_major_formatter(plt.FuncFormatter(fmt.format))
            ax.set(xlabel='Year')
            plt.grid(True, 'major', 'y', ls='-', lw=.5, c='k', alpha=.3)

            plt.tick_params(axis='both', which='both', bottom=False, top=False,
                            labelbottom=True, left=False, right=False, labelleft=True)
            n = os.path.join(path, f'{lb}_R1.{ft}')
            plt.savefig(n)
            plt.show()
            plt.close(fig)


def getting_data(folders, col):
    files = [fi for fi in os.listdir(folders) if fi.isdigit()]
    data = pd.DataFrame(columns=['month'] + col)
    for file in files:
        path = os.path.join(folders, file, 'temp_stats.csv')
        table = pd.read_csv(path, sep=';', names=cols['stats']['columns'])
        table = table[['month'] + col]
        data = data.append(table)
    return data


def calculate_bounds(data, col):
    database = pd.DataFrame()
    database['upper_table'] = data.groupby(by='month').quantile(.75).reset_index()[col]
    database['lower_table'] = data.groupby(by='month').quantile(.25).reset_index()[col]
    database['avg'] = data.groupby(by='month').agg('mean').reset_index()[col]
    database['month'] = data.groupby(by='month').agg('max').reset_index()['month']
    return database


if __name__ == '__main__':
    w_false = r'\\storage1\carga\MODELO DINAMICO DE SIMULACAO\Exits_python\PS2020\WAGE_IGNORE_UNEMPLOYMENT__2021-02-22T08_13_37.848876\WAGE_IGNORE_UNEMPLOYMENT=False\avg\temp_stats.csv'
    w_true = r'\\storage1\carga\MODELO DINAMICO DE SIMULACAO\Exits_python\PS2020\WAGE_IGNORE_UNEMPLOYMENT__2021-02-22T08_13_37.848876\WAGE_IGNORE_UNEMPLOYMENT=True\avg\temp_stats.csv'
    lbs = [True, False]
    options = ['Unemployment influence on wages', 'Ignore unemployment influence on wages']
    colors = {options[0]: 'tab:red', options[1]: 'tab:green'}
    fmts = {options[0]: '{:.1f}',
            options[1]: '{:.1f}'}
    # f = pd.read_csv(w_false, sep=';', names=cols['stats']['columns'])
    # t = pd.read_csv(w_true, sep=';', names=cols['stats']['columns'])
    ls = ['firms_profit']
    f_true = r'\\storage1\carga\MODELO DINAMICO DE SIMULACAO\Exits_python\PS2020\WAGE_IGNORE_UNEMPLOYMENT__2021-02-22T08_13_37.848876\WAGE_IGNORE_UNEMPLOYMENT=True'
    f_false = r'\\storage1\carga\MODELO DINAMICO DE SIMULACAO\Exits_python\PS2020\WAGE_IGNORE_UNEMPLOYMENT__2021-02-22T08_13_37.848876\WAGE_IGNORE_UNEMPLOYMENT=False'

    f = getting_data(f_false, ls)
    t = getting_data(f_true, ls)
    f = calculate_bounds(f, ls[0])
    t = calculate_bounds(t, ls[0])
    plot({options[0]: f, options[1]: t}, ls, 'output')
