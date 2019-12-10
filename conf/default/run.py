# THE ROOT OUTPUT DATA LOCATION #######################################################################################
# Change your output directory as necessary
import datetime


OUTPUT_PATH = r'\\storage6\usuarios\# MODELO DINAMICO DE SIMULACAO #\Exits_python\output\policy2'
# OUTPUT_PATH = '/home/furtadobb/MyModels/policyspace2/output/testes_fpm'

KEEP_RANDOM_SEED = False

# Descriptive stats to plot evolution of age and qualification by municipality
DESCRIPTIVE_STATS_CHOICE = False

# Logging
PRINT_STATISTICS_AND_RESULTS_DURING_PROCESS = True
PRINT_FINAL_STATISTICS_ABOUT_AGENTS = True
PRINT_TIME_CONTROL_IN_TIME_ITERATION = False

# Inform numbers in percentage of the period
TIME_TO_BE_ELIMINATED = 0.0

# Saving adjustments
SAVE_PLOTS_FIGURES = False

# If plots should be generated separately
# for each simulation run or just aggregated
PLOT_EACH_RUN = False
# Spatial plots only works when PLOT_EACH_RUN is True
SAVE_SPATIAL_PLOTS = False
# 'png' or 'eps'
PLOT_FORMAT = 'png'
PLOT_REGIONAL = False

# Save Agents data
SAVE_AGENTS_DATA_MONTHLY = True
SAVE_AGENTS_DATA_QUARTERLY = False
SAVE_AGENTS_DATA_ANNUALLY = False

# What extra data (i.e. not necessary plotting) to save
# Can include: ['agents', 'grave', 'house', 'family', 'banks']
# If None, set to empty list: []
SAVE_DATA = ['house', 'family', 'banks']

# Average all data (not just general data)
# across all runs
AVERAGE_ALL_DATA = False

# Whether or not to save data for the transit simulation
SAVE_TRANSIT_DATA = False

# Limit to the following region ids that begin with any
# of the listed codes (as strings).
# If None, include all
LIMIT_SAVED_TRANSIT_REGIONS = None

# Selecting the starting year to build the Agents, can be: 1991, 2000 or 2010
STARTING_DAY = datetime.date(2000, 1, 1)

# Maximum running time (restrained by official data) is 30 years,
TOTAL_DAYS = (datetime.date(2002, 1, 1) - STARTING_DAY).days

# Force generation of new population
FORCE_NEW_POPULATION = False
