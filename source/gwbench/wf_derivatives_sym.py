# Copyright (C) 2020  Ssohrab Borhanian
# 
# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation; either version 2 of the License, or
# (at your option) any later version.
# 
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
# 
# You should have received a copy of the GNU General Public License along
# with this program; if not, write to the Free Software Foundation, Inc.,
# 51 Franklin Street, Fifth Floor, Boston, MA 02110-1301 USA.


'''This module contains two methods that calculate the lambdified functions
of the the derivatives as well as of the function/expression itself.

 Input:  sympy function/expression, string of variables, boolean that determines
         if the function/expression has one (hf) or two (hfp, hfc) outputs.
 Output: dictionary that contains the lambdified functions:
         output['hf'] / output['hfp'], output['hfc']
         output['del_x_hf'] / output['del_x_hfp'], output['del_x_hfc']
           (x being the variable wrt which the derivative was taken)

 Disclaimer: These methods can be used on any sympy functions/expressions
             that have one or two outputs only (labels are set with
             gravitational waveforms in mind.
'''

from sympy import symbols, lambdify, diff

# hf is a sympy expression
def part_deriv_hf_expr(hf, symbols_string, deriv_symbs_string=None, pl_cr=0, label='hf'):
    symb_dic = {}

    for name in symbols_string.split(' '):
        symb_dic[name] = symbols(name,real=True)

    symb_list = list(symb_dic.values())

    if deriv_symbs_string == None:
        deriv_symbs_list = list(symb_dic.keys())
    else:
        deriv_symbs_list = deriv_symbs_string.split(' ')

    if pl_cr:
        lamdified_dic = {}
        for name in deriv_symbs_list:
            if name == 'f': continue

            key_string = 'del_'+name+'_'+label+'p'
            lamdified_dic[key_string] = lambdify(symb_list, diff(hf[0],symb_dic[name]), modules='numpy')

            key_string = 'del_'+name+'_'+label+'c'
            lamdified_dic[key_string] = lambdify(symb_list, diff(hf[1],symb_dic[name]), modules='numpy')

    else:
        lamdified_dic = {}
        for name in deriv_symbs_list:
            if name == 'f': continue

            key_string = 'del_'+name+'_'+label
            lamdified_dic[key_string] = lambdify(symb_list, diff(hf,symb_dic[name]), modules='numpy')

    return lamdified_dic
