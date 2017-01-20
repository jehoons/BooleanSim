# BooleanSim

BooleanSim은 Albert라는 사람이 개발한 이진네트워크 시뮬레이터인 [boolean2](https://github.com/ialbert/booleannet)를 python 3에서도 실행이 가능하도록 개선한 것입니다. python 3에서 실행되도록 하기 위해 [2to3.py](https://docs.python.org/3.0/library/2to3.html)와 [ply](http://www.dabeaz.com/ply)를 이용하였습니다.

### Installation

```
git clone git@github.com:jehoons/BooleanSim.git
cd BooleanSim 
python setup.py install 
```

### Test

다음과 같이 간단한 모델에 대해서 시뮬레이션을 실행해 볼 수 있습니다. 

```python
import pickle 
from pdb import set_trace
from boolean3 import Model

def test_hello():
    text = """
    # initial values
    A = True
    B = Random
    C = Random
    # updating rules
    B* = A
    C* = B
    """
    model = Model( text=text, mode='sync')
    model.initialize()
    model.iterate( steps=10, repeat=1)
    
    for state in model.states:
        print (state.A, state.B, state.C)
```

