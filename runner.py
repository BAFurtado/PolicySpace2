import os
import fileinput
import datetime


def replace_in_file(file_path, search_text, new_text):
    with fileinput.input(file_path, inplace = True) as f:
        for line in f:
            new_line = line.replace(search_text, new_text)
            print(new_line, end='')


def sensitivity(path='conf/default/params.py',
                alt=None,
                default="['BRASILIA']",
                txt='PROCESSING_ACPS = ',
                c='python main.py -c 8 -n 20 sensitivity POLICIES'):
    if alt is None:
        alt = ["['BELO HORIZONTE']", "['FORTALEZA']", "['CAMPINAS']", "['PORTO ALEGRE']"]
    for each in alt:
        search_text = f"{txt}{default}"
        new_text = f'{txt}{each}'
        replace_in_file(path, search_text, new_text)
        os.system(c)
        search_text = f"{txt}{default}"
        new_text = f'{txt}{each}'
        replace_in_file(path, new_text, search_text)


def main(c):
    os.system(c)


if __name__ == '__main__':
    # General sensitivity
    c0 = 'python main.py -c 10 -n 20 sensitivity ' \
         'PRODUCTIVITY_EXPONENT:0:.9:7 ' \
         'PRODUCTIVITY_MAGNITUDE_DIVISOR:1:36:7 ' \
         'MUNICIPAL_EFFICIENCY_MANAGEMENT:.00001:.0002:7 ' \
         'LOAN_PAYMENT_TO_PERMANENT_INCOME:0.1:.9:7 ' \
         'MAX_LOAN_TO_VALUE:.1:.9:7 ' \
         'PERCENTAGE_ENTERING_ESTATE_MARKET:.001:.05:7 ' \
         'NEIGHBORHOOD_EFFECT:0:5:6 ' \
         'OFFER_SIZE_ON_PRICE:0:4:5' \

    c1 = 'python main.py -c 10 -n 20 sensitivity ' \
         'PERCENT_CONSTRUCTION_FIRMS:.02:.07:6 ' \
         'STICKY_PRICES:.1:.9:7 ' \
         'LABOR_MARKET:.1:.9:7 ' \
         'CONSTRUCTION_ACC_CASH_FLOW:1:36:4 ' \
         'INTEREST ' \
         'MARKUP:0:.3:4' \

    c2 = 'python main.py -c 10 -n 20 sensitivity ' \
         'SIZE_MARKET:1:20:5 ' \
         'PCT_DISTANCE_HIRING:0:1:7 ' \
         'WAGE_IGNORE_UNEMPLOYMENT ' \
         'HIRING_SAMPLE_SIZE:1:30:6 ' \
         'PUBLIC_TRANSIT_COST:0:.5:7 ' \
         'PRIVATE_TRANSIT_COST:0:.5:7 ' \
         'MARRIAGE_CHECK_PROBABILITY:.02:.05:7 ' \
         'PERCENTAGE_ACTUAL_POP:.005:.03:6'

    c3 = 'python main.py -c 8 -n 20 sensitivity ' \
         'TAX_CONSUMPTION:.27:.33:7 ' \
         'TAX_LABOR:.12:.18:7 ' \
         'TAX_ESTATE_TRANSACTION:.001:.007:7 ' \
         'TAX_FIRM:.12:.18:7 ' \
         'CAPPED_TOP_VALUE:1:1.5:6 ' \
         'CAPPED_LOW_VALUE:.5:1:6 ' \
         'TAX_PROPERTY:.001:.007:7'

    x = 'python main.py -c 10 -n 20 sensitivity LOT_COST:.1:.3:5'

    c4 = 'python main.py -c 8 -n 5 acps' \

    c5 = 'python main.py -c 8 -n 20 distributions' \

    c6 = 'python main.py -c 8 -n 2 sensitivity POLICIES' \

    c7 = f'python main.py -c 1 -n 1 run'

    main(c7)

    # for each in [c6, c0, c1, c2]:
    #     main(each)
    #
    # sensitivity()
    # sensitivity(alt=['180', '360'], default='360', txt='POLICY_DAYS = ')
    # sensitivity(alt=['.1', '.3'], default='.2', txt='POLICY_QUANTILE = ')
    #

    c8 = f'python main.py -c 8 -n 20 sensitivity "PROCESSING_ACPS-BRASILIA-CAMPINAS-FORTALEZA-BELO HORIZONTE-PORTO ALEGRE"'
    #
    # main(c7)
    #
    # for each in [c6, c0, c1, c2]:
    #     main(each)

    # sensitivity()
    # sensitivity(alt=['180', '360'], default='360', txt='POLICY_DAYS = ')
    # sensitivity(alt=['.1', '.3'], default='.2', txt='POLICY_QUANTILE = ')
    # sensitivity(alt=['.1', '.3'], default='.2', txt='POLICY_COEFFICIENT = ')
    # sensitivity(alt=['7200'], default='3652', txt='TOTAL_DAYS = ')
    # Manually 2000-2030 e 2000-2020

    # for each in [c3, c4, c5]:
    #     main(each)
    #
    # sensitivity(alt=['datetime.date(2000, 1, 1)'], txt='STARTING_DAY = ',
    #             c=f'python main.py -c 10 -n 20 run')
    # sensitivity(alt=['(datetime.date(2030, 1, 1) - STARTING_DAY).days'], txt='TOTAL_DAYS = ',
    #             c=f'python main.py -c 10 -n 20 run')

