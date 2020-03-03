import conf
import tempfile
from simulation import Simulation


def check(label, cond):
    res = 'PASS' if cond(sim) else 'FAIL'
    print(res, label)


print('Verifying...')

# Keep it short
conf.RUN['TOTAL_DAYS'] = 100

path = tempfile.gettempdir()
sim = Simulation(conf.PARAMS, path)
sim.initialize()

N_HOUSES = len(sim.houses)

sim.run()

check('Construction increases housing supply', lambda sim: len(sim.houses) > N_HOUSES)
check('Bank is loaning money', lambda sim: sim.central.n_loans() > 0)
