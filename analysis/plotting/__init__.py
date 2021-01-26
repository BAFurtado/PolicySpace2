import os
import warnings

import matplotlib.pyplot as plt
import pandas as pd

import conf
from . import geo
from ..output import OUTPUT_DATA_SPEC

# map mun code -> name
mun_codes = pd.read_csv('input/names_and_codes_municipalities.csv', sep=';')
mun_codes = dict(zip(mun_codes['cod_mun'], mun_codes['cod_name']))

warnings.filterwarnings("ignore")
try:
    plt.style.use('ggplot')
    plt.set_cmap('Spectral')
except AttributeError:
    pass


class MissingDataError(Exception):
    pass


class Plotter:
    """Manages all plotting of simulation outputs"""
    def __init__(self, run_paths, output_path, params, avg=None):
        # Keep track of params that generated these plots for annotating/titling
        self.params = params

        # List of (label, input data path)
        self.labels, self.run_paths = zip(*run_paths)
        self.avg = avg

        # Create output path (if necessary) for plots
        self.output_path = output_path
        if not os.path.exists(self.output_path):
            os.makedirs(self.output_path)

    def save_fig(self, fig, name, clear=True):
        fig.savefig(
            os.path.join(self.output_path, '{}.{}'.format(name, conf.RUN['PLOT_FORMAT'])),
            format=conf.RUN['PLOT_FORMAT'],
            dpi=conf.RUN['PLOT_DPI'],
            bbox_inches='tight')

        if clear:
            # reset figure
            plt.close(fig)

    def make_plot(self, datas, title, labels, y_label=None):
        """Create plot based on input data"""
        # Annotate title with percentage of actual population used
        p_pop = self.params.get('PERCENTAGE_ACTUAL_POP', conf.PARAMS['PERCENTAGE_ACTUAL_POP'])
        title = '{}\nAgents : {}% of Population'.format(title, p_pop * 100)

        for d in datas:
            plot = d.plot()

        # Create the plot
        plot.legend(loc='best', ncol=3, fancybox=True, shadow=False, framealpha=.25, labels=labels)
        plot.set_title(title)
        plot.set_xlabel('Time')
        if y_label is not None:
            plot.set_ylabel(y_label)
        fig = plot.get_figure()
        fig.set_size_inches(15, 10)
        return fig

    def _prepare_data(self, path, columns):
        # Just read the data
        try:
            dat = pd.read_csv(path,  sep=';', decimal='.', header=None)
        except FileNotFoundError:
            raise MissingDataError
        dat.columns = columns

        # # Time to be eliminated (adjustment of the model)
        if conf.RUN['TIME_TO_BE_ELIMINATED'] > 0:
            dat = dat.loc[len(dat['month']) * conf.RUN['TIME_TO_BE_ELIMINATED']:, :]
        return dat

    def _prepare_datas(self, fname, columns):
        paths = [(label, os.path.join(path, fname)) for label, path in zip(self.labels, self.run_paths)]
        paths = [(label, self._prepare_data(path, columns))
                 for label, path in paths
                 if os.path.exists(path)]
        labels, dats = zip(*paths)
        return labels, dats

    def _load_multiple_runs(self, key, fname):
        spec = OUTPUT_DATA_SPEC[key]
        labels, dats = self._prepare_datas(fname, spec['columns'])
        if self.avg:
            avg_type, avg_path = self.avg
            cols = spec['avg']['columns']
            if cols == 'ALL':
                cols = spec['columns']
            else:
                cols = spec['avg']['groupings'] + cols
            avg_dat = self._prepare_data(os.path.join(avg_path, fname), cols)
            labels = [avg_type] + list(labels)
            dats = [avg_dat] + list(dats)
        return labels, dats

    def _load_single_run(self, key, fname):
        """Some plots can only plot one run at a time.
        Use average if available, otherwise default to first run data."""
        spec = OUTPUT_DATA_SPEC[key]
        if self.avg:
            avg_type, avg_path = self.avg
            cols = spec['avg']['columns']
            if cols == 'ALL':
                cols = spec['columns']
            else:
                cols = spec['avg']['groupings'] + cols
            # return avg_type, self._prepare_data(os.path.join(avg_path, fname), cols)
            return self._prepare_data(os.path.join(avg_path, fname), cols)
        else:
            # return 'run', self._prepare_data(os.path.join(self.run_paths[0], fname), spec['columns'])
            return self._prepare_data(os.path.join(self.run_paths[0], fname), spec['columns'])

    def plot_general(self):
        labels, dats = self._load_multiple_runs('stats', 'temp_stats.csv')

        cols = ['price_index', 'gdp_index', 'gdp_growth', 'unemployment', 'average_workers',
                'families_median_wealth', 'families_wealth',
                'families_commuting', 'families_savings', 'families_helped', 'amount_subsidised',
                'firms_wealth', 'firms_profit', 'gini_index',
                'average_utility', 'pct_zero_consumption', 'rent_default', 'inflation', 'average_qli', 'house_vacancy',
                'house_price', 'house_rent', 'affordable', 'p_delinquent', 'equally', 'locally', 'fpm', 'bank']
        titles = ['Average prices\' level', 'GDP absolute value', 'GDP growth in monthly perc.', 'Unemployment',
                  'Average workers per firm', 'Families median permanent income',
                  'Families\' disposable cash', 'Families\'s total commuting',
                  'Families\' absolute savings', 'Number of families receiving policy help',
                  'Amount of $ implemented by policy',
                  'Firms\' absolute capital', 'Firms\' profit', 'GINI index',
                  'Average families\' utility', 'Percentual families zero consumption',
                  'Percentual default among renting families', 'Monthly inflation',
                  'Average QLI index value', 'House vacancies', 'House prices', 'House rent prices',
                  'Affordable rent (less than 30% permanent income)',
                  'Percentual of delinquent loans', 'Taxes invested equally', 'Taxes invested locally',
                  'Taxes invested via FPM', 'Taxes paid by the banks on top of interests']

        # General plotting
        dats = [d.set_index('month') for d in dats]
        for col, title in zip(cols, titles):
            fig = self.make_plot([d[col] for d in dats], title, labels)
            self.save_fig(fig, 'temp_general_{}'.format(title))

    def plot_banks(self):
        labels, dats = self._load_multiple_runs('banks', 'temp_banks.csv')

        cols = ['balance', 'deposits', 'active_loans', 'mortgage_rate', 'p_delinquent_loans',
                'mean_loan_age', 'mean_loan']
        titles = ['Bank balance', 'Bank deposits', 'Bank active loans', 'Mortage rate',
                  'Bank perc. delinquent loans', 'Bank mean loan age', 'Bank mean loan amount']
        dats = [d.set_index('month') for d in dats]
        for col, title in zip(cols, titles):
            fig = self.make_plot([d[col] for d in dats], title, labels)
            self.save_fig(fig, 'temp_banks_{}'.format(title))

    def plot_houses(self):
        dat = self._load_single_run('houses', 'temp_houses.csv')

        to_plot = {
            'price': {
                'title': 'Mean house prices by month',
                'name': 'prices'
            },
            'on_market': {
                'title': 'Mean house time on market by month',
                'name': 'time_on_market'
            }
        }
        df = dat.groupby(['month', 'mun_id'], as_index=False).mean()
        for k, d in to_plot.items():
            title = d['title']
            name = d['name']
            dat_to_plot = df.pivot(index='month', columns='mun_id', values=k).astype(float)
            names_mun = [mun_codes[v] for v in list(dat_to_plot.columns.values)]
            fig = self.make_plot([dat_to_plot], title, labels=names_mun, y_label='Mean {}'.format(name))
            self.save_fig(fig, 'temp_houses_{}'.format(name))

    def plot_families(self):
        dat = self._load_single_run('families', 'temp_families.csv')
        dat['renting'] = pd.notna(dat['house_rent'])

        to_plot = {
            'house_rent': {
                'title': 'Mean rent value by month',
                'name': 'rents'
            },
            'total_wage': {
                'title': 'Mean total wage by month',
                'name': 'total_wages'
            },
            'savings': {
                'title': 'Mean savings by month',
                'name': 'savings'
            },
            'renting': {
                'title': 'Mean number of families that are renting by month',
                'name': 'renting'
            }
        }

        df = dat.groupby(['month', 'mun_id'], as_index=False).mean()
        for k, d in to_plot.items():
            title = d['title']
            name = d['name']
            dat_to_plot = df.pivot(index='month', columns='mun_id', values=k).astype(float)
            dats_to_plot = [dat_to_plot[c] for c in dat_to_plot.columns.values]
            names_mun = [mun_codes[v] for v in list(dat_to_plot.columns.values)]
            fig = self.make_plot(dats_to_plot, title, labels=names_mun, y_label='Median {}'.format(name))
            self.save_fig(fig, 'temp_families_{}'.format(name))

    def plot_regional_stats(self):
        dat = self._load_single_run('regional', 'temp_regional.csv')
        # TODO: adjusted percentual time off not working for regional plots, neither distributions
        # Time to be eliminated (adjustment of the model)
        # if conf.RUN['TIME_TO_BE_ELIMINATED'] > 0:
        #     dat = dat.loc[len(dat['month']) * conf.RUN['TIME_TO_BE_ELIMINATED']:, :]

        # commuting
        title = 'Evolution of commute by region, monthly'
        dat_to_plot = dat.pivot(index='month', columns='mun_id', values='commuting')
        names_mun = [mun_codes[v] for v in list(dat_to_plot.columns.values)]
        dats_to_plot = [dat_to_plot[c] for c in dat_to_plot.columns.values]
        fig = self.make_plot(dats_to_plot, title, labels=names_mun, y_label='Regional commute')
        self.save_fig(fig, 'temp_regional_evolution_of_commute')

        cols = ['gdp_region', 'regional_gini', 'regional_house_values',
                'gdp_percapita', 'regional_unemployment', 'qli_index', 'pop',
                'treasure', 'licenses']
        titles = ['GDP', 'GINI', 'House values', 'per capita GDP', 'Unemployment', 'QLI index', 'Population',
                  'Total Taxes', 'Land licenses']
        for col, title in zip(cols, titles):
            title = 'Evolution of {} by region, monthly'.format(title)
            dat_to_plot = dat.pivot(index='month', columns='mun_id', values=col).astype(float)
            dats_to_plot = [dat_to_plot[c] for c in dat_to_plot.columns.values]
            fig = self.make_plot(dats_to_plot, title, labels=names_mun, y_label='Regional {}'.format(title))
            self.save_fig(fig, 'temp_regional_{}'.format(title))

        taxes = ['equally', 'locally', 'fpm']
        taxes_labels = ['Taxes distributed Equally', 'Taxes distributed Locally', 'FPM invested']
        for i in taxes:
            dats_to_plot = [dat.groupby(by=['month']).sum()[i]]
            fig = self.make_plot(dats_to_plot, 'Evolution of Taxes', labels=taxes_labels, y_label='Total Taxes')
        self.save_fig(fig, 'temp_TAXES')

    def plot_firms(self):
        dat = self._load_single_run('firms', 'temp_firms.csv')

        cols = ['amount_produced', 'price']
        titles = ['Cumulative sum of amount produced by firm, by month', 'Price values by firm, by month']
        for col, title in zip(cols, titles):
            dat_to_plot = dat.pivot(index='month', columns='firm_id', values=col).astype(float)
            dats_to_plot = [dat_to_plot[c] for c in dat_to_plot.columns.values]
            labels = ['Firm {}'.format(i) for i, _ in enumerate(dat_to_plot.columns.values)]
            fig = self.make_plot(dats_to_plot, title, labels=labels, y_label='Values in units')
            self.save_fig(fig, 'temp_general_{}'.format(col))

        title = 'Median of number of employees by firm, by month'
        firms_stats = dat.groupby(['month', 'firm_id'], as_index=False).median()
        dat_to_plot = firms_stats.pivot(index='month', columns='firm_id', values='number_employees').astype(float)
        dats_to_plot = [dat_to_plot[c] for c in dat_to_plot.columns.values]
        labels = ['Firm {}'.format(i) for i, _ in enumerate(dat_to_plot.columns.values)]
        fig = self.make_plot(dats_to_plot, title, labels=labels, y_label='Median of employees')
        self.save_fig(fig, 'temp_general_median_number_of_employees_by_firm_index')

    def plot_construction(self):
        dat = self._load_single_run('construction', 'temp_construction.csv')
        cols = ['amount_produced', 'price']
        titles = ['Cumulative sum of amount produced by construction firms, by month',
                  'Price values of houses by firm, by month']
        for col, title in zip(cols, titles):
            dat_to_plot = dat.pivot(index='month', columns='firm_id', values=col).astype(float)
            dats_to_plot = [dat_to_plot[c] for c in dat_to_plot.columns.values]
            labels = ['Firm {}'.format(i) for i, _ in enumerate(dat_to_plot.columns.values)]
            fig = self.make_plot(dats_to_plot, title, labels=labels, y_label='Values in units')
            self.save_fig(fig, 'temp_construction_{}'.format(col))

        title = 'Median of number of employees by construction firms, by month'
        firms_stats = dat.groupby(['month', 'firm_id'], as_index=False).median()
        dat_to_plot = firms_stats.pivot(index='month', columns='firm_id', values='number_employees').astype(float)
        dats_to_plot = [dat_to_plot[c] for c in dat_to_plot.columns.values]
        labels = ['Firm {}'.format(i) for i, _ in enumerate(dat_to_plot.columns.values)]
        fig = self.make_plot(dats_to_plot, title, labels=labels, y_label='Median of employees')
        self.save_fig(fig, 'temp_construction_median_number_of_employees_by_firm_index')

    def plot_geo(self, sim, text):
        """Generate spatial plots"""
        figs = geo.plot(sim, text)
        for name, fig in figs:
            fig.savefig(os.path.join(self.output_path,
                                     'temp_spatial_plot_{}_{}.{}'.format(name, text, conf.RUN['PLOT_FORMAT'])),
                        format=conf.RUN['PLOT_FORMAT'], close=True, verbose=True, dpi=600)
            # Reset figure
            plt.close(fig)
        return plt
