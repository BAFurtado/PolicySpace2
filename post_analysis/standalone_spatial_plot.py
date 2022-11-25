import glob

import geopandas as gpd
import matplotlib.pyplot as plt
import pandas as pd
from matplotlib import cm
from shapely.geometry import Point
from sklearn.preprocessing import MinMaxScaler

from analysis.output import OUTPUT_DATA_SPEC

scaler = MinMaxScaler(feature_range=(0, 1))


def get_mun_codes(acp='BRASILIA'):
    codes = pd.read_csv('../input/ACPs_MUN_CODES.csv', sep=';')
    return set(codes[codes['ACPs'] == acp]['cod_mun'].to_list())


def prepare_data(path):
    # Get list of files
    place = f"{path}/**/0/temp_houses.csv"
    house_list = glob.iglob(place, recursive=True)
    # Separate into policy categories

    policies = dict()
    cols = OUTPUT_DATA_SPEC['houses']['columns']
    for each in house_list:
        for pol in ['no_policy', 'wage', 'buy', 'rent']:
            if pol in each:
                policies[pol] = pd.read_csv(each, sep=';', names=cols)
                policies[pol] = policies[pol][policies[pol].month == '2019-12-01']
                policies[pol] = policies[pol][['x', 'y', 'price', 'size']]
                policies[pol]['price_util'] = policies[pol]['price'] / policies[pol]['size']
                # Normalized
                policies[pol]['price_util'] = scaler.fit_transform(policies[pol][['price_util']])
                # Adding point geometry on pandas DataFrame
                policies[pol]['geometry'] = [Point(xy) for xy in zip(policies[pol].x, policies[pol].y)]
                # Creating geodataframe
                policies[pol] = gpd.GeoDataFrame(policies[pol], geometry='geometry')
    # Plot and save
    # return house_list
    return policies


def restrict_quantile(data, col, max_q=.95, min_q=.05):
    tmp = data[data[col] < data[col].quantile(max_q)]
    tmp = tmp[tmp[col] > tmp[col].quantile(min_q)]
    return tmp


def prepare_real_data(path):
    r = pd.read_csv(path, sep=';')
    r = r.dropna(subset=['longitude', 'latitude', 'price_util'])
    r = restrict_quantile(r, 'price_util', .97, .03)
    for col in r.columns:
        print(r[col].describe())
    r.to_csv('spatial_plotted_data.csv', sep=';')
    r = r[['longitude', 'latitude', 'price_util']]
    r.columns = ['x', 'y', 'price_util']
    r['price_util'] = scaler.fit_transform(r[['price_util']])
    # Adding point geometry on pandas DataFrame
    r['geometry'] = [Point(xy) for xy in zip(r.x, r.y)]
    # Creating geodataframe
    r = gpd.GeoDataFrame(r, geometry='geometry')
    return r


def plot(family_coords, name, c='inferno'):
    """Generate a spatial plot"""
    cmap = cm.get_cmap(c)

    # Loading the shapefiles
    full_region = gpd.read_file('../input/shapes/mun_ACPS_ibge_2014_latlong_wgs1984_fixed.shp')
    urban_region = gpd.read_file('../input/shapes/URBAN_IBGE_ACPs.shp')

    plots = ['price_util']

    for p in plots:
        # Starting the plot
        fig, ax = plt.subplots(figsize=(15, 15), subplot_kw={'aspect': 'equal'})

        # plotting each polygon in the selection process (based on mun_codes)
        # All municipalities
        # Urban areas (ACPs IBGE)
        mun_codes = get_mun_codes()
        for index in mun_codes:
            shape_select = urban_region[urban_region['GEOCODI'] == str(index)]
            shape_select.plot(ax=ax, color='black', linewidth=0.2, alpha=.2)

        for index in mun_codes:
            shape_select = full_region[full_region['CD_GEOCMU'] == str(index)]
            shape_select.plot(ax=ax, color='grey', linewidth=1, alpha=.7, edgecolor='black')

        # Plotting families locations
        ax = family_coords.plot(ax=ax, column=p, cmap=cmap, markersize=13, marker='.', alpha=.5)

        minx, miny, maxx, maxy = -48.5, -16.3, -47.6, -15.4
        ax.set_xlim(minx, maxx)
        ax.set_ylim(miny, maxy)

        cax = fig.add_axes([0.9, 0.1, 0.03, 0.8])
        sm = plt.cm.ScalarMappable(cmap=c, norm=plt.Normalize(vmin=0, vmax=1))
        sm._A = []
        fig.colorbar(sm, cax=cax)

        # Adding the grid location, title, axes labels
        ax.grid(True, color='grey', linestyle='-')
        # ax.set_title(p.capitalize().replace('_', ' '))
        ax.set_xlabel('Longitude (in degrees)')
        ax.set_ylabel('Latitude (in degrees)')
        for item in ([ax.xaxis.label, ax.yaxis.label] +
                     ax.get_xticklabels() + ax.get_yticklabels()):
            item.set_fontsize(17)
        plt.savefig(f'output/maps/{name}_bookps2.svg', format='svg', bbox_inches='tight')
        plt.close()
        # plt.show()


if __name__ == '__main__':
    pa = r'\\storage1\carga\MODELO DINAMICO DE SIMULACAO\Exits_python\PS2020\POLICIES__2021-06-06T14_22_49.049768'
    ps = prepare_data(pa)
    p2 = 'sensible_sales_300.csv'
    real = prepare_real_data(p2)
    for key in ps:
        plot(ps[key], key)
    plot(real, 'real')
