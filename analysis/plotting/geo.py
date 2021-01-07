import geopandas
import pandas as pd
import matplotlib.pyplot as plt
from shapely.geometry import Point
from sklearn.preprocessing import MinMaxScaler
from matplotlib import cm

scaler = MinMaxScaler(feature_range=(0, 1))


def gen_coords(group, family_factor=False):
    coords = pd.DataFrame(columns=[
        'lat', 'long', 'savings', 'house_values', 'members',
        'balance', 'employees', 'taxes_paid', 'profit', 'renting'
    ])

    # Selecting the coordinates of firms
    for item in group:
        if family_factor:
            if item.num_members > 0:
                coords = coords.append([{
                    'lat': item.address.y,
                    'long': item.address.x,
                    'savings': item.savings,
                    'house_values': item.house.price,
                    'members': item.num_members,
                    'renting': item.is_renting
                }])
        else:
            coords = coords.append([{
                'lat': item.address.y,
                'long': item.address.x,
                'balance': item.total_balance,
                'employees': item.num_employees,
                'taxes_paid': item.taxes_paid,
                'profit': item.profit
            }])

    if family_factor:
        cols = ['savings', 'house_values', 'members']
    else:
        cols = ['balance', 'employees', 'taxes_paid', 'profit']
    coords[cols] = scaler.fit_transform(coords[cols])

    # Adding point geometry on pandas DataFrame
    coords['geometry'] = [Point(xy) for xy in zip(coords.long, coords.lat)]

    # Creating geodataframe
    return geopandas.GeoDataFrame(coords, geometry='geometry')


def plot(sim, text):
    """Generate a spatial plot"""
    cmap = cm.get_cmap('viridis')
    firms_coords = gen_coords(sim.firms.values())
    family_coords = gen_coords(sim.families.values(), True)

    # Loading the shapefiles
    full_region = geopandas.read_file('input/shapes/mun_ACPS_ibge_2014_latlong_wgs1984_fixed.shp')
    urban_region = geopandas.read_file('input/shapes/URBAN_IBGE_ACPs.shp')

    family_plots = ['savings', 'house_values', 'members', 'renting']
    plots = ['savings', 'house_values', 'members', 'renting', 'balance', 'employees', 'taxes_paid', 'profit']
    figs = []

    for p in plots:
        # Starting the plot
        fig, ax = plt.subplots(figsize=(15, 15), subplot_kw={'aspect': 'equal'})

        # plotting each polygon in the selection process (based on mun_codes)
        # All municipalities
        # Urban areas (ACPs IBGE)
        for index in sim.geo.mun_codes:
            shape_select = urban_region[urban_region['GEOCODI'] == str(index)]
            shape_select.plot(ax=ax, color='black', linewidth=0.2, alpha=.2)

        for index in sim.geo.mun_codes:
            shape_select = full_region[full_region['CD_GEOCMU'] == str(index)]
            shape_select.plot(ax=ax, color='grey', linewidth=0.5, alpha=.7, edgecolor='black')

        # Plotting the firms and families locations
        # Using colormap suggestion from: https://stackoverflow.com/questions/36008648/colorbar-on-geopandas
        if p in family_plots:
            ax = family_coords.plot(ax=ax, column=p, cmap=cmap, markersize=12, marker='.', alpha=.5)
        else:
            ax = firms_coords.plot(ax=ax, column=p, cmap=cmap, markersize=10, marker='.', alpha=.5)

        cax = fig.add_axes([0.9, 0.1, 0.03, 0.8])
        sm = plt.cm.ScalarMappable(cmap='viridis', norm=plt.Normalize(vmin=0, vmax=1))
        sm._A = []
        fig.colorbar(sm, cax=cax)

        # Adding the grid location, title, axes labels
        ax.grid(True, color='grey', linestyle='-')
        ax.set_title(p.capitalize().replace('_', ' '))
        ax.set_xlabel('Longitude (in degrees)')
        ax.set_ylabel('Latitude (in degrees)')
        figs.append((p, fig))

    return figs
