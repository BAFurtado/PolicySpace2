import json
import conf
from . import manager
from flask_wtf import FlaskForm
from wtforms.validators import Required, NumberRange
from wtforms.fields import TextAreaField, SelectField
from wtforms.fields.html5 import IntegerField

RUN_TYPES = [(rt, rt) for rt in manager.RUN_TYPES]
PARAMS = json.dumps(conf.PARAMS, sort_keys=True, indent=4)
CONFIG = json.dumps(conf.RUN, sort_keys=True, indent=4)


class SimulationForm(FlaskForm):
    run_type = SelectField('Run Type', [Required()], choices=RUN_TYPES, default='run')
    n_runs = IntegerField('Number of runs per config', [Required(), NumberRange(min=0)], default=2)
    n_cpus = IntegerField('Number of cores to use', [Required()], default=2)
    params = TextAreaField('Parameters', [Required()], default=PARAMS)
    config = TextAreaField('Run config', [Required()], default=CONFIG)
    sensitivity_params = TextAreaField('Sensitivity Params', [Required()], default='WAGE_IGNORE_UNEMPLOYMENT\nALPHA:.04:.94:.1')
