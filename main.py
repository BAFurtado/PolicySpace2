"""
This is the model that organizes the full simulation.
It handles all the choices of the model, usually set at the Parameters module.


Disclaimer:
This code was generated for research purposes only.
It is licensed under GNU v3 license
"""
import copy
import json
import logging
import os
import random
import sys
from collections import defaultdict
import datetime
from glob import glob
from itertools import product

import click
import matplotlib
# import validation_tentative
import numpy as np
import pandas as pd
from joblib import Parallel, delayed

import conf
from analysis import report
from analysis.output import OUTPUT_DATA_SPEC
from analysis.plotting import Plotter, MissingDataError
from simulation import Simulation
from web import app

matplotlib.use('agg')

logger = logging.getLogger('main')
logging.basicConfig(level=logging.INFO)


def conf_to_str(conf, delimiter='\n'):
    """Represent a configuration dict as a string"""
    parts = []
    for k, v in sorted(conf.items()):
        v = ','.join(v) if isinstance(v, list) else str(v)
        part = '{}={}'.format(k, v)
        parts.append(part)
    return delimiter.join(parts)


def single_run(params, path):
    """Run a simulation once for given parameters"""
    if conf.RUN['PRINT_STATISTICS_AND_RESULTS_DURING_PROCESS']:
        logging.basicConfig(level=logging.INFO)
    sim = Simulation(params, path)
    sim.initialize()
    sim.run()

    if conf.RUN['PLOT_EACH_RUN']:
        logger.info('Plotting run...')
        plot([('run', path)], os.path.join(path, 'plots'), params, sim=sim)


def multiple_runs(overrides, runs, cpus, output_dir, fix_seeds=False):
    """Run multiple configurations, each `runs` times"""
    logger.info('Running simulation {} times'.format(len(overrides) * runs))

    if fix_seeds:
        seeds = [random.randrange(sys.maxsize) for _ in range(runs)]
    else:
        seeds = []

    # calculate output paths and params with overrides
    paths = [os.path.join(output_dir, conf_to_str(o, delimiter=';'))
             for o in overrides]
    params = []
    for o in overrides:
        p = copy.deepcopy(conf.PARAMS)
        p.update(o)
        params.append(p)

    # run simulations in parallel
    if cpus == 1:
        # run serially if cpus==1, easier debugging
        for p, path in zip(params, paths):
            for i in range(runs):
                if seeds:
                    p['SEED'] = seeds[i]
                single_run(p, os.path.join(path, str(i)))
    else:
        jobs = []
        for p, path in zip(params, paths):
            for i in range(runs):
                if seeds:
                    p['SEED'] = seeds[i]
                jobs.append((delayed(single_run)(p, os.path.join(path, str(i)))))
        Parallel(n_jobs=cpus)(jobs)

    logger.info('Averaging run data...')
    results = []
    for path, params, o in zip(paths, params, overrides):
        # save configurations
        with open(os.path.join(path, 'conf.json'), 'w') as f:
            json.dump({
                'RUN': conf.RUN,
                'PARAMS': params
            }, f, default=str)

        # average run data and then plot
        runs = [p for p in glob('{}/*'.format(path)) if os.path.isdir(p)]
        avg_path = average_run_data(path, avg=conf.RUN['AVERAGE_TYPE'])

        # return result data, e.g. paths for plotting
        results.append({
            'path': path,
            'runs': runs,
            'params': params,
            'overrides': o,
            'avg': avg_path,
            'avg_type': conf.RUN['AVERAGE_TYPE']
        })
    with open(os.path.join(output_dir, 'meta.json'), 'w') as f:
        json.dump(results, f, default=str)

    plot_results(output_dir)

    # link latest sim to convenient path
    latest_path = os.path.join(conf.RUN['OUTPUT_PATH'], 'latest')
    if os.path.isdir(latest_path):
        os.remove(latest_path)

    try:
        os.symlink(os.path.join('..', output_dir), latest_path)
    except OSError: # Windows requires special permissions to symlink
        pass

    logger.info('Finished.')
    return results


def average_run_data(path, avg='mean'):
    """Average the run data for a specified output path"""
    output_path = os.path.join(path, 'avg')
    os.makedirs(output_path)

    # group by filename
    file_groups = defaultdict(list)
    keep_files = {'temp_{}.csv'.format(k): k for k in conf.RUN['AVERAGE_DATA']}
    for file in glob(os.path.join(path, '**/*.csv')):
        fname = os.path.basename(file)
        if fname in keep_files:
            file_groups[fname].append(file)

    # merge
    for fname, files in file_groups.items():
        spec = OUTPUT_DATA_SPEC[keep_files[fname]]
        dfs = []
        for f in files:
            df = pd.read_csv(f,  sep=';', decimal='.', header=None)
            dfs.append(df)
        df = pd.concat(dfs)
        df.columns = spec['columns']

        # Saving date before averaging
        avg_cols = spec['avg']['columns']
        if avg_cols == 'ALL': avg_cols = [c for c in spec['columns'] if c not in spec['avg']['groupings']]

        # Ensure these columns are numeric
        df[avg_cols] = df[avg_cols].apply(pd.to_numeric)

        dfg = df.groupby(spec['avg']['groupings'])
        dfg = dfg[avg_cols]
        df = getattr(dfg, avg)()
        df = df.reset_index() # "ungroup" by
        df.to_csv(os.path.join(output_path, fname), header=False, index=False, sep=';')
    return output_path


def plot(input_paths, output_path, params, avg=None, sim=None, only=None):
    """Generate plots based on data in specified output path"""
    logger.info('Plotting to {}'.format(output_path))
    plotter = Plotter(input_paths, output_path, params, avg=avg)

    if conf.RUN['DESCRIPTIVE_STATS_CHOICE']:
        report.stats('')

    keys = ['general', 'firms',
            'construction', 'houses',
            'families', 'banks']
    if only is not None:
        keys = [k for k in keys if k in only]

    if conf.RUN['SAVE_PLOTS_FIGURES'] and conf.RUN['SAVE_AGENTS_DATA'] is not None:
        for k in keys:
            try:
                logger.info('Plotting {}...'.format(k))
                getattr(plotter, 'plot_{}'.format(k))()
            except MissingDataError:
                logger.warn('Missing data for "{}", skipping.'.format(k))
                if avg is not None:
                    logger.warn('You may need to add "{}" to AVERAGE_DATA.'.format(k))

        if sim is not None and conf.RUN['PLOT_REGIONAL']:
            logger.info('Plotting regional...')
            plotter.plot_regional_stats()

    # Checking whether to plot or not
    if conf.RUN['SAVE_SPATIAL_PLOTS'] and sim is not None:
        logger.info('Plotting spatial...')
        plotter.plot_geo(sim, 'final')


def plot_runs_with_avg(run_data):
    """Plot results of simulations sharing a configuration,
    with their average results"""
    # individual runs
    labels_paths = list(enumerate(run_data['runs']))

    # output to the run directory + /plots
    output_path = os.path.join(run_data['path'], 'plots')

    # plot
    plot(labels_paths, output_path, {}, avg=(run_data['avg_type'], run_data['avg']))


def plot_results(output_dir):
    """Plot results of multiple simulations"""
    logger.info('Plotting results...')
    results = json.load(open(os.path.join(output_dir, 'meta.json'), 'r'))
    avgs = []
    for r in results:
        if not conf.RUN.get('SKIP_PARAM_GROUP_PLOTS'):
            plot_runs_with_avg(r)

        # group averages, with labels, to plot together
        label = conf_to_str(r['overrides'], delimiter='\n')
        avgs.append((label, r['avg']))

    # plot averages
    if len(avgs) > 1:
        output_path = os.path.join(output_dir, 'plots')
        plot(avgs, output_path, {}, only=['general'])


def impute(data):
    """very naive/imprecise data imputation, can be improved"""
    return data.interpolate(limit_direction='both').fillna(method='bfill')


def gen_output_dir(command):
    timestamp = datetime.datetime.utcnow().isoformat().replace(':', '_')
    run_id = '{}__{}'.format(command, timestamp)
    return os.path.join(conf.RUN['OUTPUT_PATH'], run_id)


@click.group()
@click.pass_context
@click.option('-n', '--runs', help='Number of simulation runs', default=1)
@click.option('-c', '--cpus', help='Number of CPU cores to use', default=1)
@click.option('-p', '--params', help='JSON of params override')
@click.option('-r', '--config', help='JSON of run config override')
def main(ctx, runs, cpus, params, config):
    if conf.RUN['SAVE_AGENTS_DATA'] == None:
        logger.warn('Warning!!! Are you sure you do NOT want to save AGENTS\' data?')

    # apply any top-level overrides, if specified
    params = json.loads(params) if params is not None else {}
    config = json.loads(config) if config is not None else {}
    conf.PARAMS.update(params) # applied per-run
    conf.RUN.update(config)    # applied globally

    ctx.obj = {
        'output_dir': gen_output_dir(ctx.invoked_subcommand),
        'runs': runs,
        'cpus': cpus
    }


@main.command()
@click.pass_context
def run(ctx):
    """
    Basic run(s) with different seeds
    """
    multiple_runs([{}], ctx.obj['runs'], ctx.obj['cpus'], ctx.obj['output_dir'])


@main.command()
@click.argument('params', nargs=-1)
@click.pass_context
def sensitivity(ctx, params):
    """
    Continuous param syntax: NAME:MIN:MAX:STEP
    Boolean param syntax: NAME
    """
    for param in params:
        ctx.obj['output_dir'] = gen_output_dir(ctx.command.name)

        # if ':' present, assume continuous param
        if ':' in param:
            p_name, p_min, p_max, p_step = param.split(':')
            p_min, p_max = float(p_min), float(p_max)
            p_vals = np.linspace(p_min, p_max, int(p_step))

            # round to 8 decimal places
            p_vals = [round(v, 8) for v in p_vals]

        # TODO: Fix plots for starting-day. Yearly information refers to 2010-2020. Should go the whole period.
        elif param == 'STARTING_DAY':
            p_name = param
            p_vals = [datetime.date(2000, 1, 1), datetime.date(2010, 1, 1)]
        # else, assume boolean
        elif '-' in param:
            p_name = 'PROCESSING_ACPS'
            p_vals = [[i] for i in param.split('-')[1:]]
        else:
            p_name = param
            p_vals = [True, False]
            # TODO: allow for multiple parameters to be update at a time
        confs = [{p_name: v} for v in p_vals]

        # fix the same seed for each run
        conf.RUN['KEEP_RANDOM_SEED'] = False
        # conf.RUN['FORCE_NEW_POPULATION'] = False # Ideally this is True, but it slows things down a lot
        conf.RUN['SKIP_PARAM_GROUP_PLOTS'] = True

        logger.info('Sensitivity run over {} for values: {}, {} run(s) each'.format(p_name, p_vals, ctx.obj['runs']))
        multiple_runs(confs, ctx.obj['runs'], ctx.obj['cpus'], ctx.obj['output_dir'], fix_seeds=True)


@main.command()
@click.pass_context
def distributions(ctx):
    """
    Run across ALTERNATIVE0/FPM_DISTRIBUTION combinations
    """
    confs = [{
        'ALTERNATIVE0': ALTERNATIVE0,
        'FPM_DISTRIBUTION': FPM_DISTRIBUTION
    } for ALTERNATIVE0, FPM_DISTRIBUTION in product([True, False], [True, False])]

    logger.info('Varying distributions, {} run(s) each'.format(ctx.obj['runs']))
    multiple_runs(confs, ctx.obj['runs'], ctx.obj['cpus'], ctx.obj['output_dir'])


@main.command()
@click.pass_context
def distributions_acps(ctx):
    """
    Run across taxes combinations for all ACPs
    """
    confs = []
    dis = [{
        'ALTERNATIVE0': ALTERNATIVE0,
        'FPM_DISTRIBUTION': FPM_DISTRIBUTION
    } for ALTERNATIVE0, FPM_DISTRIBUTION in product([True, False], [True, False])]

    exclude_list = []
    # ACPs with just one municipality
    exclude_list = ['CAMPO GRANDE', 'CAMPO DOS GOYTACAZES', 'FEIRA DE SANTANA', 'MANAUS',
                    'PETROLINA - JUAZEIRO', 'TERESINA', 'UBERLANDIA']
    all_acps = pd.read_csv('input/ACPs_BR.csv', sep=';', header=0)
    acps = set(all_acps.loc[:, 'ACPs'].values.tolist())
    acps = list(acps)
    for acp in acps:
        if acp not in exclude_list:
            dic0 = {'PROCESSING_ACPS': [acp]}
            for each in dis:
                confs.append(dict(dic0, **each))

    logger.info('Varying distributions, {} run(s) each'.format(ctx.obj['runs']))
    multiple_runs(confs, ctx.obj['runs'], ctx.obj['cpus'], ctx.obj['output_dir'])


@main.command()
@click.pass_context
def acps(ctx):
    """
    Run across ACPs
    """
    confs = []
    exclude_list = []
    # ACPs with just one municipality
    exclude_list = ['CAMPO GRANDE', 'CAMPO DOS GOYTACAZES', 'FEIRA DE SANTANA', 'MANAUS',
                    'PETROLINA - JUAZEIRO', 'TERESINA', 'UBERLANDIA']
    all_acps = pd.read_csv('input/ACPs_BR.csv', sep=';', header=0)
    acps = set(all_acps.loc[:, 'ACPs'].values.tolist())
    acps = list(acps)
    for acp in acps:
        if acp not in exclude_list:
            confs.append({
                'PROCESSING_ACPS': [acp]
            })
    logger.info('Running over ACPs, {} run(s) each'.format(ctx.obj['runs']))
    multiple_runs(confs, ctx.obj['runs'], ctx.obj['cpus'], ctx.obj['output_dir'])


@main.command()
@click.argument('output_dir')
def make_plots(output_dir):
    """
    (Re)generate plots for an output directory
    """
    plot_results(output_dir)


# @main.command()
# @click.option('-s', '--sig-level', help='Significance level', default=0.05)
# @click.pass_context
# def validate(ctx, sig_level):
#     """
#     Validate simulation output
#     """
#     df = pd.read_csv('validating_data/general.csv')
#     rw_data = {
#         'inflation': impute(df['real_inflation']).values,
#         'consumption': impute(df['real_consumption']).values
#     }
#
#     ab_data = [{
#         'inflation': impute(df['model_inflation']).values,
#         'consumption': impute(df['model_consumption']).values
#     }]
#     rw_data_len = len(df['real_inflation'].values)
#     results = validation_tentative.validate(rw_data, ab_data, rw_data_len, sig_level)
#     print(results)


@main.command()
def web():
    app.run(debug=False)


if __name__ == '__main__':
    main()
