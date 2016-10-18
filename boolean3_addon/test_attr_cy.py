import json
from os.path import exists
from boolean3_addon import attr_cy

modeltext = '''
A= Random
B= Random
C= Random
A*= A or C
B*= A and C
C*= not A or B
'''

if not exists('engine.pyx'):
    attr_cy.build(modeltext)

import pyximport; pyximport.install()

def test_this():
    res = attr_cy.run(samples=100000, steps=30, debug=False, on_states=['A'], \
        progress=True)
    json.dump(res, open('output.json', 'w'), indent=4)
