# MODEL PARAMETERS
# FIRMS
# Production function, labour with decaying exponent, Alpha for K. [0, 1]
ALPHA = .24
# By how much percentage to increase prices
MARKUP = 0.15
# Frequency firms change prices. Probability > than parameter
STICKY_PRICES = .5
# Order of magnitude correction of production. Production divided by parameter
PRODUCTION_MAGNITUDE = 76

# Number of firms consulted before consumption
SIZE_MARKET = 10

# Frequency firms enters in the market
LABOR_MARKET = 0.05

# Percentage of employees firms hire by distance
PCT_DISTANCE_HIRING = .17
# Ignore unemployment in wage base calculation
WAGE_IGNORE_UNEMPLOYMENT = False
# Candidate sample size for the labor market
HIRING_SAMPLE_SIZE = 100

# Percentage of households pursuing new location
# PERCENTAGE_CHECK_NEW_LOCATION = 0.002
PERCENTAGE_CHECK_NEW_LOCATION = 0.02

# TAXES
TAX_CONSUMPTION = 3.9E-04
TAX_LABOR = 1.3E-04
TAX_ESTATE_TRANSACTION = 1.5E-06
TAX_FIRM = 4.4E-04
TAX_PROPERTY = 1.4E-06

# LOANS
MAX_LOAN_AGE = 80
MAX_LOAN_REPAYMENT_PERCENT_INCOME = 0.05

# GOVERNMENT
# ANNUAL Real interest rate of the economy (SELIC minus INFLATION) for the Brazilian case
INTEREST_RATE = round(0.06 - 0.055, 4)
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
LICENSES_PER_REGION = 10000

# Families run parameters
MEMBERS_PER_FAMILY = 2.5                             # (on average)
HOUSE_VACANCY = .1                                   # percentage of vacant houses
RENTAL_SHARE = .2
INITIAL_RENTAL_PRICE = .05
# Definition to simplify population by group age groups(TRUE) or including all ages (FALSE)
SIMPLIFY_POP_EVOLUTION = True
# Defines the superior limit of age groups, the first value is always ZERO and is omitted from the list.
LIST_NEW_AGE_GROUPS = [6, 12, 17, 25, 35, 45, 65, 100]

# Percentage of actual population to run the simulation
# Minimum value to run depends on the size of municipality 0,001 is recommended minimum
PERCENTAGE_ACTUAL_POP = 0.002

# Consumption_equal: ratio of consumption tax distributed at state level (equal)
# Fpm: ratio of 'labor' and 'firm' taxes distributed per the fpm ruling
TAXES_STRUCTURE = {'consumption_equal': .1875,
                   'fpm': .235}

# Order of magnitude parameter
TREASURE_INTO_SERVICES = 1

# selecting the ACPs (Population Concentration Areas)
# ACPs and their STATES - ALL ACPs written in UPPER CASE and whiteout  ACCENT
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

# Write exactly like the list
PROCESSING_ACPS = ['IPATINGA']
