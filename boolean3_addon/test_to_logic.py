import boolean3_addon 
from boolean3_addon import to_logic

def test_1():
    
    txtdata = """
    a = False
    b = True
    a *= a 
    b *= sign(a+b-1)
    """
    res = to_logic.build(txtdata, short=False)

    print(res)


def test_2():
    
    txtdata = """
    y *= sign(x+y+z+w-3)
    """
    res = to_logic.build(txtdata, short=False)

    print(res)

