# PolicySpace2

This is an evolution of:

**FURTADO, Bernardo Alves. PolicySpace: agent-based modeling. IPEA: Brasília, 2018.** available at https://github.com/BAFurtado/PolicySpace

This is an open agent-based model (ABM) with three markets and a tax scheme that empirically simulates 46 Brazilian
metropolitan regions.

Developed by Bernardo Alves Furtado, funded by Institute of Applied Economic Research (IPEA).
The author acknowledges receiving a grant of productivity by National Council of Research (CNPq).

This work is licensed under GNU General Public License v3.0

#### Recent publication

Furtado, B. A. (2019). Modeling tax distribution in metropolitan regions with PolicySpace. Journal on Policy and Complex Systems, 5(1). https://doi.org/10.18278/jpcs.5.1.6

#### Repository of produced texts
https://www.researchgate.net/profile/Bernardo_Furtado

### Previous collaborator after PolicySpace
Francis Tseng (automating, general fixtures and improvements, transport, plots, output) [April-July 2018]

### Major changes, since PolicySpace

1. PolicySpace2 generates data that can be applied at https://github.com/frnsys/transit_demand_model. 
The transit model in turn generates private and public transport routes, visualization and congestion times.
2. Now data is read at the **intraurban** level of 'áreas de ponderação' (census track/block) from IBGE.
3. There is exogenous migration embedded in the model (creating new houses)
4. Exogenous growth of firms
5. [Marriage disabled]
6. Better support for plot formats
7. House prices (supply) are included into families' wealth and updated every month
8. Consumption decisions now follow Bielefeld, 2018 and is now a 
"linear function of current and expected future incomes and of financial wealth." In other words, 
"all income in excess of permanent income will be saved and added to financial wealth."
9. Families composition are now sure to have at least one adult. Children are initially distributed randomly.
10. Houses of families whose last member dies are randomly allocated to remaining families.
11. Interest being now paid on families' savings
12. When no cash available, families can withdraw from savings for consumption (if any at savings) 
up to permanent income
13. Internal clock updated to use datetime

#### How do I get set up?

We recommend using conda  and creating an environment that includes all libraries simultaneously.

First create an environment and install Shapely and GDAL as such:

`conda create --name ps2 python=3.7`

Then add Shapely from conda-forge channel
 `conda install shapely -c conda-forge`
 `conda install gdal -c conda-forge`

Then the other packages 
`conda install fiona shapely numpy pandas geopandas numba
descartes scipy seaborn pyproj matplotlib six cycler statsmodels
joblib scikit-learn flask flask-wtf psutil -c conda-forge`
 
Type on a terminal, after having downloaded and installed conda, choosing a name for your environment and replacing 
<env> and using requirements.txt | requirements_linux.txt in place of <this file>

`conda create --name <env> --file <this file>`

## How to run the model ##

### Configuration

To locally configure the simulation's parameters, create the following files as needed:

- `conf/run.py` for run-specific options, e.g. `OUTPUT_PATH` for where sim results are saved
- `conf/params.py` for simulation parameters, e.g. `LABOR_MARKET`.

The default options are in `conf/default/`, refer to those for what values can be set.

### Parallelization and multiple runs

These optional arguments are available for all the run commands:

- `-n` or `--runs` to specify how many times to run the simulation.
- `-c` or `--cpus` to specify number of CPUs to use when running multiple times. Use `-1` for all cores (default).

### Running

```
python main.py run
```

Example:

```
python main.py -c 2 -n 10 run
```

#### Sensitivity analysis

Runs simulation over a range of values for a specific parameter. For continuous parameters, the syntax is
`NAME:MIN:MAX:NUMBER_STEPS`. For boolean parameters, just provide the parameter name.

Example:

```
python main.py sensitivity ALPHA:0:1:7
```

Will run the simulation once for each value `ALPHA=0`, `ALPHA=0.17`, `ALPHA=0.33`, ... `ALPHA=1`.

Example:

```
python main.py sensitivity WAGE_IGNORE_UNEMPLOYMENT
```

Will run the simulation once for each value `WAGE_IGNORE_UNEMPLOYMENT=True` & `WAGE_IGNORE_UNEMPLOYMENT=False`.

You can also set up multiple sensitivity runs at once.

For example:

```
python main.py sensitivity ALPHA:0:1:0.1 WAGE_IGNORE_UNEMPLOYMENT
```

is equivalent to running the previous two examples in sequence.


#### Distributions

Runs simulation over a different distribution combinations: `ALTERNATIVE0: True/False, FPM_DISTRIBUTION: True/False`.

Example:

```
python main.py -n 2 -c 2 distributions
```

#### ACPs

Runs simulation over a different ACPs.

Example:

```
python main.py -n 2 -c 2 acps
```

#### Regenerating plots

You can regenerate plots for a set of runs by using:

```
python main.py make_plots /path/to/output
```

In Windows, make sure to use double quotes " " and backward slashes as in:

```
python main.py make_plots
"..\run__2017-11-01T11_59_59.240250_bh"
```

### Running the web interface

There is a preliminary web interface in development.

To run the server:

```
python main.py web
```

Then open `localhost:5000` in your browser.
---
