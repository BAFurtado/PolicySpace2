import os

from flask import Blueprint, render_template, redirect, url_for, send_from_directory

import conf
from . import manager
from .forms import SimulationForm

bp = Blueprint('web', __name__)



@bp.route('/')
def index():
    return render_template('status.html')


@bp.route('/start', methods=['GET', 'POST'])
def start():
    form = SimulationForm()
    if form.validate_on_submit():
        manager.start(**form.data)
        return redirect(url_for('web.index'))
    return render_template('start.html', form=form)


@bp.route('/results')
def runs():
    # sort by datetime, most recent first
    ids = os.listdir(conf.RUN['OUTPUT_PATH'])
    ids = sorted(ids, key=lambda d: d.split('__')[-1], reverse=True)
    return render_template('runs.html', runs=ids)


@bp.route('/results/<string:id>')
def results(id):
    # Currently just showing top-level plots
    path = os.path.join(conf.RUN['OUTPUT_PATH'], id)
    plots = os.path.join(path, 'plots')
    try:
        plots = [os.path.join('/output', id, 'plots', p) for p in os.listdir(plots)]
    except FileNotFoundError:
        plots = []
    return render_template('results.html', id=id, plots=plots)


@bp.route('/output/<path:filename>')
def output(filename):
    """serve simulation result files from the output path"""
    return send_from_directory(conf.RUN['OUTPUT_PATH'], filename)
