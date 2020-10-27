import pandas as pd


def simplify(data):
    return data[data[0] == '2019-12-01']


if __name__ == '__main__':
    loc = r'\\STORAGE1\CARGA\MODELO DINAMICO DE SIMULACAO\Exits_python\PS2020' \
           r'\NEIGHBORHOOD_EFFECT__2020-10-27T18_37_25.808167\NEIGHBORHOOD_EFFECT=3.0\0\temp_houses.csv'
    file = pd.read_csv(loc, sep=';', header=None)
    file = simplify(file)
    file.to_csv(loc[:-15] + 'reduced_house.csv', sep=';', index=False)
