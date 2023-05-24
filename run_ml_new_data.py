import os
import time
import json

from SecondRunData import generating_random_conf as g
from joblib import Parallel, delayed


def main(i):
    js = {k: scenarios[k][i] for k in scenarios}
    print(js['PROCESSING_ACPS'], ' ', js['PERCENTAGE_ACTUAL_POP'])
    # js = json.dumps(js)
    # with open(f'SecondRunData/json_{i}.json', 'w') as outfile:
    #     outfile.write(js)
    print(f'Run number ________________________{i}')
    c = f"python main.py -c 5 -n 5 -p SecondRunData/json_{i}.json run"
    print()
    # try:
    #     os.system(c)
    # except Exception as e:
    #     print(e)
    #     time.sleep(5)


if __name__ == '__main__':
    # Getting dictionaries
    number_dicts = 50

    scenarios = g.compound(number_dicts)
    for i in range(number_dicts):
        main(i)
    # Parallel(n_jobs=2)(delayed(main)(i) for i in range(number_dicts))
