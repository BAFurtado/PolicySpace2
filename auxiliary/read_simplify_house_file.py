import pandas as pd
import glob
from post_analysis.smirnov_kolmogorov_test import ks_test
from post_analysis.plot_comparisons import prepare_data


def simplify(data):
    return data[data[0] == '2019-12-01']


def get_all_house_data(place):
    place = f"{place}/**/**/**/temp_houses.csv"
    return glob.iglob(place, recursive=True)


def run_tests(places):
    for place in places:
        if 'avg' not in place:
            s_sales_price, real_sales_data, s_rent_price, real_rental_data = prepare_data(place)
            print(f'Sales {ks_test(s_sales_price, real_sales_data)}')
            print(f'Rent {ks_test(s_rent_price, real_rental_data)}')


if __name__ == '__main__':
    d = r'\\STORAGE1\CARGA\MODELO DINAMICO DE SIMULACAO\Exits_python\PS2020'
    all = get_all_house_data(d)
    run_tests(all)
    # loc = r'\\STORAGE1\CARGA\MODELO DINAMICO DE SIMULACAO\Exits_python\PS2020' \
    #        r'\RENTAL_SHARE__2020-11-03T23_17_41.490300\RENTAL_SHARE=0.3\0\temp_houses.csv'
    # file = pd.read_csv(loc, sep=';', header=None)
    # file = simplify(file)
    # file.to_csv(loc[:-15] + 'reduced_house_rental_.3.csv', sep=';', index=False)
