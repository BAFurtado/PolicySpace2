import datetime


# MODEL PARAMETERS
# FIRMS
# Production function, labour with decaying exponent, Alpha for K. [0, 1]
ALPHA = .24
# By how much percentage to increase prices
MARKUP = 0.15
# Frequency firms change prices. Probability > than parameter
STICKY_PRICES = .8
# Number of firms consulted before consumption
SIZE_MARKET = 10

# Frequency firms enters in the market
# TODO: Check if this frequency (95% of the time is adequate)
LABOR_MARKET = 0.95

# Percentage of employees firms hire by distance
PCT_DISTANCE_HIRING = .17
# Ignore unemployment in wage base calculation
WAGE_IGNORE_UNEMPLOYMENT = False
# Candidate sample size for the labor market
HIRING_SAMPLE_SIZE = 20

# Percentage of households pursuing new location
PERCENTAGE_CHECK_NEW_LOCATION = 0.005

# TAXES
TAX_CONSUMPTION = .3
TAX_LABOR = .15
TAX_ESTATE_TRANSACTION = .005
TAX_FIRM = .15
TAX_PROPERTY = .005

# LOANS
MAX_LOAN_AGE = 80
MAX_LOAN_REPAYMENT_PERCENT_INCOME = 0.3
MAX_LOAN_BANK_PERCENT = 0.7

# GOVERNMENT
# MONTHLY Real interest rate of the economy (SELIC minus INFLATION) for the Brazilian case
# REAL INTEREST RATE OF 1.5% YEARLY TRANSFORMED INTO MONTHS' VALUES: = ((1.05-.035)**(1/12)) - 1 = 0.0012415
INTEREST_RATE = .0012415
# ALTERNATIVE OF DISTRIBUTION OF TAXES COLLECTED. REPLICATING THE NOTION OF A COMMON POOL OF RESOURCES ################
# Alternative0 is True, municipalities are just normal as INPUT
# Alternative0 is False, municipalities are all together
ALTERNATIVE0 = True
# Apply FPM distribution as current legislation assign TRUE
# Distribute locally, assign FALSE
FPM_DISTRIBUTION = True
# alternative0  TRUE,           TRUE,       FALSE,  FALSE
# fpm           TRUE,           FALSE,      TRUE,   FALSE
# Results     fpm + eq. + loc,  locally,  fpm + eq,   eq

# CONSTRUCTION
LICENSES_PER_REGION = 50
NEW_LICENSE_RATE = 10
PERCENT_CONSTRUCTION_FIRMS = 0.05
# Months that construction firm will divide its income into monthly revenue installments.
# Although prices are accounted for at once.
CONSTRUCTION_ACC_CASH_FLOW = 36
# Cost of lot in PERCENTAGE of construction
LOT_COST = .1

# Families run parameters
MEMBERS_PER_FAMILY = 2.5                             # (on average)
HOUSE_VACANCY = .11                                   # percentage of vacant houses

RENTAL_SHARE = 0.4
INITIAL_RENTAL_PRICE = .0029
# Definition to simplify population by group age groups(TRUE) or including all ages (FALSE)
SIMPLIFY_POP_EVOLUTION = True
# Defines the superior limit of age groups, the first value is always ZERO and is omitted from the list.
LIST_NEW_AGE_GROUPS = [6, 12, 17, 25, 35, 45, 65, 100]
MARRIAGE_CHECK_PROBABILITY = .034

# Consumption_equal: ratio of consumption tax distributed at state level (equal)
# Fpm: ratio of 'labor' and 'firm' taxes distributed per the fpm ruling
TAXES_STRUCTURE = {'consumption_equal': .1875, 'fpm': .235}

# GENERAL CALIBRATION PARAMETERS
# Order of magnitude parameter of input into municipality investment
TREASURE_INTO_SERVICES = 5e-07
# Order of magnitude correction of production. Production divided by parameter
PRODUCTION_MAGNITUDE = 1

WAGE_TO_CAR_OWNERSHIP_QUANTILES = [
    0.1174,
    0.1429,
    0.2303,
    0.2883,
    0.3395,
    0.4667,
    0.5554,
    0.6508,
    0.7779,
    0.9135,
]
PRIVATE_TRANSIT_COST = 0.5
PUBLIC_TRANSIT_COST = 0.2

# selecting the ACPs (Population Concentration Areas)
# ACPs and their STATES - ALL ACPs written in UPPER CASE and without  ACCENT
# STATE    -       ACPs
# ------------------------
# "AM"     -      "MANAUS"
# "PA"     -      "BELEM"
# "AP"     -      "MACAPA"
# "MA"     -      "SAO LUIS", "TERESINA"
# "PI"     -      "TERESINA"
# "CE"     -      "FORTALEZA", "CRAJUBAR" - CRAJUBAR refers to JUAZEIRO DO NORTE - CRATO - BARBALHA
# "RN"     -      "NATAL"
# "PB"     -      "JOAO PESSOA", "CAMPINA GRANDE"
# "PE"     -      "RECIFE", "PETROLINA - JUAZEIRO"
# "AL"     -      "MACEIO"
# "SE"     -      "ARACAJU"
# "BA"     -      "SALVADOR", "FEIRA DE SANTANA", "ILHEUS - ITABUNA", "PETROLINA - JUAZEIRO"
# "MG"     -      "BELO HORIZONTE", "JUIZ DE FORA", "IPATINGA", "UBERLANDIA"
# "ES"     -      "VITORIA"
# "RJ"     -      "VOLTA REDONDA - BARRA MANSA", "RIO DE JANEIRO", "CAMPOS DOS GOYTACAZES"
# "SP"     -      "SAO PAULO", "CAMPINAS", "SOROCABA", "SAO JOSE DO RIO PRETO", "SANTOS", "JUNDIAI",
#                 "SAO JOSE DOS CAMPOS", "RIBEIRAO PRETO"
# "PR"     -      "CURITIBA" "LONDRINA", "MARINGA"
# "SC"     -      "JOINVILLE", "FLORIANOPOLIS"
# "RS"     -      "PORTO ALEGRE", "NOVO HAMBURGO - SAO LEOPOLDO", "CAXIAS DO SUL", "PELOTAS - RIO GRANDE"
# "MS"     -      "CAMPO GRANDE"
# "MT"     -      "CUIABA"
# "GO"     -      "GOIANIA", "BRASILIA"
# "DF"     -      "BRASILIA"

# Percentage of actual population to run the simulation
# Minimum value to run depends on the size of municipality 0,001 is recommended minimum
PERCENTAGE_ACTUAL_POP = 0.002

# Write exactly like the list
PROCESSING_ACPS = ['GOIANIA']

# Selecting the starting year to build the Agents, can be: 1991, 2000 or 2010
STARTING_DAY = datetime.date(2000, 1, 1)

# Maximum running time (restrained by official data) is 30 years,
TOTAL_DAYS = (datetime.date(2020, 1, 1) - STARTING_DAY).days


