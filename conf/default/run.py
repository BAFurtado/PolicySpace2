# THE ROOT OUTPUT DATA LOCATION #######################################################################################
# Change your output directory as necessary


# OUTPUT_PATH = 'output'
OUTPUT_PATH = r'output'

KEEP_RANDOM_SEED = False

# Descriptive stats to plot evolution of age and qualification by municipality
DESCRIPTIVE_STATS_CHOICE = False

# Logging
PRINT_STATISTICS_AND_RESULTS_DURING_PROCESS = True
PRINT_FINAL_STATISTICS_ABOUT_AGENTS = False

# Inform numbers in percentage of the period
TIME_TO_BE_ELIMINATED = .05

# Saving adjustments
# If you save_plots (in a multiple run), you need AVERAGE_DATA = ['stats'] below!
SAVE_PLOTS_FIGURES = False

# If plots should be generated separately for each simulation run or just aggregated
# When PLOT_EACH_RUN is True, DATA for banks, construction, firms, regional, stats are also SAVED
# *be aware of theirs sizes*
PLOT_EACH_RUN = False
# Spatial plots only works when PLOT_EACH_RUN is True
SAVE_SPATIAL_PLOTS = False
# 'png' or 'eps'
PLOT_FORMAT = 'png'
PLOT_REGIONAL = False

# Plot DPI. Lower ones will plot faster
PLOT_DPI = 600

# Save Agents data 'MONTHLY' or 'QUARTERLY', 'ANNUALLY', or None
SAVE_AGENTS_DATA = 'MONTHLY'

# What extra CSV data (i.e. not necessary plotting) to save
# 'firms', 'banks', 'construction', 'regional' and 'stats' data are always saved,
# "agents", "grave", "house", "family" are optional.
# If you don't save "house" data for instance you can't generate housing plots.
# Can include: ['agents', 'grave', 'house', 'family']
# If None, set to empty list: []
SAVE_DATA = []
# SAVE_DATA = ['agents', 'house', 'family']

# What data to average across all runs. If plotting and not 'firms', 'banks', 'construction' or 'regional',
# needs to include them in SAVE_DATA as well
# Notice that they are grouped by MONTH and MUNICIPALITY and some values may not make sense
# Options: ['families', 'houses', 'agents]
# You need to INCLUDE STATS to generate SPATIAL PLOTS. 'stats' also refer to general averaged plots

AVERAGE_DATA = ['stats', 'regional']
# 'median' or 'mean'
AVERAGE_TYPE = 'mean'

# Whether to save data for the transit simulation
SAVE_TRANSIT_DATA = False

# Limit to the following region ids that begin with any of the listed codes (as strings).
# If None, include all
LIMIT_SAVED_TRANSIT_REGIONS = None

# Force generation of new population
FORCE_NEW_POPULATION = False
