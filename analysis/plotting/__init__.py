import os
import warnings

import matplotlib.pyplot as plt
import pandas as pd

import conf
from . import geo

# map mun code -> name
mun_codes = pd.read_csv('input/names_and_codes_municipalities.csv', sep=';')
mun_codes = dict(zip(mun_codes['cod_mun'], mun_codes['cod_name']))

warnings.filterwarnings("ignore")
try:
    plt.style.use('ggplot')
    plt.set_cmap('Spectral')
except AttributeError:
    pass

class MissingDataError(Exception): pass

class Plotter:
    """Manages all plotting of simulation outputs"""

    # Data in SINGLE_ONLY is grouped by mun_id, so we can only plot
    # one run at a time (or one average run)
    SINGLE_ONLY = ['houses', 'families', 'firms', 'construction']

    def __init__(self, input_paths, output_path, params, styles=None):
        # Keep track of params that generated these plots for annotating/titling
        self.params = params

        # List of (label, input data path)
        self.labels, self.input_paths = zip(*input_paths)

        # User can specify style overrides per plot, otherwise use defaults
        self.styles = styles if styles is not None else ['' for _ in self.input_paths]

        # Create output path (if necessary) for plots
        self.output_path = output_path
        if not os.path.exists(self.output_path):
            os.makedirs(self.output_path)

    def save_fig(self, fig, name, clear=True):
        fig.savefig(
            os.path.join(self.output_path, '{}.{}'.format(name, conf.RUN['PLOT_FORMAT'])),
            format=conf.RUN['PLOT_FORMAT'],
            dpi=600,
            bbox_inches='tight')

        if clear:
            plt.close(fig) # reset figure

    def make_plot(self, datas, title, labels, y_label=None):
        """Create plot based on input data"""
        # Annotate title with percentage of actual population used
        p_pop = self.params.get('PERCENTAGE_ACTUAL_POP', conf.PARAMS['PERCENTAGE_ACTUAL_POP'])
        title = '{}\nAgents : {}% of Population'.format(title, p_pop * 100)

        # Apply styles, if any
        for d, style in zip(datas, self.styles):
            plot = d.plot(style=style)

        # Create the plot
        plot.legend(loc='best', ncol=3, fancybox=True, shadow=False, framealpha=.25, labels=labels)
        plot.set_title(title)
        plot.set_xlabel('Time')
        if y_label is not None:
            plot.set_ylabel(y_label)
        # plot.set_axis_bgcolor('w')
        fig = plot.get_figure()
        fig.set_size_inches(15, 10)
        return fig

    def _prepare_data(self, path, columns):
        # Just read the data
        dat = pd.read_csv(path,  sep=';', decimal='.', header=None)
        dat.columns = columns

        # # Time to be eliminated (adjustment of the model)
        if conf.RUN['TIME_TO_BE_ELIMINATED'] > 0:
            dat = dat.loc[len(dat['month']) * conf.RUN['TIME_TO_BE_ELIMINATED']:, :]
        return dat

    def _prepare_datas(self, fname, columns):
        paths = [(label, os.path.join(path, fname)) for label, path in zip(self.labels, self.input_paths)]
        paths = [(label, self._prepare_data(path, columns))
                                 for label, path in paths
                                 if os.path.exists(path)]
        if not paths:
            raise MissingDataError
        labels, dats = zip(*paths)
        return labels, dats

    def plot_general(self):
        labels, dats = self._prepare_datas(
            'temp_stats.csv',
            ['month', 'price_index', 'gdp_index', 'gdp_growth', 'unemployment', 'average_workers',
             'families_wealth', 'families_savings', 'firms_wealth', 'firms_profit', 'gini_index',
             'average_utility', 'inflation', 'average_qli', 'equally', 'locally', 'fpm']
        )

        cols = ['price_index', 'gdp_index', 'gdp_growth', 'unemployment', 'average_workers', 'families_wealth',
                'families_savings', 'firms_wealth', 'firms_profit', 'gini_index', 'average_utility', 'inflation',
                'average_qli','equally', 'locally', 'fpm']
        titles = ['Average prices\' level', 'GDP absolute value', 'GDP growth in % m-m', 'Unemployment',
                'Average workers per firm', 'Families\' disposable cash', 'Families\' absolute savings',
                'Firms\' abolute capital', 'Firms\' profit', 'GINI index', 'Average families\' utility',
                'Monthly inflation', 'Average QLI index value', 'Taxes invested equally', 'Taxes invested locally',
                  'Taxes invested via FPM']

        # General plotting
        dats = [d.set_index('month') for d in dats]
        for col, title in zip(cols, titles):
            fig = self.make_plot([d[col] for d in dats], title, labels)
            self.save_fig(fig, 'temp_general_{}'.format(title))

    def plot_banks(self):
        labels, dats = self._prepare_datas(
            'temp_banks.csv',
            ['month', 'taxes', 'balance', 'deposits',
             'active_loans', 'p_delinquent_loans',
             'mean_loan_age', 'min_loan', 'max_loan', 'mean_loan']
        )
        cols = ['taxes', 'balance', 'deposits',
                'active_loans', 'p_delinquent_loans',
                'mean_loan_age', 'mean_loan']
        titles = ['Bank taxes paid', 'Bank balance', 'Bank deposits', 'Bank active loans',
                  'Bank p delinquent loans', 'Bank mean loan age', 'Bank mean loan amount']
        dats = [d.set_index('month') for d in dats]
        for col, title in zip(cols, titles):
            fig = self.make_plot([d[col] for d in dats], title, labels)
            self.save_fig(fig, 'temp_banks_{}'.format(title))

    def plot_houses(self):
        labels, dats = self._prepare_datas(
            'temp_houses.csv',
            ['month', 'id', 'x', 'y', 'size', 'price', 'on_market', 'family_id', 'region_id', 'mun_id']
        )

        # Because we're plotting by mun_id,
        # can't plot multiple datasets at once
        # Otherwise we have lines per mun_id, per run
        # Which quickly becomes illegible.
        # If you need to see each run's plots,
        # you should plot each run (PLOT_EACH_RUN=True)
        dat = dats[0]
        label = labels[0]

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
            title = '{} ({})'.format(d['title'], label)
            name = d['name']
            dat_to_plot = df.pivot(index='month', columns='mun_id', values=k).astype(float)
            dats_to_plot = [dat_to_plot[c] for c in dat_to_plot.columns.values]
            names_mun = [mun_codes[v] for v in list(dat_to_plot.columns.values)]
            fig = self.make_plot([dat_to_plot], title, labels=names_mun, y_label='Mean {}'.format(name))
            self.save_fig(fig, 'temp_houses_{}'.format(name))

    def plot_families(self):
        labels, dats = self._prepare_datas(
            'temp_families.csv',
            ['month', 'id', 'house_price', 'house_rent', 'house_id', 'house_owner_id', 'house_family_id',
             'region_id', 'mun_id', 'total_wage', 'savings', 'num_members']
        )

        for df in dats:
            df['renting'] = pd.notna(df['house_rent'])
            df['income_towards_rent'] = df['house_rent']/df['total_wage']
            df['affordable_rent'] = (df['income_towards_rent'] <= 0.3) | (pd.isna(df['income_towards_rent']))

        # Because we're plotting by mun_id,
        # can't plot multiple datasets at once
        # Otherwise we have lines per mun_id, per run
        # Which quickly becomes illegible.
        # If you need to see each run's plots,
        # you should plot each run (PLOT_EACH_RUN=True)
        dat = dats[0]
        label = labels[0]

        to_plot = {
            'house_rent': {
                'title': 'Mean rent by month',
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
            'affordable_rent': {
                'title': 'Mean affordability by month',
                'name': 'affordable'
            },
            'income_towards_rent': {
                'title': 'Mean rent as share of income by month',
                'name': 'rent_shares'
            },
            'renting': {
                'title': 'Mean is renting by month',
                'name': 'renting'
            }
        }

        df = dat.groupby(['month', 'mun_id'], as_index=False).mean()
        for k, d in to_plot.items():
            title = '{} ({})'.format(d['title'], label)
            name = d['name']
            dat_to_plot = df.pivot(index='month', columns='mun_id', values=k).astype(float)
            dats_to_plot = [dat_to_plot[c] for c in dat_to_plot.columns.values]
            names_mun = [mun_codes[v] for v in list(dat_to_plot.columns.values)]
            fig = self.make_plot(dats_to_plot, title, labels=names_mun, y_label='Mean {}'.format(name))
            self.save_fig(fig, 'temp_families_{}'.format(name))


    def plot_regional_stats(self):
        labels, dats = self._prepare_datas(
            'temp_regional.csv',
            ['month', 'mun_id', 'commuting', 'pop', 'gdp_region', 'regional_gini', 'regional_house_values',
            'regional_unemployment', 'qli_index', 'gdp_percapita', 'treasure', 'equally', 'locally', 'fpm',
             'licenses']
        )

        # commuting
        title = 'Evolution of commute by region, monthly'
        dats_to_plot = [d.pivot(index='month', columns='mun_id', values='commuting') for d in dats]
        names_mun = [mun_codes[v] for v in list(dats_to_plot[0].columns.values)]
        fig = self.make_plot(dats_to_plot, title, labels=names_mun, y_label='Regional commute')
        self.save_fig(fig, 'temp_regional_evolution_of_commute')

        cols = ['gdp_region', 'regional_gini', 'regional_house_values',
                'gdp_percapita', 'regional_unemployment', 'qli_index', 'pop',
                'treasure', 'licenses']
        titles = ['GDP', 'GINI', 'House values', 'per capita GDP', 'Unemployment', 'QLI index', 'Population',
                'Total Taxes', 'Land licenses']
        for col, title in zip(cols, titles):
            title = 'Evolution of {} by region, monthly'.format(title)
            dats_to_plot = [d.pivot(index='month', columns='mun_id', values=col).astype(float) for d in dats]
            fig = self.make_plot(dats_to_plot, title, labels=names_mun, y_label='Regional {}'.format(title))
            self.save_fig(fig, 'temp_regional_{}'.format(title))

        # Plotting
        taxes = ['equally', 'locally', 'fpm']
        taxes_labels = ['Taxes distributed Equally', 'Taxes distributed Locally', 'FPM invested']

        for i in taxes:
            dats_to_plot = [d.groupby(by=['month']).sum()[i] for d in dats]
            fig = self.make_plot(dats_to_plot, 'Evolution of Taxes', labels=taxes_labels, y_label='Total Taxes')
        self.save_fig(fig, 'temp_TAXES')

    def plot_firms(self):
        labels, dats = self._prepare_datas(
            'temp_firms.csv',
            ['month', 'firm_id', 'region_id', 'mun_id', 'long', 'lat', 'total_balance$', 'number_employees',
            'stocks', 'amount_produced', 'price', 'amount_sold', 'revenue', 'profit', 'wages_paid']
        )

        cols = ['amount_produced', 'price']
        titles = ['Cumulative sum of amount produced by firm, by month', 'Price values by firm, by month']
        for col, title in zip(cols, titles):
            dats_to_plot = [d.pivot(index='month', columns='firm_id', values=col).astype(float) for d in dats]
            fig = self.make_plot(dats_to_plot, title, labels, y_label='Values in units')
            self.save_fig(fig, 'temp_general_{}'.format(col))

        # Median of number of employees by firm, by region
        title = 'Median of number of employees by firm, by month'
        dats_to_plot = []
        for d in dats:
            firms_stats = d.groupby(['month', 'mun_id'], as_index=False).median()
            dat_to_plot = firms_stats.pivot(index='month', columns='mun_id', values='number_employees').astype(float)
            dats_to_plot.append(dat_to_plot)
        names_mun = [mun_codes[v] for v in list(dats_to_plot[0].columns.values)]
        fig = self.make_plot(dats_to_plot, title, labels=names_mun, y_label='Median of employees')
        self.save_fig(fig, 'temp_general_median_number_of_employees_by_firm_index')

        # Mean of number of employees by firm, by region
        title = 'Mean of number of employees by firm, by month'
        dats_to_plot = []
        for d in dats:
            firms_stats = d.groupby(['month', 'mun_id'], as_index=False).mean()
            dat_to_plot = firms_stats.pivot(index='month', columns='mun_id', values='number_employees').astype(float)
            dats_to_plot.append(dat_to_plot)
        fig = self.make_plot(dats_to_plot, title, labels=names_mun, y_label='Mean of employees')
        self.save_fig(fig, 'temp_general_mean_number_of_employees_by_firm_index')

    def plot_construction(self):
        labels, dats = self._prepare_datas(
            'temp_construction.csv',
            ['month', 'firm_id', 'region_id', 'mun_id', 'long', 'lat', 'total_balance$', 'number_employees',
            'stocks', 'amount_produced', 'price', 'amount_sold', 'revenue', 'profit', 'wages_paid']
        )

        cols = ['amount_produced', 'price']
        titles = ['Cumulative sum of amount produced by firm, by month', 'Price values by firm, by month']
        for col, title in zip(cols, titles):
            dats_to_plot = [d.pivot(index='month', columns='firm_id', values=col).astype(float) for d in dats]
            fig = self.make_plot(dats_to_plot, title, labels, y_label='Values in units')
            self.save_fig(fig, 'temp_construction_{}'.format(col))

        # Median of number of employees by firm, by region
        title = 'Median of number of employees by region, by month'
        dats_to_plot = []
        for d in dats:
            firms_stats = d.groupby(['month', 'mun_id'], as_index=False).median()
            dat_to_plot = firms_stats.pivot(index='month', columns='firm_id', values='number_employees').astype(float)
            dats_to_plot.append(dat_to_plot)
        names_mun = [mun_codes[v] for v in list(dats_to_plot[0].columns.values)]
        fig = self.make_plot(dats_to_plot, title, labels=names_mun, y_label='Median of employees')
        self.save_fig(fig, 'temp_construction_median_number_of_employees_by_firm_index')

        # Mean of number of employees by firm, by region
        title = 'Mean of number of employees by firm, by month'
        dats_to_plot = []
        for d in dats:
            firms_stats = d.groupby(['month', 'mun_id'], as_index=False).mean()
            dat_to_plot = firms_stats.pivot(index='month', columns='firm_id', values='number_employees').astype(float)
            dats_to_plot.append(dat_to_plot)
        fig = self.make_plot(dats_to_plot, title, labels=names_mun, y_label='Mean of employees')
        self.save_fig(fig, 'temp_construction_mean_number_of_employees_by_firm_index')

    def plot_geo(self, sim, text):
        """Generate spatial plots"""
        figs = geo.plot(sim, text)
        for name, fig in figs:
            fig.savefig(os.path.join(self.output_path,
                                     'temp_spatial_plot_{}_{}.{}'.format(name, text,conf.RUN['PLOT_FORMAT'])),
                        format=conf.RUN['PLOT_FORMAT'], close=True, verbose=True, dpi=600)
            plt.close(fig) # reset figure
        return plt
