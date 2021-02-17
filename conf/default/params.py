import datetime


# MODEL PARAMETERS
# FIRMS
# Production function, labour with decaying exponent, Alpha for K. [0, 1]
PRODUCTIVITY_EXPONENT = .6
# Order of magnitude correction of production. Production divided by parameter
PRODUCTIVITY_MAGNITUDE_DIVISOR = 10
# GENERAL CALIBRATION PARAMETERS
# Order of magnitude parameter of input into municipality investment
MUNICIPAL_EFFICIENCY_MANAGEMENT = .00007
# INTEREST. Choose either: 'nominal', 'real' or 'fixed'. Default 'real'
INTEREST = 'real'

# By how much percentage to increase prices
MARKUP = 0.15
# Frequency firms change prices. Probability > than parameter
STICKY_PRICES = .7
# Number of firms consulted before consumption
SIZE_MARKET = 5

# Frequency firms enter the market
LABOR_MARKET = 0.75

# Percentage of employees firms hired by distance
PCT_DISTANCE_HIRING = .3
# Ignore unemployment in wage base calculation
WAGE_IGNORE_UNEMPLOYMENT = False
# Candidate sample size for the labor market
HIRING_SAMPLE_SIZE = 20

# TAXES
TAX_CONSUMPTION = .3
TAX_LABOR = .15
TAX_ESTATE_TRANSACTION = .005
TAX_FIRM = .15
TAX_PROPERTY = .005

# GOVERNMENT
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

# POVERTY POLICIES. If POLICY_COEFFICIENT = 0, do nothing.
POLICY_COEFFICIENT = 0.2
# Policies alternatives may include: 'buy', 'rent' or 'wage' or 'no_policy'. For no policy set to empty strings ''
# POLICY_COEFFICIENT needs to be > 0.
POLICIES = 'wage'
POLICY_MONTHS = 180
# HOUSING AND REAL ESTATE MARKET
# LOANS
# Maximum age of borrower at the end of the contract
MAX_LOAN_AGE = 75
# Used to calculate monthly payment for the families, thus limiting maximum loan by number of months and age
LOAN_PAYMENT_TO_PERMANENT_INCOME = .5
# Refers to the maximum loan monthly payment to total wealth
# MAX_LOAN_PAYMENT_TO_WEALTH = .4
# Refers to the maximum rate of the loan on the value of the estate
MAX_LOAN_TO_VALUE = .3

# This parameter refers to the total amount of resources available at the bank.
MAX_LOAN_BANK_PERCENT = .7

CAPPED_TOP_VALUE = 1.3
CAPPED_LOW_VALUE = .7

# Influence of vacancy size on house prices
# It can be True or 1 or if construction companies consider vacancy strongly it might be 2 [1 - (vacancy * VALUE)]
OFFER_SIZE_ON_PRICE = 2
# TOO LONG ON THE MARKET:
# value = (1 - MAX_OFFER_DISCOUNT) * e ** (ON_MARKET_DECAY_FACTOR * MONTHS ON MARKET) + MAX_OFFER_DISCOUNT
# AS SUCH (-.02) DECAY OF 1% FIRST MONTH, 10% FIRST YEAR. SET TO 0 TO ELIMINATE EFFECT
ON_MARKET_DECAY_FACTOR = -.01
# LOWER BOUND, THAT IS, AT LEAST 50% PERCENT OF VALUE WILL REMAIN AT END OF PERIOD, IF PARAMETER IS .5
MAX_OFFER_DISCOUNT = .6
# Percentage of households pursuing new location
PERCENTAGE_ENTERING_ESTATE_MARKET = 0.0045
NEIGHBORHOOD_EFFECT = 3

# RENTAL
RENTAL_SHARE = 0.3
INITIAL_RENTAL_PRICE = .0028

# CONSTRUCTION
# LICENSES ARE URBANIZED LOTS AVAILABLE FOR CONSTRUCTION PER NEIGHBORHOOD PER MONTH.
# If random, it will vary between 1 and 0, otherwise an integer
T_LICENSES_PER_REGION = 'random'
PERCENT_CONSTRUCTION_FIRMS = 0.03
# Months that construction firm will divide its income into monthly revenue installments.
# Although prices are accounted for at once.
CONSTRUCTION_ACC_CASH_FLOW = 24
# Cost of lot in PERCENTAGE of construction
LOT_COST = .15

# Families run parameters (on average) for year 2000, or no information. 2010 uses APs average data
MEMBERS_PER_FAMILY = 2.5
# Initial percentage of vacant houses
HOUSE_VACANCY = .1

# Definition to simplify population by group age groups(TRUE) or including all ages (FALSE)
SIMPLIFY_POP_EVOLUTION = True
# Defines the superior limit of age groups, the first value is always ZERO and is omitted from the list.
LIST_NEW_AGE_GROUPS = [6, 12, 17, 25, 35, 45, 65, 100]
MARRIAGE_CHECK_PROBABILITY = .034

# Consumption_equal: ratio of consumption tax distributed at state level (equal)
# Fpm: ratio of 'labor' and 'firm' taxes distributed per the fpm ruling
TAXES_STRUCTURE = {'consumption_equal': .1875, 'fpm': .235}

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
PRIVATE_TRANSIT_COST = 0.25
PUBLIC_TRANSIT_COST = 0.05

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
PERCENTAGE_ACTUAL_POP = 0.01

# Write exactly like the list above
PROCESSING_ACPS = ['BRASILIA']

# Selecting the starting year to build the Agents, can be: 1991, 2000 or 2010
STARTING_DAY = datetime.date(2010, 1, 1)

# Maximum running time (restrained by official data) is 30 years,
TOTAL_DAYS = (datetime.date(2020, 1, 1) - STARTING_DAY).days
