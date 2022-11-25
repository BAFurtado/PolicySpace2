import os
import time
import json

from SecondRunData import generating_random_conf as g


if __name__ == '__main__':
    # Getting dictionaries
    number_dicts = 10
    scenarios = g.compound(number_dicts)
    for i in range(number_dicts):
        js = {k: scenarios[k][i] for k in scenarios}
        js = json.dumps(js)
        with open('json.json', 'w') as outfile:
            outfile.write(js)
        print(f'Run number ________________________{i}')
        c = f"python main.py -c 5 -n 5 -p json.json run"
        print(c)
        try:
            os.system(c)
        except Exception as e:
            print(e)
            time.sleep(5)



