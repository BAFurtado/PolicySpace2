# THE ROOT OUTPUT DATA LOCATION #######################################################################################
# Change your output directory as necessary
import datetime


# OUTPUT_PATH = 'output'
OUTPUT_PATH = r'\\STORAGE1\CARGA\MODELO DINAMICO DE SIMULACAO\EXITS_PYTHON\PS2020'

KEEP_RANDOM_SEED = False

# Descriptive stats to plot evolution of age and qualification by municipality
DESCRIPTIVE_STATS_CHOICE = False

# Logging
PRINT_STATISTICS_AND_RESULTS_DURING_PROCESS = True
PRINT_FINAL_STATISTICS_ABOUT_AGENTS = False
PRINT_TIME_CONTROL_IN_TIME_ITERATION = False

# Inform numbers in percentage of the period
TIME_TO_BE_ELIMINATED = 0.0

# Saving adjustments
SAVE_PLOTS_FIGURES = True

# If plots should be generated separately
# for each simulation run or just aggregated
PLOT_EACH_RUN = False
# Spatial plots only works when PLOT_EACH_RUN is True
SAVE_SPATIAL_PLOTS = False
# 'png' or 'eps'
PLOT_FORMAT = 'png'
PLOT_REGIONAL = False

# NOTE THAT YOU NEED TO SAVE_AGENTS_DATA to generate the plots, because this is what saves the output CSV data.
# You can also use set it to "QUARTERLY" or "ANNUALLY" to save less frequently.
# SAVE_DATA lets you narrow down what data to save.
# Firms and banks data are always saved, "agents", "grave", "house", "family" are optional.
# If you don't save "house" data for instance you can't generate housing plots.
# Save Agents data
SAVE_AGENTS_DATA = 'MONTHLY' # or 'QUARTERLY', 'ANNUALLY', or None

# What extra data (i.e. not necessary plotting) to save
# Can include: ['agents', 'grave', 'house', 'family', 'banks']
# If None, set to empty list: []
# SAVE_DATA = []
SAVE_DATA = ['house', 'family', 'banks']

# What data to average
# across all runs
# Options: ['stats', 'families', 'housing', 'firms', 'regional', 'banks', 'construction']
AVERAGE_DATA = ['stats', 'families', 'housing', 'banks']

# Whether or not to save data for the transit simulation
SAVE_TRANSIT_DATA = False

# Limit to the following region ids that begin with any
# of the listed codes (as strings).
# If None, include all
LIMIT_SAVED_TRANSIT_REGIONS = None

# Selecting the starting year to build the Agents, can be: 1991, 2000 or 2010
STARTING_DAY = datetime.date(2000, 1, 1)

# Maximum running time (restrained by official data) is 30 years,
TOTAL_DAYS = (datetime.date(2020, 1, 1) - STARTING_DAY).days

# Force generation of new population
FORCE_NEW_POPULATION = False
