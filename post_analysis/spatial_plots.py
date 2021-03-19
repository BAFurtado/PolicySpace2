from collections import defaultdict

import branca
import folium
import pandas as pd
from folium.plugins import HeatMap


def organize(f):
    f.columns = ['months', 'id', 'long', 'lat', 'size', 'house_value', 'rent', 'quality', 'qli', 'on_market',
                 'family_id', 'region_id', 'mun_id']
    return f


def generate_base_map(lat=-17.8, long=-47.8, default_zoom_start=11):
    return folium.Map(location=[lat, long], control_scale=True, zoom_start=default_zoom_start)


def generate_heatmap(data, gradient, base_map, radius=8):
    HeatMap(data=data, gradient=gradient, radius=radius, max_zoom=2).add_to(base_map)


def generate_legend(col):
    steps = 20
    colormap = branca.colormap.linear.RdYlGn_07.scale(0, 1).to_step(steps)
    colormap.caption = col.capitalize()
    gradient_map = defaultdict(dict)
    for i in range(steps):
        gradient_map[1 / steps * i] = colormap.rgb_hex_str(1 / steps * i)
    return colormap, gradient_map


def normalize_data(data, col):
    mn = data[col].min()
    if mn > 0:
        mn = -mn
    data[col] += mn
    data[col] = data[col]/data[col].max()
    return data


def main(data, col, flag='rent', rad=11):
    base = generate_base_map(-15.77972, -47.92972)
    # data = restrict_quantile(data, col)
    data = normalize_data(data, col)
    heat_ = data[['latitude', 'longitude', col]]
    heat_ = heat_.dropna()
    heat_data = heat_.values.tolist()
    leg, gradient = generate_legend(col)
    generate_heatmap(heat_data, gradient, base, radius=rad)
    leg.add_to(base)
    filepath = f'output/{flag}_{col}_r{rad}.html'
    base.save(filepath)


def basic_description(data):
    print(f'Number observations: {len(data)}')
    print(f'Number unique neighborhoods {len(data.neighbor.unique())}')

    for col in data.columns:
        try:
            print(f'Median values for {col}: {data[col].median():,.4f}')
        except TypeError:
            pass


if __name__ == '__main__':
    # Comparable between REAL and SIMULATED data
    # #######     SIMULATED DATA ###############
    # Read file
    file = r'\\storage1\carga\modelo dinamico de simulacao' \
           r'\Exits_python\PS2020\run__2021-02-19T21_03_54.541893\0/temp_houses.csv'
    file = pd.read_csv(file, sep=';')
    # Add columns
    file = organize(file)
    # Restricting to DF data
    file = file[file.region_id.astype(str).str.startswith('53')]
    # Restricting to last month of simulation
    file = file[file['months'] == '2019-12-01']
    file = file.rename(columns={'lat': 'latitude', 'long': 'longitude'})

    r = 11

    main(file, 'house_value', 'simulated_sales', rad=r)
    main(file, 'rent', 'simulated_rent', rad=r)

    # #######     REAL DATA ###############
    n = 300
    r = 14
    file = f'sensible_sales_{n}.csv'
    real_sales_data = pd.read_csv(file, sep=';')
    basic_description(real_sales_data)
    main(real_sales_data, 'price', 'real_sales', rad=r)

    file = f'sensible_rent_{n}.csv'
    real_rent_data = pd.read_csv(file, sep=';')
    basic_description(real_rent_data)
    main(real_rent_data, 'price', 'real_rent', rad=r)
