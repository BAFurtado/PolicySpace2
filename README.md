PolicySpace2: Real Estate Modeling
------
<img alt="GitHub stars" src="https://img.shields.io/github/stars/bafurtado/policyspace2.svg?color=orange">  ![GitHub All Releases](https://img.shields.io/github/downloads/bafurtado/policyspace2/total) ![GitHub](https://img.shields.io/github/license/bafurtado/policyspace2)  ![GitHub forks](https://img.shields.io/github/forks/bafurtado/policyspace2)
------

<a href="https://www.comses.net/codebases/c8775158-4360-46d8-bac8-be94502b04b0/releases/1.2.0/"><img src="https://www.comses.net/static/images/icons/open-code-badge.png" align="left" height="64" width="64" ></a>

---
#### Reviewed code at ComSES

## Post-PolicySpace2 work

1. Optimal policy, which, where, and why: https://papers.ssrn.com/sol3/papers.cfm?abstract_id=4276602
2. Machine Learning Simulates Agent-Based Model Towards Policy: https://arxiv.org/abs/2203.02576

### Published at JASSS

## https://www.jasss.org/25/1/8.html

Policymakers' role in decision making on alternative policies is facing restricted budgets and an uncertain future. 
The need to decide on priorities and handle effects across policies has made their task even more difficult. 
For instance, housing policies involve heterogeneous characteristics of the properties themselves and the intricacy 
of housing markets within the spatial context of cities. Here, we have proposed PolicySpace2 (PS2) as an adapted and 
extended version of the open source PolicySpace agent-based model. PS2 is a computer simulation that relies 
on empirically detailed spatial data to model real estate, along with labor, credit, and goods and services markets. 
Interaction among workers, firms, a bank, households and municipalities follow the literature benchmarks by 
integrating economic, spatial and transport research. PS2 is applied here as a comparison of three competing public 
policies aimed at reducing inequality and alleviating poverty: (a) house acquisition by the government and 
distribution to lower income households, (b) rental vouchers and (c) monetary aid. Within the model context, 
monetary aid, that is smaller amounts of help for a larger number of households, improves the economy in terms 
of production, consumption, reduction of inequality and maintenance of financial duties. PS2 is also a framework 
that can be further adapted to a number of related research questions.  


This is an evolution of PolicySpace  
<img alt="GitHub stars" src="https://img.shields.io/github/stars/bafurtado/policyspace.svg?color=orange">  ![GitHub forks](https://img.shields.io/github/forks/bafurtado/policyspace)
 ---

Available here: https://github.com/BAFurtado/PolicySpace and published as a book 
here: https://www.researchgate.net/publication/324991027_PolicySpace_agent-based_modeling

 
 **FURTADO, Bernardo Alves. PolicySpace: agent-based modeling. IPEA: Brasília, 2018.** 

This was an open agent-based model (ABM) with three markets and a tax scheme that empirically simulates 46 Brazilian
metropolitan regions. Now, we have also **added a credit market, a housing construction scheme and an incipient 
land market mechanism**. 

### Collaborators
Bernardo Alves Furtado -- https://sites.google.com/view/bernardo-alves-furtado

Francis Tseng --  http://frnsys.com

![GitHub labels](https://img.shields.io/github/labels/atom/atom/help-wanted)

### Funding

Developed by Bernardo Alves Furtado, funded primarily by Institute of Applied Economic Research (IPEA) 
[www.ipea.gov.br] with one-period grant from [https://www.cepal.org/pt-br/sedes-e-escritorios/cepal-brasilia] 
(CEPAL-Brasília) and International Policy Centre (https://ipcig.org/). 
BAF acknowledges receiving a grant of productivity by National Council of Research (CNPq) [www.cnpq.br].

#### Recent publication

Furtado, B. A. (2019). Modeling tax distribution in metropolitan regions with PolicySpace. 
Journal on Policy and Complex Systems, 5(1). https://doi.org/10.18278/jpcs.5.1.6

### Major changes

**new BOOK describing changes and processes currently on the make**

1. PolicySpace2 generates data that can be applied at https://github.com/frnsys/transit_demand_model. 
The transit model in turn generates private and public transport routes, visualization and congestion times.
2. Now data is read at the **intraurban** level of 'áreas de ponderação' (census track/block) from IBGE.
3. There is exogenous migration embedded in the model (creating new houses)
4. Exogenous growth of firms
5. Marriage 
6. Better support for plot formats
7. House prices (supply) are included into families' wealth and updated every month
8. Consumption decisions now follow Bielefeld, 2018 and is now a 
"linear function of current and expected future incomes and of financial wealth." In other words, 
"all income in excess of permanent income will be saved and added to financial wealth."
9. Families composition are now sure to have at least one adult. Children are initially distributed randomly.
10. Houses of families whose last member dies are randomly allocated to remaining family members.
11. Interest being now paid on families' savings
12. When no cash available, families can withdraw from savings for consumption (if any at savings) 
up to permanent income
13. Internal clock updated to use datetime
14. Introduced a rental market 
15. Included construction companies endogenous to the model.
16. Financial (mortgage, credit) market structures
17. Included transportation costs on workers' decision on choosing jobs
18. Introduce inheritance (savings).
19. A neighborhood effect (wealth of resident families influence price of houses)
20. Decay effect on prices due to excess of houses on offer 
21. Data updated (from census 2000 to census 2010)
22. Offer decay (time depreciation) implemented
23. Global availability of houses (vacancy) influences prices
24. Neighborhood effects (based on families' wealth) influence prices.
25. Possibility of negotiating house prices below the offer
26. Vacancy size (offer) now impacts willingness to build of construction firms and prices
27. New output analysis
28. Endogenous mortgage rate setting by the bank. Default uses exogenous data though.
29. Included the SAC -- Constant Amortization System -- mostly used in Brazil.
30. POLICY EXPERIMENTAL DESIGN. Testing wether giving houses, paying rent or distribution money is the best policy
    alternative. Both families in poverty and resources invested are endogenous.
31. Included varying oficial monthly interest rate.      


#### How do I get set up?

We recommend using conda  and creating an environment that includes all libraries simultaneously.

First create an environment and install Shapely and GDAL as such:

`conda create --name ps2 python=3.6`

Activate the environmnet

`conda activate ps2`

Then add Shapely from conda-forge channel
 `conda install shapely gdal -c conda-forge`

Then the other packages 
`conda install fiona pandas geopandas numba descartes scipy seaborn pyproj matplotlib six cycler statsmodels joblib scikit-learn flask flask-wtf psutil -c conda-forge`

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
It now also accepts selected "PROCESSING_ACPS-BRASILIA-CAMPINAS-FORTALEZA-BELO HORIZONTE"

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
python main.py sensitivity MARKUP:.05:.15:7 WAGE_IGNORE_UNEMPLOYMENT
```

is equivalent to running the previous two examples in sequence.

For multiple combinations of parameters one may try the following rules

Include first the params, separated by '+', then '*' and then the list of values also '+'
Such as 'param1+param2*1+2*10+20'.
Thus,  producing the dict: {'param1': ['10', '20'], 'param2': ['10', '20']}
```
python main.py sensitivity PRODUCTIVITY_EXPONENT+PRODUCTIVITY_MAGNITUDE_DIVISOR*.3+.4*10+20
```
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

Then open `localhost:5000` in your browser.
