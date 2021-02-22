import pandas as pd
import glob
import os
import shutil
from pathlib import Path


if __name__ == '__main__':
    d = r'\\storage1\carga\modelo dinamico de simulacao\Exits_python\PS2020\POLICIES__2021-02-19T22_39_56.035769'
    nd = f'{d}/avgs'
    os.makedirs(nd) if not os.path.exists(nd) else print('existing directory')
    for f in glob.glob(f"{d}/*/avg/temp_stats.csv"):
        print(f)
        shutil.copy(f, os.path.join(nd, f'{Path(f).parts[-3]}.csv'))
