import json
from os.path import exists
from boolean3_addon import attr_cy, to_logic
import numpy as np 
from pdb import set_trace
import pytest


#def test_this_1():
#    modeltext = '''
#    A= Random
#    B= Random
#    C= Random
#    A*= A or C
#    B*= A and C
#    C*= not A or B
#    '''
#    attr_cy.build(modeltext, pyx='engine.pyx', weighted_sum=False)
#    import pyximport; pyximport.install()
#    import engine 
#
#    res = engine.main(50, 1, debug=False, on_states=['A'])
#    json.dump(res, open('test_attr_cy.json', 'w'), indent=4)


def test_this_2():
   
    steps = 50
    samples = 100000
    debug = False
    on_states = []
    off_states = []
    
    res = engine_ws.main(steps, samples, debug, on_states, off_states)    
    #res2 = engine.main(steps, samples, debug, on_states, off_states)    
    
    json.dump(res, open('res_ws.json', 'w'), indent=4)
    #json.dump(res2, open('res_logic.json', 'w'), indent=4)


modeltext = '''
A= Random
B= Random
C= Random
A*= sign(A + B + C)
B*= sign(A + B + 2*C - 1)
C*= sign(A + B - C)
'''
attr_cy.build(modeltext, pyx='engine_ws.pyx', weighted_sum=True)
#modeltext_logic = to_logic.build(modeltext) 
#print(modeltext_logic)
#attr_cy.build(modeltext_logic, pyx='engine.pyx', weighted_sum=False)

import pyximport; pyximport.install()        
import engine_ws, engine

# set_trace()



