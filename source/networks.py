"""James Gardner, March 2022
using colours from https://flatuicolors.com/palette/us"""
from useful_functions import flatten_list

# colours pulled from B&S2022 using Inkscape
BS2022_SIX = dict(nets=[
    ['A+_H', 'A+_L', 'V+_V', 'K+_K', 'A+_I'],
    ['V+_V', 'K+_K', 'Voyager-CBO_H', 'Voyager-CBO_L', 'Voyager-CBO_I'],
    ['A+_H', 'A+_L', 'K+_K', 'A+_I', 'ET_ET1', 'ET_ET2', 'ET_ET3'],
    ['V+_V', 'K+_K', 'A+_I', 'CE2-40-CBO_C'],
    ['K+_K', 'A+_I', 'ET_ET1', 'ET_ET2', 'ET_ET3', 'CE2-40-CBO_C'],
    ['ET_ET1', 'ET_ET2', 'ET_ET3', 'CE2-40-CBO_C', 'CE2-40-CBO_S']],
    colours=['#8c510aff', '#bf812dff', '#dfc27dff', '#80cdc1ff', '#35978fff', '#01665eff'],
    label='BS2022-six')

# --- CE only ---
# - One in the US
CE_C = dict(nets=[
    ['CE2-40-CBO_C']],
    colours=['#2d3436'],
    label='CE_C')
# - One in the US, One in Australia
CE_CS = dict(nets=[
    ['CE2-40-CBO_C', 'CE2-40-CBO_S'],
    ['CE2-40-CBO_C', 'CE2-20-CBO_S'],
    ['CE2-40-CBO_C', 'CE2-20-PMO_S']],
    colours=['#0984e3', '#74b9ff', '#ff7675'],
    label='CE_CS')
# - Two in the US --> done in B&S2022 with VKI+
CE_CN = dict(nets=[
    ['CE2-40-CBO_C', 'CE2-40-CBO_N'],
    ['CE2-40-CBO_C', 'CE2-20-CBO_N'],
    ['CE2-40-CBO_C', 'CE2-20-PMO_N']],
    colours=['#0984e3', '#74b9ff', '#ff7675'],
    label='CE_CN')
# - Three (two in US, one in Aus)
CE_CNS = dict(nets=[
    ['CE2-40-CBO_C', 'CE2-20-CBO_N', 'CE2-40-CBO_S'],
    ['CE2-40-CBO_C', 'CE2-20-CBO_N', 'CE2-20-CBO_S'],
    ['CE2-40-CBO_C', 'CE2-20-CBO_N', 'CE2-20-PMO_S'],
    ['CE2-40-CBO_C', 'CE2-20-PMO_N', 'CE2-40-CBO_S'],
    ['CE2-40-CBO_C', 'CE2-20-PMO_N', 'CE2-20-CBO_S'],
    ['CE2-40-CBO_C', 'CE2-20-PMO_N', 'CE2-20-PMO_S']],
    colours=['#0984e3', '#74b9ff', '#ff7675', '#6c5ce7', '#a29bfe', '#fd79a8'],
    label='CE_CNS')

# --- CE_S with non-CE others ---
# - CE_S + A+ network
CE_S_AND_2G = dict(nets=[
    ['A+_H', 'A+_L', 'V+_V', 'K+_K', 'A+_I', 'CE2-40-CBO_S'],
    ['A+_H', 'A+_L', 'V+_V', 'K+_K', 'A+_I', 'CE2-20-CBO_S'],
    ['A+_H', 'A+_L', 'V+_V', 'K+_K', 'A+_I', 'CE2-20-PMO_S']],
    colours=['#00cec9', '#81ecec', '#fab1a0'],
    label='CE_S_and_2G')
# - CE_S + Voyager notework
CE_S_AND_VOYAGER = dict(nets=[
    ['V+_V', 'K+_K', 'Voyager-CBO_H', 'Voyager-CBO_L', 'Voyager-CBO_I', 'CE2-40-CBO_S'],
    ['V+_V', 'K+_K', 'Voyager-CBO_H', 'Voyager-CBO_L', 'Voyager-CBO_I', 'CE2-20-CBO_S'],
    ['V+_V', 'K+_K', 'Voyager-CBO_H', 'Voyager-CBO_L', 'Voyager-CBO_I', 'CE2-20-PMO_S']],
    colours=['#00cec9', '#81ecec', '#fab1a0'],
    label='CE_S_and_Voy') 
# - CE_S + ET, not yet examined, compare to CE_CN_AND_ET
CE_S_AND_ET = dict(nets=[
    ['ET_ET1', 'ET_ET2', 'ET_ET3', 'CE2-40-CBO_S'],
    ['ET_ET1', 'ET_ET2', 'ET_ET3', 'CE2-20-CBO_S'],
    ['ET_ET1', 'ET_ET2', 'ET_ET3', 'CE2-20-PMO_S']],
    colours=['#00cec9', '#81ecec', '#fab1a0'],
    label='CE_S_and_ET') 

# --- CE_CN with ET ---
CE_CN_AND_ET = dict(nets=[
    ['ET_ET1', 'ET_ET2', 'ET_ET3', 'CE2-40-CBO_C', 'CE2-40-CBO_N'],
    ['ET_ET1', 'ET_ET2', 'ET_ET3', 'CE2-40-CBO_C', 'CE2-20-CBO_N'],
    ['ET_ET1', 'ET_ET2', 'ET_ET3', 'CE2-40-CBO_C', 'CE2-20-PMO_N']],
    colours=['#00cec9', '#81ecec', '#fab1a0'],
    label='CE_CN_and_ET')

# --- H0 science case: A+_S to get sky localisation for the ~10 BNS this decade ---
NEMOLF_AND_2G = dict(nets=[
    ['A+_S', 'A+_H', 'A+_L', 'V+_V', 'K+_K', 'A+_I'],
    ['A+_S', 'A+_H', 'A+_L', 'V+_V', 'K+_K'],
    ['A+_S', 'A+_H', 'A+_L']],
    colours=['#00b894', '#55efc4', '#e17055'],
    label='NEMO-LF_and_2G')

# list of network sets (dicts) following meeting on 2022-03-17
NET_DICT_LIST = [
    BS2022_SIX,
    CE_C, CE_CS, CE_CN, CE_CNS,
    CE_S_AND_2G, CE_S_AND_VOYAGER, CE_S_AND_ET,
    CE_CN_AND_ET,
    NEMOLF_AND_2G
]
NET_LIST = flatten_list([net_dict['nets'] for net_dict in NET_DICT_LIST])
# look-up table: given net_spec return colour
DICT_NETSPEC_TO_COLOUR = dict()
for net_dict in NET_DICT_LIST:
    for net_spec in net_dict['nets']:
        DICT_NETSPEC_TO_COLOUR[repr(net_spec)] = net_dict['colours'][net_dict['nets'].index(net_spec)]
