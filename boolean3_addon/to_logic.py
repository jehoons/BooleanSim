# -*- coding: utf-8 -*-
#*************************************************************************
# Author: {Je-Hoon Song, <song.je-hoon@kaist.ac.kr>
#
# This file is part of {sbie_optdrug}.
#*************************************************************************

""" This module should be executed from python 3.5 
This module changes 'z = sign(x+y-1)' to logical equation. """

import re
import sys
import itertools
from pyeda.inter import *
from ipdb import set_trace
from sympy import And, Or, Not, symbols


def get_variables(rule): 
    found = re.findall('[A-Za-z_][_A-Za-z0-9]*', rule)
    variables = [] 
    for v in found:
        if v not in ['sign']: 
            variables.append(v)

    return variables


def compute_truth_table(rule, tt, variables):
    def sign(x):
        if x > 0:
            return 1
        else: 
            return 0

    output_list = [] 
    for var_assignment in tt: 
        expression = repr(tuple(variables)).replace('\'', '') + '=' + \
            repr(var_assignment)
        exec(expression)

        if rule=='sign(+State_p53+State_Mdm2−1)':
            set_trace()

        try:
            __y = eval(rule)
        except: 
            print('error in ', rule)
            assert False 
            
        output_list.append(str(__y))

    return output_list


def engine_rule2logic(rule):
    variables = get_variables(rule)
    tt = [i for i in itertools.product([0,1], repeat=len(variables))]
    # set_trace()
    if variables == []:
        if rule == '1':
            boolvalue = 'True'
        elif rule == '0': 
            boolvalue = 'False'
        elif rule == 'True': 
            boolvalue = 'True'
        elif rule == 'False': 
            boolvalue = 'False'
        else: 
            assert False 

        return boolvalue, boolvalue, variables, None, None, boolvalue

    output_list = compute_truth_table(rule, tt, variables)

    tt_f = truthtable(ttvars('x', len(variables)), "".join(output_list))

    sop = [] 
    for i,output in enumerate(output_list):
        if output == '1': 
            args = tt[i]
            lbls = []
            for i,arg in enumerate(args):
                if arg == 1:
                    lbls.append(variables[i])
                else: 
                    lbls.append('not ' + variables[i])

            sop.append(" and ".join(lbls))

    # print ( 'sop: ' + repr(sop))
    sop_eqns = " or ".join(sop)

    # set_trace();

    f_minimized = espresso_tts(tt_f)
    str_f_min = repr(f_minimized[0])
    for i in range(len(variables)): 
        str_f_min = str_f_min.replace('x[%d]'%(len(variables)-1-i), \
            variables[i])

    for var in variables:
        cmd = '%s = symbols(\'%s\')' % (var, var)
        exec(cmd)
        
    from sympy import And, Or, Not, Xor, printing 

    # if len(variables) > 4: 
    #     set_trace()

    cstr = repr( eval('printing.ccode(%s)' % str_f_min) )
    cstr = cstr.replace('&&', 'and')
    cstr = cstr.replace('||', 'or')
    cstr = cstr.replace('!', 'not ')
    cstr = cstr.replace('\'', '')
    
    return rule, cstr, variables, tt, output_list, sop_eqns


def run(txtdata, short=False):
    eq_lines = txtdata.split('\n')
    output_str = '' 
    for k, eq in enumerate(eq_lines): 
        eq = eq.strip()
        if eq == '':
            continue

        words = eq.split('*=')
        words[0]=words[0].strip()
        words[1]=words[1].strip()
        res0, res1, varlist, tt, y, sop_eqns = engine_rule2logic(words[1])
        
        if short == False: 
            output_str += '# source: ' + words[0] + ' *= ' + res0 + '\n'
            output_str += '# input: ' + ",".join(varlist) + '\n'
            output_str += '# output: ' + words[0] + '\n'
            output_str += '# table: ' + '\n'

            if tt != None: 
                for j, row in enumerate(tt):
                    lhs_ = ",".join( ['%d' % r for r in row] )
                    output_str += '# '+lhs_ + ' | ' + str(y[j]) + '\n'

            else:  
                output_str += '# N/A' + '\n'

            output_str += '# SOP: ' + words[0] + ' *= ' + sop_eqns + '\n'
            output_str += words[0] + ' *= ' + res1 + '\n'
            

        else: 
            output_str += words[0] + ' *= ' + res1 + '\n'

    return output_str


def build(txtdata, short=True):
    lines = txtdata.split('\n')
    ic_lines = [] 
    update_lines = [] 
    for thisline in lines:
        thisline = thisline.strip()
        if thisline == '': 
            continue
        if thisline.find('*=') > 0: 
            update_lines.append(thisline) 
        else:
            ic_lines.append(thisline)

    res = run("\n".join(update_lines), short=short)

    return "\n".join(ic_lines) + '\n' + res 


def test():
    txtdata = """
    a = False
    b = True
    a *= a 
    b *= sign(a+b-1)
    """
    res = build(txtdata, short=False)

    print(res)

