"""
Manages a running simulation.

This launches the simulation as a subprocess
and tracks it with a pidfile.
"""

import os
import psutil
import signal
import tempfile
import subprocess

TMP_DIR = tempfile.gettempdir()
LOG_FILE = os.path.join(TMP_DIR, 'seal.log')
PID_FILE = os.path.join(TMP_DIR, 'seal.pid')

# maps run types to required kwargs
RUN_TYPES = ['run', 'sensitivity', 'distributions', 'acps']

# need to handle subprocesses differently on windows
WINDOWS = os.name == 'nt'


def start(run_type, n_runs=1, n_cores=-2, **kwargs):
    """run the simulation as a subprocess,
    which makes it easier to manage"""

    if is_running():
        raise Exception('Simulation is already running.')

    if run_type not in RUN_TYPES:
        raise Exception('Not a valid run type: "{}".'.format(run_type))

    if run_type == 'sensitivity':
        params = [s.strip() for s in kwargs['sensitivity_params'].split('\n') if s.strip()]
    else:
        params = []

    cmd = [
        'python',
        'main.py',
        '-n', str(n_runs),
        '-c', str(n_cores),
        '-p', kwargs['params'],
        '-r', kwargs['config'],
        run_type
    ]
    cmd.extend(params)
    with open(LOG_FILE, 'w+') as f:
        kwargs = {
            'stdout': f,
            'stderr': subprocess.STDOUT,
        }
        if WINDOWS:
            kwargs['creationflags'] = subprocess.CREATE_NEW_PROCESS_GROUP
        else:
            kwargs['preexec_fn'] = os.setsid
        ps = subprocess.Popen(cmd, **kwargs)
    with open(PID_FILE, 'w') as f:
        f.write(str(ps.pid))


def get_pid():
    """gets pid of running simulation process"""
    try:
        return int(open(PID_FILE, 'r').read().strip())
    except FileNotFoundError:
        return None


def get_logs():
    with open(LOG_FILE, 'r') as f:
        return f.read().strip().split('\n')


def is_running():
    """check if the simulation is running by pid.
    assumes that the pid has successfully be written to the pid file."""
    pid = get_pid()
    if pid is None:
        return False

    # <https://stackoverflow.com/a/568285>
    try:
        os.kill(pid, 0)
    except OSError:
        return False
    else:
        proc = psutil.Process(pid)
        return proc.status() != psutil.STATUS_ZOMBIE


def stop():
    """kills running simulation process"""
    pid = get_pid()
    if pid is None:
        return
    if WINDOWS:
        os.kill(pid, signal.CTRL_BREAK_EVENT)
    else:
        os.killpg(os.getpgid(pid), signal.SIGTERM)  #or signal.SIGKILL
    os.remove(PID_FILE)
