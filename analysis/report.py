"""     File used only for descriptive statistics
"""

import os
import conf
import pandas as pd

# List of municipalities' names
mun_list = pd.read_csv('input/names_and_codes_municipalities.csv', header=0, sep=';', decimal=',')


def stats(filename):

    dat = pd.read_csv(filename,  sep=';', decimal='.', header=None)
    dat.columns = ['month', 'region_id', 'gender', 'long', 'lat', 'id', 'age', 'qualification', 'firm_id',
                   'family_id', 'money', 'utility', 'distance']

    # Variable to pass percentage value of population into plot's title
    percentage_of_pop = str(open('FilesforControl/percentage_of_population.txt').read().replace('\n', ''))
    title_pop_val = float(percentage_of_pop) * 100

    # Formatting the list of values for X axis
    list_of_years_division = list(range(dat['month'].min(), int(dat['month'].max()), 12)) + [dat['month'].max() + 1]
    list_of_years = [int(i/12) for i in list_of_years_division]

    dat_name = dat['region_id'].loc[dat['month'] == 0]
    dat_name = list(dat_name.unique())

    # Selecting the names for each municipality code
    LIST_NAMES_MUN = pd.DataFrame(columns=['cod_name', 'cod_mun', 'state'])
    for mun in dat_name:
        LIST_NAMES_MUN = pd.concat([LIST_NAMES_MUN, mun_list.loc[mun_list['cod_mun'] == int(mun)]], axis=0)
    names_mun = list(LIST_NAMES_MUN['cod_name'])

    # By month and municipality together
    dat_month_mun = dat.groupby(['month', 'region_id'], as_index=False)

    # Plotting AGE by Municipality and region
    temp = pd.DataFrame(dat_month_mun['age'].median())
    temp = temp.pivot(index='month', columns='region_id', values='age')
    plot_data = temp.plot(title='Evolution of AGE by Municipality, monthly\nAgents : %s' %
                                       title_pop_val + '% of Population')
    plot_data.set_xlabel('Years')
    plot_data.set_ylabel('Median of age (in years)')
    plot_data.legend(loc='best', ncol=4, fancybox=True, shadow=True, labels=names_mun)
    plot_data.set_xticks(list_of_years_division)
    plot_data.set_xticklabels(list_of_years)
    fig = plot_data.get_figure()
    fig.set_size_inches(15, 10)
    fig.savefig(os.path.join(conf.RUN['OUTPUT_DATA_PATH'],
                             'temp_descriptive_stats_age_month_municipality_evolutions.png'), dpi=300)

    # Plotting QUALIFICATION by Municipality and region
    temp = pd.DataFrame(dat_month_mun['qualification'].mean())
    temp = temp.pivot(index='month', columns='region_id', values='qualification')
    plot_data = temp.plot(title='Evolution of QUALIFICATION by Municipality, monthly\nAgents : %s' %
                                       title_pop_val + '% of Population')
    plot_data.set_xlabel('Years')
    plot_data.set_ylabel('Average of QUALIFICATION (in years)')
    plot_data.legend(loc='best', ncol=4, fancybox=True, shadow=True, labels=names_mun)
    plot_data.set_xticks(list_of_years_division)
    plot_data.set_xticklabels(list_of_years)
    fig = plot_data.get_figure()
    fig.set_size_inches(15, 10)
    fig.savefig(os.path.join(conf.RUN['OUTPUT_DATA_PATH'],
                             'temp_descriptive_stats_qualification_month_municipality_evolution.png'), dpi=200)

    # plotting QUALIFICATION by Municipality and region by month and municipality together
    agent_employment_sequence = pd.DataFrame(columns=['agent','gender', 'firm_id','duration'])
    list_of_ids = list(dat['id'].unique())
    for agent in list_of_ids:
        temp = dat.loc[dat['id'] == agent]
        agent_firm_situation = temp['firm_id'].tolist()
        positions_change = [i for i, (x, y) in enumerate(zip(agent_firm_situation[:-1], agent_firm_situation[1:]))
                            if x != y]
        if len(positions_change) == 0:
            agent_result = pd.concat([pd.DataFrame([agent], columns=['agent']),
                                      pd.DataFrame(temp['gender'].unique(), columns=['gender']),
                                      pd.DataFrame(temp['firm_id'].unique(), columns=['firm_id']),
                                      pd.DataFrame([temp['firm_id'].count()], columns=['duration'])], axis=1)
            agent_employment_sequence = pd.concat([agent_employment_sequence, agent_result], axis=0)
        else:
            positions_change = positions_change + [positions_change[-1] + 1]
            agent_firm_location = [agent_firm_situation[i] for i in positions_change]
            agent_id = temp['id'].unique().tolist() * len(positions_change)
            agent_gender = temp['gender'].unique().tolist() * len(positions_change)
            initial = [int(i)+1 for i in positions_change]
            final = initial.copy()
            initial.pop(len(initial)-1, )

            initial = [0] + initial
            final.pop(len(final)-1,)
            final += [temp['month'].max() + 1]
            duration_in_the_job = []
            for pos in range(len(final)):
                duration_in_the_job.append(temp['firm_id'].iloc[initial[pos]:final[pos]].count())

            agent_result = pd.concat([pd.DataFrame(agent_id, columns=['agent']),
                                      pd.DataFrame(agent_gender, columns=['gender']),
                                      pd.DataFrame(agent_firm_location, columns=['firm_id']),
                                      pd.DataFrame(duration_in_the_job, columns=['duration'])], axis=1)
            agent_employment_sequence = pd.concat([agent_employment_sequence, agent_result], axis=0)
    agent_employment_sequence.to_csv(os.path.join(conf.RUN['OUTPUT_DATA_PATH'],
                                                  'temp_descriptive_stats_agents_locations_job.csv'),
                                     sep=';', decimal='.',
                                     header=True, index=None, na_rep='NaN')
