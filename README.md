# BooleanSim

BooleanSim은 Albert라는 사람이 개발한 이진네트워크 시뮬레이터인 [boolean2](https://github.com/ialbert/booleannet)를 python 3에서도 실행이 가능하도록 개선하고 몇개의 편리한 기능을 추가한 것입니다. python 3에서 실행되도록 하기 위해 [2to3.py](https://docs.python.org/3.0/library/2to3.html)와 [ply](http://www.dabeaz.com/ply)를 이용하였습니다.

BooleanSim은 boolean3와 boolean3_addon 모듈로 구성됩니다. boolean3는 Albert의 시뮬레이터와 동일하며 boolean3_addon에서는 boolean network의 basin크기를 추정하는 기능이 포함되어 있습니다.

### Installation

```
git clone git@github.com:jehoons/BooleanSim.git
cd BooleanSim 
python setup.py install 
```

### Test - Hello 

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

### Test - Basin크기 추정하기 

```python 
import json
from ipdb import set_trace
from boolean3 import Model
from boolean3_addon import attractor

def test_find_attractors():
    text = """
    A = True
    B = Random
    C = Random
    D = Random

    B* = A or C
    C* = A and not D
    D* = B and C
    """

    model = Model( text=text, mode='sync')
    res = attractor.find_attractors(model=model, steps=100, sample_size=10)

    outputfile = 'output.json'
    json.dump(res, open(outputfile, 'w'), indent=1)
```