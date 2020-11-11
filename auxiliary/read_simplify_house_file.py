import pandas as pd
import glob
from post_analysis.plot_comparisons import prepare_data, ks_test, plot_qq
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
            plot_qq(s_sales_price['price_util'], real_sales_price, a[-3] + 'sales')
            plot_qq(s_rent_price['price_util'], real_rental_price, a[-3] + 'rent')


if __name__ == '__main__':
    file = r'C:\Users\R1702898\Documents\PolicySpace2\post_analysis/sensible_sales_300.csv'
    real_sales_data = pd.read_csv(file, sep=';', usecols=['price_util'])
    real_sales_data = normalize_data(real_sales_data, 'price_util')
    file = r'C:\Users\R1702898\Documents\PolicySpace2\post_analysis/sensible_rent_300.csv'
    real_rental_data = pd.read_csv(file, sep=';', usecols=['price_util'])
    real_rental_data = normalize_data(real_rental_data, 'price_util')
    d = r'\\STORAGE1\CARGA\MODELO DINAMICO DE SIMULACAO\Exits_python\PS2020'
    _all = get_all_house_data(d)
    run_tests(_all, real_sales_data['price_util'], real_rental_data['price_util'])

