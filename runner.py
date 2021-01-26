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
        search_text = f'PROCESSING_ACPS=[{default}]'
        default = each
        new_text = f'PROCESSING_ACPS=[{default}]'
        replace_in_file(fpath, search_text, new_text)
        os.system(f'python main.py -c 10 -n 2 sensitivity POLICIES')


def main(c):
    os.system(c)


if __name__ == '__main__':
    # General sensitivity
    c1 = 'python main.py -c 10 -n 4 sensitivity ' \
         'PRODUCTIVITY_EXPONENT:.5:.7:6 ' \
         'PRODUCTIVITY_MAGNITUDE_DIVISOR:8:12:5 ' \
         'MUNICIPAL_EFFICIENCY_MANAGEMENT:.00004:.00009:6 ' \
         'LOAN_PAYMENT_TO_PERMANENT_INCOME:.1:.9:7 ' \
         'MAX_LOAN_TO_VALUE:.3:.7:5 ' \
         'PERCENTAGE_CHECK_NEW_LOCATION:.002:.005:7 ' \
         'NEIGHBORHOOD_EFFECT:2:3:2 ' \
         'PERCENT_CONSTRUCTION_FIRMS:.02:.05:7 ' \
         'STICKY_PRICES:.3:.7:4 ' \
         'CONSTRUCTION_ACC_CASH_FLOW:1:37:4 ' \
         'PRIVATE_TRANSIT_COST:0:.5:6 ' \
         'PUBLIC_TRANSIT_COST:0:.5:6'
    # main(c1)
    sensitivity()
