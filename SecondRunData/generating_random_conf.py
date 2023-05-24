import numpy as np
import pandas as pd
import scipy.stats as stats

from SecondRunData import parameters_restriction as params


def to_dict_from_module(prs):
    return {k: getattr(prs, k) for k in dir(prs) if not k.startswith('_')}


def compound(n):
    # Function will break if n is too small < 1000
    param = to_dict_from_module(params)
    samples = pd.read_csv('SecondRunData/means_stds.csv', sep=';').set_index('parameters')
    data = dict()
    # Either choice or normal
    for p in param:
        # For continuous parameter
        if p in samples.index:
            if param[p]['distribution'] == 'normal':
                lower, upper = param[p]['min'], param[p]['max']
                mu, sigma = samples.loc[p, 'mean'], samples.loc[p, 'std'] * 2
                out = list(stats.truncnorm((lower - mu) / sigma, (upper - mu) / sigma, loc=mu, scale=sigma).rvs(n))
                if 'tp' in param[p]:
                    out = [int(i) for i in out]
                data[p] = out
        else:
            if 'alternatives' in param[p]:
                choices = param[p]['alternatives']
                m = len(choices)
                if 'weights' in param[p]:
                    idx = np.random.choice(m, n, p=param[p]['weights'])
                    choices_vector = [choices[i] for i in idx]
                else:
                    idx = np.random.choice(m, n, p=[1 / m] * m)
                    choices_vector = [choices[i] for i in idx]
                if param['PROCESSING_ACPS'] == "['RIO DE JANEIRO']" or param['PROCESSING_ACPS'] == "['SAO PAULO']":
                    data['PERCENTAGE_ACTUAL_POPULATION'] = np.random.choice([.5, .6, .7])
                data[p] = choices_vector
    return data
