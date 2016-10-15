import json
from boolean3_addon import attr_cy

def test_this():
    text  = '''
    A= Random
    B= True
    A*= not B
    B*= False
    '''

    attr_cy.build(text)
    res = attr_cy.run(samples=100, steps=30, debug=False)

    json.dump(res, open('output.json', 'w'), indent=4)

