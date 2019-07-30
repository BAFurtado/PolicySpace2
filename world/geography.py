import pandas as pd


ACP_CODES = pd.read_csv('input/ACPs_BR.csv', sep=';', header=0, decimal=',')
ACPS_MUN_CODES = pd.read_csv('input/ACPs_MUN_CODES.csv', sep=';', header=0, decimal=',')
STATES_CODES = pd.read_csv('input/STATES_ID_NUM.csv', sep=';', header=0, decimal=',')


def state_string(state, states_codes):
    state_id = states_codes.loc[states_codes['codmun'] == state]['nummun']
    return str(state_id.iloc[0])


def process_acps(acps):
    acps_codes = []
    states_on_process = []
    for item in acps:
        acps_codes.extend(ACP_CODES[ACP_CODES['ACPs'] == item]['ID'].values)
        states_on_process.extend(ACP_CODES[ACP_CODES['ACPs'] == item]['state_code'].values)
    acps_codes = sorted(map(str, acps_codes))
    acps = sorted(map(str, acps))
    return acps_codes, acps, states_on_process


class Geography:
    """Manages which ACPs/states/municipalities are used for the simulation"""
    def __init__(self, params):
        # Processing the chosen ACPs
        self.processing_acps_codes, self.processing_acps, self.states_on_process = process_acps(params['PROCESSING_ACPS'])

        # DATA INPUT: ########################################################################################################
        # ACP list to control the selection of municipalities
        mun_codes = []

        # Selecting the municipalities' codes from list
        for acp in self.processing_acps:
            mun_codes += list(ACPS_MUN_CODES.loc[ACPS_MUN_CODES['ACPs'] == acp, ]['cod_mun'])

        self.mun_codes = list(set(mun_codes))

        # Creating a list of municipalities and ACPs
        ACPs_on_process = ACPS_MUN_CODES.loc[ACPS_MUN_CODES['ACPs'] == self.processing_acps[0]]

        if len(self.processing_acps) > 1:
            list_acps_temp = self.processing_acps[1:]
            for acp_dat in list_acps_temp:
                ACPs_on_process = pd.concat([ACPs_on_process, ACPS_MUN_CODES.loc[ACPS_MUN_CODES['ACPs'] == acp_dat]], axis=0)

        self.list_of_acps = [i for i in ACPs_on_process['ACPs'].unique()]

        # List of municipality names
        mun_list = pd.read_csv('input/names_and_codes_municipalities.csv', header=0, sep=';', decimal=',')

        # Selecting the names for each municipality code
        self.LIST_NAMES_MUN = pd.DataFrame(columns=['cod_name', 'cod_mun', 'state'])
        for mun in self.mun_codes:
            self.LIST_NAMES_MUN = pd.concat([self.LIST_NAMES_MUN, mun_list.loc[mun_list['cod_mun'] == int(mun)]], axis=0)
