import boolean3_addon 
from boolean3_addon import to_logic

def test():
    
    txtdata = """
    a = False
    b = True
    a *= a 
    b *= sign(a+b-1)
    """
    res = to_logic.build(txtdata, short=False)

    print(res)

