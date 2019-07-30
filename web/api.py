from . import manager
from flask import Blueprint, jsonify

bp = Blueprint('api', __name__, url_prefix='/api')


@bp.route('/stop')
def stop():
    """stops a running simulation"""
    manager.stop()
    return jsonify(success=True)


@bp.route('/status')
def status():
    """returns info about any running simulations"""
    running = manager.is_running()
    logs = manager.get_logs() if running else []
    return jsonify(success=True, running=running, logs=logs)
