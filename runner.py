import os
import fileinput


def replace_in_file(file_path, search_text, new_text):
    with fileinput.input(file_path, inplace=True) as f:
        for line in f:
            new_line = line.replace(search_text, new_text)
            print(new_line, end='')


def sensitivity(p='conf/default/params.py',
                alt=None,
                txt='PROCESSING_ACPS = ',
                c='python main.py -c 8 -n 20 sensitivity POLICIES'):
    if alt is None:
        alt = ["['BRASILIA']", "['BELO HORIZONTE']", "['FORTALEZA']", "['CAMPINAS']", "['PORTO ALEGRE']"]
    fpath = p
    for each in alt:
        search_text = f"{txt}"
        new_text = f'{txt}{each}'
        replace_in_file(fpath, search_text, new_text)
        os.system(c)


def main(c):
    os.system(c)


if __name__ == '__main__':
    # General sensitivity
    c0 = 'python main.py -c 10 -n 20 sensitivity ' \
         'PRODUCTIVITY_EXPONENT:0:1:7 ' \
         'PRODUCTIVITY_MAGNITUDE_DIVISOR:1:36:7 ' \
         'MUNICIPAL_EFFICIENCY_MANAGEMENT:.00001:.00010:7 ' \
         'LOAN_PAYMENT_TO_PERMANENT_INCOME:0:1:7 ' \
         'MAX_LOAN_TO_VALUE:.1:.9:7 ' \
         'PERCENTAGE_ENTERING_ESTATE_MARKET:.001:.05:7 ' \
         'NEIGHBORHOOD_EFFECT:0:5:6 ' \
         'OFFER_SIZE_ON_PRICE:0:4:5' \

    c1 = 'python main.py -c 10 -n 20 sensitivity ' \
         'PERCENT_CONSTRUCTION_FIRMS:.02:.07:6 ' \
         'STICKY_PRICES:.1:.9:7 ' \
         'LABOR_MARKET:.1:.9:7 ' \
         'CONSTRUCTION_ACC_CASH_FLOW:1:37:4 ' \
         'PRIVATE_TRANSIT_COST:0:.5:7 ' \
         'INTEREST ' \
         'MARKUP:0:.3:4' \

    c2 = 'python main.py -c 10 -n 20 sensitivity ' \
         'SIZE_MARKET:1:20:5 ' \
         'PCT_DISTANCE_HIRING:0:1:7 ' \
         'WAGE_IGNORE_UNEMPLOYMENT ' \
         'HIRING_SAMPLE_SIZE:1:100:7 ' \
         'PUBLIC_TRANSIT_COST:0:.5:7 ' \
         'PRIVATE_TRANSIT_COST:0:.5:7 ' \
         'MARRIAGE_CHECK_PROBABILITY:.02:.05:7 ' \
         'PERCENTAGE_ACTUAL_POP:.005:.03:6'

    c3 = 'python main.py -c 10 -n 20 sensitivity ' \
         'TAX_CONSUMPTION:.27:.33:7 ' \
         'TAX_LABOR:.12:.18:7 ' \
         'TAX_ESTATE_TRANSACTION:.001:.007:7 ' \
         'TAX_FIRM:.12:.18:7 ' \
         'LOT-COST:.1:.3:5 ' \
         'CAPPED_TOP_VALUE:1:1.5:6 ' \
         'CAPPED_LOW_VALUE:.5:1:6 ' \
         'TAX_PROPERTY:.001:.007:7'

    c4 = 'python main.py -c 6 -n 4 acps' \

    c5 = 'python main.py -c 10 -n 20 distributions' \

    c6 = 'python main.py -c 10 -n 20 sensitivity POLICIES'

    c7 = 'python main.py -c 10 -n 20 run'

    main(c7)

    for each in [c6, c0, c1, c2]:
        try:
            main(each)
        except:
            pass

    try:
        sensitivity()
    except:
        pass

    sensitivity(alt=['180', '360'], txt='POLICY_MONTHS = ')
    sensitivity(alt=['.1', '.5'], txt='POLICY_QUANTILE = ')

    for each in [c3, c4, c5]:
        try:
            main(each)
        except:
            pass

    try:
        sensitivity(p='conf/default/run.py', txt='SAVE_DATA = ', alt=["['agents', 'house', 'family']"],
                    c=f'python main.py -c 10 -n 20 run')
    except:
        pass

    try:
        sensitivity(alt=['datetime.date(2000, 1, 1)'], txt='STARTING_DAY = ',
                    c=f'python main.py -c 10 -n 20 run')
    except:
        pass

    try:
        sensitivity(alt=['(datetime.date(2030, 1, 1) - STARTING_DAY).days'], txt='TOTAL_DAYS = ',
                    c=f'python main.py -c 10 -n 20 run')
    except:
        pass
