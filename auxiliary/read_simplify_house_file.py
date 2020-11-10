import pandas as pd
import glob
from post_analysis.smirnov_kolmogorov_test import ks_test
from post_analysis.plot_comparisons import prepare_data
from post_analysis.linear_regressions import normalize_data


def simplify(data):
    return data[data[0] == '2019-12-01']


def get_all_house_data(place):
    place = f"{place}/**/**/**/temp_houses.csv"
    return glob.iglob(place, recursive=True)


def run_tests(places, rs, rr):
    for place in places:
        if 'avg' not in place:
            s_sales_price, real_sales_price, s_rent_price, real_rental_price = prepare_data(place, rs, rr)
            a = place.split('\\')
            print(a[-3])
            print(f"Sales {ks_test(s_sales_price['price_util'], real_sales_price)}")
            print(f"Rent {ks_test(s_rent_price['price_util'], real_rental_price)}")


if __name__ == '__main__':
    file = r'C:\Users\R1702898\Documents\PolicySpace2\post_analysis/sensible_sales_300.csv'
    real_sales_data = pd.read_csv(file, sep=';', usecols=['price_util'])
    real_sales_data = normalize_data(real_sales_data, 'price_util')
    file = r'C:\Users\R1702898\Documents\PolicySpace2\post_analysis/sensible_rent_300.csv'
    real_rental_data = pd.read_csv(file, sep=';', usecols=['price_util'])
    real_rental_data = normalize_data(real_rental_data, 'price_util')
    d = r'\\STORAGE1\CARGA\MODELO DINAMICO DE SIMULACAO\Exits_python\PS2020'
    all = get_all_house_data(d)
    run_tests(all, real_sales_data['price_util'], real_rental_data['price_util'])
    # loc = r'\\STORAGE1\CARGA\MODELO DINAMICO DE SIMULACAO\Exits_python\PS2020' \
    #        r'\RENTAL_SHARE__2020-11-03T23_17_41.490300\RENTAL_SHARE=0.3\0\temp_houses.csv'
    # file = pd.read_csv(loc, sep=';', header=None)
    # file = simplify(file)
    # file.to_csv(loc[:-15] + 'reduced_house_rental_.3.csv', sep=';', index=False)
