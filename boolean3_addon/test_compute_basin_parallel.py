import json
from os.path import exists
from boolean3_addon import attr_cy, to_logic
import numpy as np
from pdb import set_trace


def test_this():
    modeltext = '''
    A= Random
    B= Random
    C= Random
    A*= sign(A + B + C)
    B*= sign(A + B + 2*C - 1)
    C*= sign(A + B - C)
    '''

    attr_cy.build(modeltext, pyx='engine_ws.pyx', weighted_sum=True)
    import pyximport; pyximport.install()
    import engine_ws

    res = attr_cy.parallel(engine_ws, steps=100, samples=10000, repeats=1000, \
            on_states=[], off_states=[])

    json.dump(res, open('res_compute_basin_parallel.json', 'w'), indent=4)


