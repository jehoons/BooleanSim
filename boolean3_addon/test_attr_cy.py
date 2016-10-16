import json
from boolean3_addon import attr_cy

def test_this():
    text  = '''
    A= Random
    B= Random
    C= Random
    A*= A or C
    B*= A and C
    C*= not A or B
    '''

    attr_cy.build(text, on_states=['A'])
    res = attr_cy.run(samples=1000, steps=30, debug=False)

    json.dump(res, open('output.json', 'w'), indent=4)

