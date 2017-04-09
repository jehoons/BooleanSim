import json
from os.path import exists
from boolean3_addon import attr_cy

def test_this_1():
    modeltext = '''
    A= Random
    B= Random
    C= Random
    A*= A or C
    B*= A and C
    C*= not A or B
    '''
    attr_cy.build(modeltext)

    import pyximport; pyximport.install()

    res = attr_cy.run(samples=1, steps=50, debug=False, on_states=['A'], \
        progress=True)

    json.dump(res, open('test_attr_cy.json', 'w'), indent=4)

from pdb import set_trace
def test_this_2():

    modeltext = '''
    A= Random
    B= Random
    C= Random
    A*= sign(A + B + C)
    B*= sign(A + B + 2*C - 1)
    C*= sign(A + B - C)
    '''
    
    attr_cy.build(modeltext, weighted_sum=True)
    
    import pyximport; pyximport.install()
    
    res = attr_cy.run(samples=10000, steps=50, debug=False, on_states=['A'])
    
    set_trace()

    json.dump(res, open('test_attr_cy.json', 'w'), indent=4)

