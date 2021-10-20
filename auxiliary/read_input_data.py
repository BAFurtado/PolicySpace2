import os
import pandas as pd
import geopandas as gpd


files = ['prop_urban_2000_2010.csv',
         'pop_women_2010.csv',
         'pop_men_2010.csv',
         'idhm_2000_2010.csv',
         'estimativas_pop.csv',
         'interest_real.csv',
         'num_people_age_gender_AP_2010.csv',
         'qualification_APs_2010.csv',
         'firms_by_APs2010_t0_full.csv',
         'firms_by_APs2010_t1_full.csv',
         'average_num_members_families_2010.csv'
         ]


def read_data(path, sep=';'):
    return pd.read_csv(path, sep=sep)


def read_mun(data, municipalities, col='cod_mun'):
    return data[data[col].isin(municipalities)]


def read_data_aps(data, municipalities, col='AP'):
    return data[data[col].astype(str).str[:7].isin([str(m) for m in municipalities])]


def descriptive_stats(data, col):
    print(col)
    print('max', data[col].max())
    print('min', data[col].min())
    print('mean', data[col].mean())
    print('std', data[col].std())
    print('obs', len(data[col]))
    print('\n')


if __name__ == '__main__':
    p = 'input'
    acp = 'BRASILIA'
    mun = pd.read_csv('input/ACPs_MUN_CODES.csv', sep=';')
    mun = mun[mun['ACPs'] == acp].cod_mun.to_list()

    f0 = read_data(os.path.join(p, files[0]))
    f0 = read_mun(f0, mun)
    descriptive_stats(f0, '2010')

    f1 = read_data(os.path.join(p, files[1]))
    f1 = read_mun(f1, mun)
    f1c = f1.drop('cod_mun', axis=1)

    f2 = read_data(os.path.join(p, files[2]))
    f2 = read_mun(f2, mun)
    f2c = f2.drop('cod_mun', axis=1)

    f3 = read_data(os.path.join(p, files[3]))
    f3 = read_mun(f3, [2010], 'year')
    f3 = read_mun(f3, mun)
    descriptive_stats(f3, 'idhm')

    f4 = read_data(os.path.join(p, files[4]), ',')
    f4 = read_mun(f4, mun, 'mun_code')
    f4c = f4.drop('mun_code', axis=1)

    f5 = read_data(os.path.join(p, files[5]), ';')
    f5d = f5.loc[:240]
    descriptive_stats(f5d, 'mortgage')

    f6 = read_data(os.path.join(p, files[6]), ';')
    f6 = read_mun(f6, mun, 'AREAP')
    descriptive_stats(f6, 'num_people')

    f7 = read_data(os.path.join(p, files[7]), ',')
    f7 = read_data_aps(f7, mun, 'code')
    f7c = f7.drop('code', axis=1)

    f8 = read_data(os.path.join(p, files[8]))
    f9 = read_data(os.path.join(p, files[9]))

    f8 = read_data_aps(f8, mun, 'AP')
    f9 = read_data_aps(f9, mun, 'AP')
    descriptive_stats(f8, 'num_firms')
    descriptive_stats(f9, 'num_firms')

    f10 = read_data(os.path.join(p, files[10]), ',')
    f10 = read_data_aps(f10, mun, 'AREAP')
    descriptive_stats(f10, 'avg_num_people')

    p1 = 'shapes/2010/areas/DF.shp'
    geo_df = gpd.read_file(os.path.join(p, p1))
    p2 = 'shapes/2010/areas/GO.shp'
    geo_go = gpd.read_file(os.path.join(p, p2))
    geo_go = read_data_aps(geo_go, mun, 'mun_code')

    # STATE-LEVEL, GENDER
    years = ['age', '2021', '2022', '2023', '2024', '2025', '2026', '2027', '2028', '2029', '2030']
    out = pd.DataFrame()
    for state in ['DF', 'GO']:
        p3 = f'fertility/fertility_{state}.csv'
        t = pd.read_csv(os.path.join(p, p3), ';')
        t = t.drop(years, axis=1)
        out = pd.concat([out, t], axis=0)

    # Mortality
    years = ['age', '2021', '2022', '2023', '2024', '2025', '2026', '2027', '2028', '2029', '2030']
    out = pd.DataFrame()
    for state in ['DF', 'GO']:
        for sex in ['men', 'women']:
            p3 = f'mortality/mortality_{sex}_{state}.csv'
            t = pd.read_csv(os.path.join(p, p3), ';')
            t = t.drop(years, axis=1)
            out = pd.concat([out, t], axis=0)

    # FPM
    out = pd.DataFrame()
    for state in ['DF', 'GO']:
        p3 = f'fpm/{state}.csv'
        t = pd.read_csv(os.path.join(p, p3), ',')
        t = read_mun(t, mun, 'cod')
        out = pd.concat([out, t], axis=0)

