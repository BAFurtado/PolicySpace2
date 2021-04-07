import os
import json


def read_meta(path1, path2):
    new_path = os.path.join(path1, path2, 'meta.json')
    if os.path.exists(new_path):
        with open(new_path, 'r') as h:
            out = json.load(h)
            a = out[0]['path'].split('\\')[-2].split('.')[-1]
            b = out[0]['params']['PROCESSING_ACPS']
            c = out[0]['params']['POLICY_COEFFICIENT']
            d = out[0]['params']['POLICY_DAYS']
            e = out[0]['params']['POLICY_QUANTILE']
            f = out[0]['params']['TOTAL_DAYS']
            return f'{a}:{b}:COEF:{c}:FAM_DAYS:{d}:QUANTILE:{e}:TOTAL_DAYS:{f}'


if __name__ == '__main__':
    p = r'\\storage1\carga\modelo dinamico de simulacao\Exits_python\PS2020'
    fls = os.listdir(p)
    interest = [f for f in fls if f.startswith('POLICIES')]
    print(f'{len(interest)} different POLICIES runs')
    for each in interest:
        print(read_meta(p, each))



