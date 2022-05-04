import numpy
import math
import random
from const import *


# from pokemon import Pokemon

def minus(x, y):
    if x < y:
        return 0
    else:
        return x - y


def move_to_key(move):
    return move.replace(' ', '').replace('-', '').replace('[', '').replace(']', '').replace('\'', '').lower()


def calc_type_buff(move, target):
    sk_name, sk_type = move['name'], move['type']
    type_buff = 1
    for attr in target.attr:
        type_buff *= get_attr_fac(sk_type, attr)

    if sk_name == 'Flying Press':
        for attr in target.attr:
            type_buff *= get_attr_fac(Attr.Flying, attr)

    if sk_name == 'Freeze Dry' and target.attr:
        # should be effective
        type_buff *= 4

    return type


def imm_ground(pkm):
    return 'Flying' in pkm.attr or pkm.ability == 'Levitate' or pkm.item is 'Air Balloon' and not pkm.vstatus[
        'roost'] and not pkm.vstatus['smackdown']


def gen_stats(sp, evs, ivs, lv, nature):
    stats = {}
    stats['HP'] = int((sp['hp'] * 2 + ivs['HP'] + evs['HP'] / 4) * lv / 100 + 10 + lv)
    for ID in ['Atk', 'Def', 'SpA', 'SpD', 'Spe']:
        stats[ID] = int((sp[ID.lower()] * 2 + ivs[ID] + evs[ID] / 4) * lv / 100 + 5)

    if nature in Nature:
        buf, deb = Nature[nature]

        stats[buf] = int(stats[buf] * 1.1)
        stats[deb] = int(stats[deb] * 0.9)

    return stats


def None2Zero(x):
    return 0 if x is None else float(x)


def get_ct(lv):
    if lv == 0:
        return 1 / 16
    elif lv == 1:
        return 1 / 8
    elif lv == 2:
        return 1 / 2
    else:
        return 1


def calc_stat_lv(lv):
    if lv >= 0:
        return (lv + 2) / 2
    else:
        return 2 / (2 - lv)


def get_attr_fac(atk_type, def_type):
    return Attr_Mat[Attr_dict[atk_type], Attr_dict[def_type]]
