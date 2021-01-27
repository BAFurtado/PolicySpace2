import os
import fileinput


def replace_in_file(file_path, search_text, new_text):
    with fileinput.input(file_path, inplace=True) as f:
        for line in f:
            new_line = line.replace(search_text, new_text)
            print(new_line, end='')


def sensitivity():
    fpath = 'conf/default/params.py'
    default = 'BRASILIA'
    for each in ['BRASILIA', 'BELO HORIZONTE', 'FORTALEZA', 'CAMPINAS', 'PORTO ALEGRE']:
        search_text = f'PROCESSING_ACPS = [{default}]'
        default = each
        new_text = f'PROCESSING_ACPS = [{default}]'
        replace_in_file(fpath, search_text, new_text)
        os.system(f'python main.py -c 10 -n 20 sensitivity POLICIES')


def main(c):
    os.system(c)


if __name__ == '__main__':
    # General sensitivity
    c1 = 'python main.py -c 10 -n 20 sensitivity ' \
         'PRODUCTIVITY_EXPONENT:.4:.8:5 ' \
         'PRODUCTIVITY_MAGNITUDE_DIVISOR:5:15:5 ' \
         'MUNICIPAL_EFFICIENCY_MANAGEMENT:.00003:.00010:6 ' \
         'LOAN_PAYMENT_TO_PERMANENT_INCOME:.1:.9:7 ' \
         'MAX_LOAN_TO_VALUE:.2:.8:7 ' \
         'PERCENTAGE_ENTERING_ESTATE_MARKET:.003:.008:6 ' \
         'NEIGHBORHOOD_EFFECT:2:4:3 ' \
         'OFFER_SIZE_ON_PRICE:1:4:4' \

    c0 = 'python main.py -c 10 -n 20 sensitivity ' \
         'PERCENT_CONSTRUCTION_FIRMS:.02:.07:5 ' \
         'STICKY_PRICES:.2:.8:7 ' \
         'LABOR_MARKET:.3:.9:7 ' \
         'CONSTRUCTION_ACC_CASH_FLOW:1:37:4 ' \
         'PRIVATE_TRANSIT_COST:0:.5:6 ' \
         'INTEREST ' \
         'MARKUP:.01:.2:4' \

    c5 = 'python main.py -c 10 -n 20 sensitivity ' \
         'SIZE_MARKET:1:17:5 ' \
         'PCT_DISTANCE_HIRING:0:1:5 ' \
         'WAGE_IGNORE_UNEMPLOYMENT ' \
         'HIRING_SAMPLE_SIZE:5:25:5 ' \
         'PUBLIC_TRANSIT_COST:0:.5:6 ' \
         'MARRIAGE_CHECK_PROBABILITY:.02:.05:7 ' \
         'PERCENTAGE_ACTUAL_POP:.005:.03:6'

    c2 = 'python main.py -c 10 -n 20 sensitivity ' \
         'TAX_CONSUMPTION:.27:.33:7 ' \
         'TAX_LABOR:.12:.18:7 ' \
         'TAX_ESTATE_TRANSACTION:.001:.007:7 ' \
         'TAX_FIRM:.12:.18:7 ' \
         'LOT-COST:.1:.3:5 ' \
         'CAPPED_TOP_VALUE:1:1.5:6 ' \
         'CAPPED_LOW_VALUE:.5:1:6 ' \
         'TAX_PROPERTY:.001:.007:7'

    c3 = 'python main.py -c 10 -n 5 acps' \

    c4 = 'python main.py -c 10 -n 20 distributions' \

    try:
        sensitivity()
    except:
        pass

    for each in [c0, c1, c2, c3, c4, c5]:
        try:
            main(each)
        except:
            pass
