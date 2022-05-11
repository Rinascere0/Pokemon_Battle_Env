import copy
from lib.const import *


def gen_z_move(move):
    sk_ctg = move['category']
    if sk_ctg == 'Status':
        z_move = copy.deepcopy(move)
        z_move['is_z_move'] = True
    else:
        sk_type = move['type']
        sk_name = Z_MOVES[sk_type]
        power = move['basePower']
        if power <= 55:
            power = 100
        elif power <= 65:
            power = 120
        elif power <= 75:
            power = 140
        elif power <= 85:
            power = 160
        elif power <= 95:
            power = 175
        elif power == 100:
            power = 180
        elif power == 110:
            power = 185
        elif power <= 125:
            power = 190
        elif power == 130:
            power = 195
        else:
            power = 200

        if move['name'] == 'Mega Drain':
            power = 120
        elif move['name'] == 'Weather Ball':
            power = 160
        elif move['name'] == 'Hex':
            power = 160
        elif move['name'] == 'Gear Grind':
            power = 180
        elif move['name'] == 'V-create':
            power = 220
        elif move['name'] == 'Flying Press':
            power = 170
        elif move['name'] == 'Core Enforcer':
            power = 140
        elif 'ohko' in move:
            power = 180

        z_move = {'name': sk_name, 'origin_name': move['name'], 'basePower': power, 'type': sk_type, 'accuracy': True,
                  'category': sk_ctg, 'priority': 0,
                  'flags': {}, 'target': 'common', 'is_z_move': True}
    return z_move


# type related

def calc_type_buff(move, target):
    sk_name, sk_type = move['name'], move['type']
    type_buff = 1
    for attr in target.attr:
        type_buff *= get_attr_fac(sk_type, attr)

    if sk_name == 'Flying Press':
        for attr in target.attr:
            type_buff *= get_attr_fac(Attr.Flying, attr)

    if sk_name == 'Freeze Dry' and target.attr:
        type_buff *= 4
    return type_buff


def get_attr_fac(atk_type, def_type):
    return Attr_Mat[Attr_dict[atk_type], Attr_dict[def_type]]


def imm_poison(pkm):
    return 'Steel' in pkm.attr or 'Poison' in pkm.attr or pkm.ability == 'Immunity'


def imm_ground(pkm, env):
    return not pkm.vstatus[
        'smackdown'] and 'Flying' in pkm.attr or pkm.ability == 'Levitate' or pkm.item is 'Air Balloon' or pkm.vstatus[
               'magnetrise'] or pkm.vstatus['telekinesis'] or env.pseudo_weather['gravity']


# stat related

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


# key related

def move_to_key(move):
    return move.replace(' ', '').replace('-', '').replace('[', '').replace(']', '').replace('\'', '').lower()


def None2Zero(x):
    return 0 if x is None else float(x)


def gen_def_type(attr):
    type_prob = Attr_Mat[Attr_dict[attr]] < 1
    type_id = np.random.choice(np.arange(0, 19), p=type_prob / type_prob.sum())
    return list(Attr_dict.keys())[type_id]


def gen_atk_type(attr):
    return
