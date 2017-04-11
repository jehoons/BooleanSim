from boolean3 import tokenizer,tokenizer_ws
from ipdb import set_trace
from os.path import basename,dirname
import numpy as np

tempcode="""
from numpy.random import random
import os, sys
import time
from ipdb import set_trace
from itertools import combinations, combinations_with_replacement
from cython.parallel import parallel, prange
from libc.stdlib cimport abort, malloc, free
import hashlib
import json


__start_time = 0

FP_LENGTH = 10

cdef detect_cycles( data ):
    fsize   = len(data)
    for msize in range(1, int(fsize/2) + 1):
        for index in range(fsize):
            left  = data[index:index+msize]
            right = data[index+msize:index+2*msize]
            if left == right:
                return index, msize

    return 0, 0

$MODELCODE$

def fp(s):
    res = hashlib.sha224(repr(s).encode('utf-8')).hexdigest()
    return res[0:FP_LENGTH]

def prettify(state_data, trajectory=False):
    if trajectory==False: 
        return "".join( ['%d'%s for s in state_data] )        
    else:
        traj_value = [] 
        for state in state_data: 
            state_str = []
            for st0 in state:
                state_str.append('%d' % st0)

            traj_value.append("".join(state_str))

        return "-".join(traj_value)

def main(steps, samples, debug, on_states, off_states):
    res = {}
    seen = {}
    traj = {}    
    for i in range(samples):
        values = simulate(steps=steps, on_states=on_states, off_states=off_states)
        idx, size = detect_cycles(values)

        if size == 1:
            attr_type = 'point'
        elif size > 1:
            attr_type = 'cyclic'
        elif size == 0:
            attr_type = 'unknown'
        else:        
            assert False        

        if attr_type == 'cyclic':
            cyc = values[idx : idx + size]
            head = sorted(cyc)[0]
            left = cyc[cyc.index(head) : len(cyc)]
            right = cyc[0 : cyc.index(head)]
            raw_attr = left + right 
            attr_id = fp(raw_attr)
            attr = [] 
        
            for state in raw_attr:
                fp_value = fp(state)
                attr.append(fp_value)
                seen[fp_value] = prettify(state, trajectory=False)
        else: # point
            raw_attr = values[-1]
            attr_id = fp(raw_attr)
            attr = attr_id
            seen[attr_id] = prettify(raw_attr, trajectory=False)
        
        if attr_id in res: 
            res[attr_id]['count'] += 1
        else: 
            res[attr_id] = {} 
            res[attr_id]['count'] = 1 
            res[attr_id]['type'] = attr_type
            res[attr_id]['value'] = attr
    
        res[attr_id]['ratio'] = float(res[attr_id]['count']) / float(samples)

        if debug: 
            if attr_type=='cyclic':
                has_trajectory=True
            else: 
                has_trajectory=False

            traj[i] = {
                'value': prettify(values, trajectory=True),
                'type': attr_type, 
                'attr': prettify(raw_attr, trajectory=has_trajectory)
                }

    result = {
        'attractors': res, 
        'state_key': seen, 
        'trajectory': traj, 
        'labels': $LABELS$
        }

    return result
"""

def gencode(text):

    lexer = tokenizer.Lexer() 
    tokens = lexer.tokenize_text( text )
    node_list = sorted(list( tokenizer.get_nodes(tokens) ))

    init_tokens = tokenizer.init_tokens(tokens)
    update_tokens = tokenizer.update_tokens(tokens)

    ic_nodes = [] 
    for it in init_tokens:
        ic_nodes.append( it[0].value )

    update_nodes = [] 
    for it in update_tokens:
        update_nodes.append( it[0].value )        
    
    not_in_ic = [x for x in set(node_list) - set(ic_nodes)]
    not_in_update = [x for x in set(node_list) - set(update_nodes)]
    
    node_info = {
        'update_nodes': update_nodes,  
        'ic_nodes': ic_nodes, 
        'all_nodes': node_list,
        'not-in-ic': not_in_ic,
        'not-in-update': not_in_update,
        }
        
    if not_in_ic != []: 
        print('nodes not initialized:')
        print(not_in_ic)
        assert False

    if not_in_update != []: 
        print('nodes not updated:')
        print(not_in_update)

    output_str = ''
    output_str += 'DEF num_nodes = %d\n' % len(node_list)
    output_str += 'ctypedef int (*cfptr)(int*)\n' 
    output_str += 'cdef cfptr eqlist[num_nodes]\n\n'

    remainer_node_ids = [i for i in range(0, len(node_list))]

    for it in update_tokens: 
        strout = '' 
        idx = node_list.index( it[0].value ) 
        remainer_node_ids.remove(idx)
        for i,el in enumerate(it): 
            if el.type=='ID':
                if i==0:
                    strout += 'state_%d'%node_list.index( el.value ) 
                else: 
                    strout += 'state[%d]'%node_list.index( el.value ) 
            elif el.type=='STATE': 
                if el.value=='Random':
                    strout += 'random()>0.5'
                else: 
                    strout += el.value
            elif el.type == 'AND' or el.type == 'OR' or el.type == 'NOT':
                strout += ' '+el.value+' '
            elif el.type == 'LPAREN' or el.type == 'RPAREN':
                strout += el.value
            elif el.type == 'ASSIGN':
                continue
            elif el.type == 'NUMBER':
                if el.value >= 0.0: 
                    strout += 'True'
                else: 
                    strout += 'False'
            else:
                strout += el.value
        
        output_str += 'cdef int __bool_fcn_%d(int state[]):\n' % idx
        output_str += '    %s\n' % strout
        output_str += '    return state_%d\n\n' % idx

    for idx in remainer_node_ids:
        output_str += 'cdef int __bool_fcn_%d(int state[]):\n' % idx
        output_str += '    state_%d = state[%d]\n' % (idx, idx)
        output_str += '    return state_%d\n\n' % idx
 
    for i in range(len(node_list)): 
        output_str+= 'eqlist[%d] = &__bool_fcn_%d\n' % (i,i)            

    output_str+='\ncdef int state0[num_nodes]\n'
    output_str+='cdef int state1[num_nodes]\n\n'

    output_str+='def simulate(steps=10, on_states=[], off_states=[]):\n'
    output_str+='    node_list = %s\n' % repr(node_list)

    # initial_values 
    for it in init_tokens: 
        strout = '' 
        idx = node_list.index( it[0].value ) 
        for el in it: 
            if el.type=='ID':
                strout += 'state0[%d]'%node_list.index( el.value ) 
            elif el.type=='STATE': 
                if el.value=='Random':
                    strout += 'random()>0.5'
                else: 
                    strout += el.value
            else: 
                strout += el.value

        output_str+= '    ' + strout + '\n'

    # Previous version is 3sec. 
    output_str+= '    on_idxes = [ node_list.index(s) for s in on_states]\n'
    output_str+= '    off_idxes = [ node_list.index(s) for s in off_states]\n'

    output_str+= '    state_list = []\n'
    output_str+= '    state_list.append(state0)\n\n'
    output_str+= '    for i in range(steps):\n'    
    output_str+= '        for k in on_idxes:\n'
    output_str+= '            state1[k] = True\n'
    output_str+= '        for k in off_idxes:\n'    
    output_str+= '            state1[k] = False\n'
    output_str+= '        for k in range(num_nodes):\n'
    output_str+= '            state1[k] = eqlist[k](state0)\n'
    output_str+= '        for k in range(num_nodes):\n'
    output_str+= '            state0[k] = state1[k]\n'
    output_str+= '        state_list.append(state0)\n\n'
    output_str+= '    return state_list\n'
    
    return output_str, node_list

def gencode_ws(text):

    lexer = tokenizer_ws.Lexer() 
    tokens = lexer.tokenize_text( text )
    node_list = sorted(list( tokenizer_ws.get_nodes(tokens) ))

    init_tokens = tokenizer_ws.init_tokens(tokens)
    update_tokens = tokenizer_ws.update_tokens(tokens)

    ic_nodes = [] 
    for it in init_tokens:
        ic_nodes.append( it[0].value )

    update_nodes = [] 
    for it in update_tokens:
        update_nodes.append( it[0].value )

    not_in_ic = [x for x in set(node_list) - set(ic_nodes)]
    not_in_update = [x for x in set(node_list) - set(update_nodes)]

    node_info = {
        'update_nodes': update_nodes,  
        'ic_nodes': ic_nodes, 
        'all_nodes': node_list,
        'not-in-ic': not_in_ic,
        'not-in-update': not_in_update,
        }
        
    if not_in_ic != []: 
        print('nodes not initialized:')
        print(not_in_ic)
        assert False

    if not_in_update != []: 
        print('nodes not updated:')
        print(not_in_update)

    output_str = ''
    output_str = 'sign = lambda x: True if x > 0 else False\n'
    output_str += 'DEF num_nodes = %d\n' % len(node_list)
    output_str += 'ctypedef int (*cfptr)(int*)\n' 
    output_str += 'cdef cfptr eqlist[num_nodes]\n\n'

    remainer_node_ids = [i for i in range(0, len(node_list))]

    for it in update_tokens: 
        strout = '' 
        idx = node_list.index( it[0].value ) 
        remainer_node_ids.remove(idx)
        # set_trace()
        for i,el in enumerate(it): 
            if el.type=='ID':
                if i==0:
                    strout += 'state_%d'%node_list.index( el.value ) 
                else: 
                    strout += 'state[%d]'%node_list.index( el.value ) 
            elif el.type=='STATE': 
                if el.value=='Random':
                    strout += 'random()>0.5'
                else: 
                    strout += el.value
            elif el.type == 'PLUS' or el.type == 'MINUS' or el.type == 'TIMES':
                strout += el.value
            elif el.type == 'ASSIGN':
                strout += '='
            elif el.type == 'NUMBER':
                if el.value >= 0: 
                    strout += '+%f' % el.value
                else: 
                    strout += '%f' % el.value
            elif el.type == 'LPAREN' or el.type == 'RPAREN':
                strout += el.value
            elif el.type == 'SIGN':
                strout += el.value
            else: 
                strout += el.value
        
        it_types = [it0.type for it0 in it]        

        output_str += 'cdef int __bool_fcn_%d(int state[]):\n' % idx        
        output_str += '    # %s\n' % repr(it)        
        output_str += '    %s\n' % strout

        if 'SIGN' not in it_types:
            output_str += '    return sign(state_%d)\n\n' % idx
        else: 
            output_str += '    return state_%d\n\n' % idx

    for idx in remainer_node_ids:
        output_str += 'cdef int __bool_fcn_%d(int state[]):\n' % idx
        output_str += '    state_%d = sign(state[%d])\n' % (idx, idx)
        output_str += '    return state_%d\n\n' % idx
 
    for i in range(len(node_list)): 
        output_str+= 'eqlist[%d] = &__bool_fcn_%d\n' % (i,i)            

    output_str+='\ncdef int state0[num_nodes]\n'
    output_str+='cdef int state1[num_nodes]\n\n'

    output_str+='def simulate(steps=10, on_states=[], off_states=[]):\n'
    output_str+='    node_list = %s\n' % repr(node_list)

    # # initial_values 
    for it in init_tokens: 
        strout = '' 
        idx = node_list.index( it[0].value ) 
        for el in it: 
            if el.type=='ID':
                strout += 'state0[%d]'%node_list.index( el.value ) 
            elif el.type=='STATE': 
                if el.value=='Random':
                    strout += 'random()>0.5'
                else: 
                    strout += el.value
            else: 
                strout += el.value
        output_str+= '    ' + strout + '\n'

    # output_str+= '    for node in node_list:\n'
    # output_str+= '        if initial_condition[node] == \'True\':\n'
    # output_str+= '            idx = node_list.index(node)\n'
    # output_str+= '            state0[idx] = True\n'
    # output_str+= '        elif initial_condition[node] == \'False\':\n'
    # output_str+= '            idx = node_list.index(node)\n'
    # output_str+= '            state0[idx] = False\n'
    # output_str+= '        elif initial_condition[node] == \'Random\':\n'
    # output_str+= '            idx = node_list.index(node)\n'
    # output_str+= '            state0[idx] = random()>0.5\n'
    # output_str+= '        else:\n'
    # output_str+= '            assert False\n'

    # Previous version is 3sec. 
    output_str+= '    on_idxes = [ node_list.index(s) for s in on_states]\n'
    output_str+= '    off_idxes = [ node_list.index(s) for s in off_states]\n'

    output_str+= '    state_list = []\n'
    output_str+= '    state_list.append(state0)\n\n'
    output_str+= '    for i in range(steps):\n'
    output_str+= '        for k in range(num_nodes):\n'
    output_str+= '            state1[k] = eqlist[k](state0)\n'
    output_str+= '        for k in on_idxes:\n'
    output_str+= '            state1[k] = True\n'
    output_str+= '        for k in off_idxes:\n'    
    output_str+= '            state1[k] = False\n'
    output_str+= '        for k in range(num_nodes):\n'
    output_str+= '            state0[k] = state1[k]\n'
    output_str+= '        state_list.append(state0)\n\n'
    output_str+= '    return state_list\n'
    
    return output_str, node_list


def build(text, pyx='engine.pyx', weighted_sum=False):

    if weighted_sum == False: 
        modelcode, node_list = gencode(text)
    else: 
        modelcode, node_list = gencode_ws(text)

    result = tempcode.replace('$MODELCODE$', modelcode)
    result = result.replace('$LABELS$', repr(node_list))
    with open(pyx, 'w') as f:
        f.write(result)


def parallel(pyxengine, steps=100, samples=1000, repeats=10, on_states=[], off_states=[]):
    ''' trajectories would not be correct '''    
    from multiprocessing import Pool,cpu_count

    p = Pool(cpu_count())

    args = (steps, samples, False, on_states, off_states)
    
    args_list = []
    
    for i in range(repeats):
        args_list.append(args)

    results = p.starmap(pyxengine.main, args_list)
    
    p.close(); p.join()

    reduced = {'attractors':{}, 'labels':{}, 'trajectory':{}, 'state_key':{}}

    for res in results:
        for att in res['attractors']: 
            if att not in reduced['attractors']: 
                reduced['attractors'][att] = res['attractors'][att]
            else: 
                reduced['attractors'][att]['count'] += res['attractors'][att]['count']

    reduced['labels'] = results[0]['labels']
    reduced['trajectory'] = results[0]['trajectory']
    reduced['state_key'] = results[0]['state_key']
    
    count = [reduced['attractors'][att]['count'] \
            for att in reduced['attractors']]

    for att in reduced['attractors']: 
        reduced['attractors'][att]['ratio'] =  \
            reduced['attractors'][att]['count']/np.sum(count)
            
    reduced['parameters'] = {
        'samples': int(np.sum(count)),
        'steps': steps, 
        }

    return reduced


# def run(samples=10, steps=10, debug=True, on_states=[], off_states=[]): 
#     import engine    
#     result = engine.main(steps, samples, debug, on_states, off_states)
#     result['parameters'] = {
#         'samples': samples,
#         'steps': steps
#         }
#     return result

