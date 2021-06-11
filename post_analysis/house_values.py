import sys
import warnings
from itertools import combinations

import matplotlib.pyplot as plt
import pandas as pd
import holoviews as hv

hv.extension('bokeh')
hv.output(size=200)

warnings.filterwarnings("ignore", "Only Polygon objects", UserWarning)
warnings.simplefilter(action='ignore', category=FutureWarning)
pd.options.display.float_format = '{:,.2f}'.format

""" Saving code to plot families house prices changes and chord of migration flows among municipalities
"""


def organize(f):
    f.columns = ['months', 'id', 'long', 'lat', 'size', 'house_value', 'rent', 'quality', 'qli', 'on_market',
                 'family_id', 'region_id', 'mun_id']
    return f


def simplify(f):
    return f[['months', 'long', 'lat', 'size', 'house_value', 'quality', 'qli', 'on_market', 'family_id']]


def plot(f):
    # f = organize(f)
    f = f[f['family_id'] != 'None']
    g = (f.sort_values('months').groupby('family_id').filter(lambda g: g.house_value.iat[-1] != g.house_value.iat[0]))
    fplot = g.pivot_table(index='months', columns='family_id', values='house_value')
    fplot.plot(legend=False)
    plt.show()


def basics(f, names, by_what='region_id', name=None):
    g = organize(f)
    # g = g.reset_index(drop=True)
    non = g[g.family_id != 'None']
    vacant = (1 - len(non)/len(g)) * 100
    # vacant_region = g[g['family_id'] == 'None'].groupby(by_what).id.count() / \
    #                 g.groupby(by_what).id.count() * 100
    m239 = g[g.months == '2010-01-01'].house_value.mean()
    perc = (g[g.months == '2019-12-01'].house_value.mean() - m239) / m239 * 100

    move = (non.sort_values('months').groupby('family_id')
            .filter(lambda h: h.house_value.iat[-1] != h.house_value.iat[0]))
    up = (non.sort_values('months').groupby('family_id')
          .filter(lambda h: h.house_value.iat[-1] > h.house_value.iat[0]))
    down = (non.sort_values('months').groupby('family_id')
            .filter(lambda h: h.house_value.iat[-1] < h.house_value.iat[0]))
    num_families = len(set(move.family_id))

    p = 'Families which moved up/downwards weighed by the number of families which moved from a given municipality.'
    up_down = pd.DataFrame()
    up_down['up'] = up[up.months == '2019-12-01'].groupby(by_what).family_id.count() / \
                    move[move.months == '2010-01-01'].groupby(by_what).family_id.count()
    up_down['down'] = down[down.months == '2019-12-01'].groupby(by_what).family_id.count() / \
                      move[move.months == '2010-01-01'].groupby(by_what).family_id.count()

    # stack bar plot
    fig = plt.figure(figsize=(20, 20))
    ax = fig.gca()
    up_down = up_down.merge(names, left_index=True, how='inner', right_on='cod_mun')
    up_down = up_down.set_index('cod_name')
    up_down = up_down[['up', 'down']]
    up_down.sort_values('up').plot(kind='barh', stacked=False, ax=ax)
    ax.set_ylabel("Municipalities")
    plt.yticks(fontsize=24)
    plt.legend(frameon=False)
    plt.savefig(f'output/maps/hist/{name}_hist.png', bbox_inches='tight')
    plt.show()

    print('Vacant houses: {:.2f}%'.format(vacant))
    # print('Vacant houses by municipalities: {}%'.format(vacant_region.to_string()))
    print('Median house values: full base ${:.2f}'.format(g.house_value.median()))
    print('Median house values: occupied ${:.2f}'.format(non.house_value.median()))
    print('Median house values: vacant base ${:.2f}'.format(g[g.family_id=='None'].house_value.median()))
    print('Percentage of increase house prices for given period: {:.2f} %'.format(perc))
    print('Number of families that have moved: {:.0f}. '
          'Percentage of total families {:.2f} %'.format(num_families, num_families / len(set(g.family_id)) * 100))
    print('Upwards {:.2f}% and Downwards {:.2f} %'.format(float(len(set(up.family_id)) / num_families) * 100,
                                                          float(len(set(down.family_id)) / num_families) * 100))
    return g


def prepare_chord(df, names):
    # Cleaning up received DataFrame
    # df = organize(df)
    df = df[['family_id', 'mun_id']]
    tf = df.drop_duplicates(keep='first')
    tl = df.drop_duplicates(keep='last')
    df = pd.concat([tf, tl])

    # Generating nodes and links
    cnxns = []
    for k, g in df.groupby('family_id'):
        [cnxns.extend((n1, n2, len(g)) for n1, n2 in combinations(g['mun_id'], 2))]
    df = pd.DataFrame(cnxns, columns=['region1', 'region2', 'total'])
    df = df.groupby(['region1', 'region2']).agg('sum')
    df = df.reset_index()

    # Chord won't work with duplicated places
    df = df[df.region1 != df.region2]

    # Using only most relevant links
    # df = df[df.total > 100]

    # Associating names
    df = pd.merge(df, names, how='inner', left_on='region1', right_on='cod_mun')
    df = df[['region2', 'total', 'cod_name']]
    df = pd.merge(df, names, how='inner', left_on='region2', right_on='cod_mun')
    df = df[['cod_name_x', 'cod_name_y', 'total']]
    return df


def plot_chord(df, name):
    # Making and saving and showing Chord
    cities = list(set(df.cod_name_x.unique()).union(set(df.cod_name_y.unique())))
    cities_dataset = hv.Dataset(pd.DataFrame(cities, columns=["city"]))
    chord = hv.Chord((df, cities_dataset))
    chord.opts(hv.opts.Chord(height=400, width=400, title="Flow of families among municipalities",
                             node_cmap="Category20", edge_cmap='Category20', edge_color='cod_name_x',
                             labels='city', node_color='city', bgcolor="black", edge_alpha=0.8,
                             edge_line_width=2, node_size=25, label_text_color="white"))

    # To save to figure
    # hv.extension("matplotlib")
    # hv.output(fig='svg', size=250)
    hv.save(chord, f'output/maps/{name}_chord.png')
    # hv.save(chord, f'output/maps/{name}_chord.html')


def cut(f, n=10000):
    f = f.head(n).append(f.tail(n))
    return f


if __name__ == "__main__":
    for each in ['buy', 'wage', 'no_policy', 'rent']:
        location = r'\\storage1\carga\modelo dinamico de simulacao' \
                   fr'\Exits_python\PS2020\POLICIES__2021-06-06T14_22_49.049768\POLICIES={each}\0\temp_houses.csv'
        file = pd.read_csv(location, sep=';', header=None)
        try:
            mun_names = pd.read_csv('./input/names_and_codes_municipalities.csv', sep=';', header=0)
        except FileNotFoundError:
            mun_names = pd.read_csv('../input/names_and_codes_municipalities.csv', sep=';', header=0)
        file = basics(file, mun_names, 'mun_id', name=each)
        # plot(file)

        file = organize(file)
        # print(file.columns)
        chord_base = prepare_chord(file, mun_names)
        plot_chord(chord_base, each)
