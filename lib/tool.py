from data.moves import Moves
from data.pokedex import pokedex
import numpy as np
from lib.functions import move_to_key, pkm_to_key, get_attr_fac, calc_stat_lv, get_ct
from lib.const import *


def gen_setting_from_import(user):
    ivs = {
        'HP': 31, 'Atk': 31, 'Def': 31, 'SpA': 31, 'SpD': 31, 'Spe': 31
    }
    evs = {
        'HP': 0, 'Atk': 0, 'Def': 0, 'SpA': 0, 'SpD': 0, 'Spe': 0
    }
    sp = pokedex[pkm_to_key(user['name'])]['baseStats']

    return sp, ivs, evs


def find_status_move(user, target, env, mask):
    total_moves = []
    for move_info in user['moves']:
        if mask[move_info['move_id']]:
            move_name = move_to_key(move_info['name'])
            move = Moves[move_name]
            if move['category'] == 'Status' and check_useful(user, target, move, env):
                total_moves.append(move_info)

    return total_moves


def check_utvs(user, target, env, mask):
    for move_info in user['moves']:
        if mask[move_info['move_id']] and move_info['name'] in ['U-Turn', 'Volt Switch']:
            name = move_to_key(move_info['name'])
            if check_useful(user, target, Moves[name], env):
                return move_info


def find_best_move(user, target, env, mask=None):
    best_move = None
    max_dmg = -1
    if mask is None:
        mask = np.ones(4)
    for move_info in user['moves']:
        if mask[move_info['move_id']]:
            move_name = move_to_key(move_info['name'])
            move = Moves[move_name]
            if check_useful(user, target, move, env):
                dmg = calc_dmg(user, target, move, env)
                if dmg > max_dmg:
                    best_move = move_info
                    max_dmg = dmg
    return best_move, max_dmg


def find_best_foe(user, team, env):
    foe = None
    min_dmg = 10000
    for pkm in team:
        _, dmg = find_best_move(user, pkm, env)
        if dmg < min_dmg:
            foe = pkm
            min_dmg = dmg
    return foe, min_dmg


def find_best_counter(team, target, env, except_pivot=True):
    max_dmg = 0
    best_pkm = None
    #  print('myalive:')
    for pkm in team:
        if except_pivot and pkm['is_pivot']:
            #         print('mypivot', pkm)
            continue
        if pkm['alive']:
            #        print(pkm)
            _, dmg = find_best_move(pkm, target, env)
            if dmg > max_dmg:
                best_pkm = pkm
                max_dmg = dmg
    # print(best_pkm)
    return best_pkm


def find_best_action(team, foe_team, pivot_id, foe_pivot_id, masks, env):
    pivot = team[pivot_id]
    foe_pivot = foe_team[foe_pivot_id]
    # greedy
    greedy_move, greedy_dmg = find_best_move(pivot, foe_pivot, env, masks['move'])
    greedy_switch = find_best_counter(team, foe_pivot, env)
    # predict
    best_foe, _ = find_best_foe(pivot, foe_team, env)
    predict_move, predict_dmg = find_best_move(pivot, best_foe, env, masks['move'])
    predict_switch = find_best_counter(team, best_foe, env)
    # random
    random_moves = find_status_move(pivot, foe_pivot, env, masks['move'])
    utvs = check_utvs(pivot, foe_pivot, env, masks['move'])

    def print_move():
        print(pivot['name'], foe_pivot['name'])
        print('movemask', masks['move'])
        print('greedy', greedy_move['name'], greedy_dmg)
        if greedy_switch:
            print('greedy switch', greedy_switch['name'], greedy_dmg)
        print('best foe', best_foe['name'])
        print('pred move', predict_move['name'], predict_dmg)
        if predict_switch:
            print('pred switch', predict_switch['name'])

    action_space = np.array([greedy_move, greedy_switch, predict_move, predict_switch, random_moves, utvs],
                            dtype=object)

    greedy_move_prob = 0.45 * (greedy_move is not None)
    if greedy_dmg < 100:
        greedy_move_prob /= 3
    greedy_switch_prob = 0.15 * (greedy_switch is not None and greedy_switch['id'] != pivot_id) * masks['switch']
    predict_move_prob = 0.15 * (predict_move is not None)
    if predict_dmg < 100:
        predict_move_prob /= 5
    predict_switch_prob = 0.1 * (predict_switch is not None and predict_switch['id'] != pivot_id) * masks['switch']
    random_moves_prob = 0.1 * (len(random_moves) > 0)
    utvs_prob = 0.15 * (utvs is not None)

    if utvs_prob:
        if greedy_switch_prob:
            utvs_prob += greedy_switch_prob / 2
            greedy_switch_prob /= 2
        if predict_switch_prob:
            utvs_prob += predict_switch_prob / 2
            predict_switch_prob /= 2
    prob = np.array(
        [greedy_move_prob, greedy_switch_prob, predict_move_prob, predict_switch_prob, random_moves_prob, utvs_prob])
    if prob.sum() == 0:
        return {'type': ActionType.Common, 'item': 0}
    prob = prob / prob.sum()

    action = np.random.choice(action_space, p=prob)
    if type(action) is list:
        action = np.random.choice(random_moves)
    if 'lv' in action:
        action = {'type': ActionType.Switch, 'item': action['id']}
    else:
        action_type = ActionType.Common
        move_id = action['move_id']
        if masks['mega']:
            action_type = ActionType.Mega
        else:
            if masks['z'][move_id]:
                action_type = ActionType.Z_Move
        action = {'type': action_type, 'item': move_id}

    return action


def find_best_switch(team, foe_team, pivot_id, foe_pivot_id, env, switch_type):
    pivot = team[pivot_id]
    foe_pivot = foe_team[foe_pivot_id]
    if foe_pivot['alive']:
        best_switch = find_best_counter(team, foe_pivot, env, except_pivot=True)
    else:
        best_switch = None
    best_foe, _ = find_best_foe(pivot, foe_team, env)
    if best_foe:
        predict_switch = find_best_counter(team, best_foe, env, except_pivot=True)
    else:
        predict_switch = None

    switch_space = np.array([best_switch, predict_switch])

    # predict work
    if switch_type == SwitchType.Common:
        p = [0.7, 0.3]
    # no need to predict
    elif best_switch:
        p = [1, 0]
    elif predict_switch:
        p = [0, 1]
    else:
        return {'type': ActionType.Switch, 'item': 0}

    switch = np.random.choice(switch_space, p=p)
    return {'type': ActionType.Switch, 'item': switch['id']}


def gen_action(obs):
    team = obs['my_team']
    foe_team = obs['foe_team']
    env = obs['env']
    return find_best_action(team['pkms'], foe_team['pkms'], team['pivot'], foe_team['pivot'], team['masks'], env)


def gen_switch(obs, switch_type):
    team = obs['my_team']
    foe_team = obs['foe_team']
    env = obs['env']
    return find_best_switch(team['pkms'], foe_team['pkms'], team['pivot'], foe_team['pivot'], env, switch_type)


def calc_stats(user, env, raw=False):
    HP, Atk, Def, Satk, Sdef, Spe = gen_stats(user).values()
    Atk_lv, Def_lv, Satk_lv, Sdef_lv, Spe_lv, Eva_lv, Acc_lv, _ = user['stat_lv'].values()
    if not raw:
        Atk *= calc_stat_lv(Atk_lv)
        Def *= calc_stat_lv(Def_lv)
        Satk *= calc_stat_lv(Satk_lv)
        Sdef *= calc_stat_lv(Sdef_lv)
        Spe *= calc_stat_lv(Spe_lv)
        Eva = calc_stat_lv(Eva_lv)
        Acc = calc_stat_lv(Acc_lv)

    ability = user['ability']
    status = user['status']
    vstatus = user['vstatus']

    pkm_info = pokedex[pkm_to_key(user['name'])]

    # Ability Buff
    if ability == 'Defeatist' and user['hp_perc'] < 1 / 2:
        Atk *= 0.5
        Satk *= 0.5
    if ability in ['Huge Power', 'Pure Power']:
        Atk *= 2
    if ability == 'Guts' and status:
        Atk *= 1.5
    if ability == 'Marvel Scale' and status:
        Def *= 1.5
    if ability == 'Quick Feet' and status:
        Spe *= 1.5
    #    if ability == 'Tangled Feet' and vstatus['confusion']:
    #        Eva *= 2
    if ability == 'Solar Power' and env['weather'] == 'sunnyday':
        Satk *= 2
    if ability == 'Chlorophyll' and env['weather'] == 'sunnyday':
        Spe *= 2
    if ability == 'Swift Swim' and env['weather'] == 'RainDance':
        Spe *= 2
    if ability == 'Sand Rush' and env['weather'] == 'Sandstorm':
        Spe *= 2
    if ability == 'Slush Rush' and env['weather'] == 'hail':
        Spe *= 2
    if ability == 'Snow Clock' and env['weather'] == 'hail':
        Eva *= 1.25
    if ability == 'Sand Veil' and env['weather'] == 'Sandstorm':
        Eva *= 1.25

    # Item Buff
    item = user['item']
    if item == 'Choice Band':
        Atk *= 1.5

    if item == 'Choice Specs':
        Satk *= 1.5

    if item == 'Choice Scarf':
        Spe *= 1.5

    if item == 'Assault Vest':
        Sdef *= 1.5

    if item == 'Eviolite' and 'evos' in pkm_info:
        Def *= 1.5
        Sdef *= 1.5

    return {'HP': HP, 'Atk': Atk, 'Def': Def, 'SpA': Satk, 'SpD': Sdef, 'Spe': Spe, 'Eva': Eva, 'Acc': Acc}


def gen_stats(user):
    lv = user['lv']
    sp, ivs, evs = gen_setting_from_import(user)
    stats = {'HP': int((sp['hp'] * 2 + ivs['HP'] + evs['HP'] / 4) * lv / 100 + 10 + lv)}
    for ID in ['Atk', 'Def', 'SpA', 'SpD', 'Spe']:
        stats[ID] = int((sp[ID.lower()] * 2 + ivs[ID] + evs[ID] / 4) * lv / 100 + 5)
    if 'nature' in user:
        buf, deb = Nature[user['nature']]
        stats[buf] = int(stats[buf] * 1.1)
        stats[deb] = int(stats[deb] * 0.9)
    return stats


def calc_dmg(user, target, move, env):
    foe_stats = calc_stats(target, env)

    belong = user['belong']

    target_hp = target['hp_perc'] * foe_stats['HP']

    sk_type = move['type']
    sk_name = move['name']
    ctg = move['category']
    flag = move['flags']
    power = move['basePower']

    if 'damage' in move:
        if move['damage'] == 'level':
            return user['lv']
        else:
            return int(move['damage'])

    if sk_name == 'Endeavor':
        return target_hp - user['hp']

    if sk_name == 'Nature\'s Madness':
        return max(target_hp // 2, 1)

    if sk_name == 'Knock Off':
        if target['item'] and target['item'] not in mega_stones and not (
                target['name'] == 'Arceus' and target['item'] in plates) and not (
                target['name'] == 'Silvally' and target['item'] in memories) and 'ium Z' not in target['item'] and not \
                target['vstatus']['substitute']:
            power *= 1.5

    if sk_name == 'Stored Power':
        for key, boost in user['stat_lv'].items():
            if boost > 0:
                power += boost * 20

    if sk_name == 'Return':
        power = 102

    if sk_name == 'Water Shuriken' and user['name'] == 'Greninja-Ash':
        power = 20

    if sk_name == 'Acrobatics' and user['item'] is None:
        power *= 2

    ''' 
    if sk_name in ['Low Kick', 'Grass Knot']:
        if target.weight < 10:
            power = 20
        elif 10 <= target.weight < 25:
            power = 40
        elif 25 <= target.weight < 50:
            power = 60
        elif 50 <= target.weight < 100:
            power = 80
        elif 100 <= target.weight < 200:
            power = 100
        else:
            power = 120
'''
    if sk_name in ['Heavy Slam', 'Heat Crash']:
        power = 120

    if sk_name == 'Electro Ball':
        ratio = user['Spe'] / foe_stats['Spe']
        if ratio < 1:
            power = 40
        elif ratio < 2:
            power = 60
        elif ratio < 3:
            power = 80
        elif ratio < 4:
            power = 120
        else:
            power = 150

    if sk_name == 'Gyro Ball':
        power = min(150, int(25 * foe_stats['Spe'] / user['Spe']))

    # type_buff
    type_buff = calc_type_buff(move, target)

    # physical/special
    if ctg == 'Physical':
        Atk = user['atk']
        Def = foe_stats['Def']
    else:
        Atk = user['spa']
        Def = foe_stats['SpD']

    if 'defensiveCategory' in move:
        if move['defensiveCategory'] == 'Physical':
            Def = foe_stats['Def']

    if sk_name == 'Foul Play':
        Atk = foe_stats['Atk']

    lv = user['lv']
    dmg = (2 * lv + 10) / 250 * Atk / Def * power + 2

    # 本系加成
    stab_buff = 1
    if sk_type in user['type']:
        if user['ability'] == 'Adaptability':
            stab_buff = 2
        else:
            stab_buff = 1.5

    # other
    other_buff = 1

    if sk_name in ['Triple Kick', 'Triple Axel']:
        other_buff *= 6

    # status buff
    if user['status'] is 'brn' and user['ability'] != 'Guts' and sk_name != 'Facade' and ctg == 'Physical':
        other_buff *= 0.5

    # skill buff
    if sk_name == 'Facade' and (user['status'] is not None):
        other_buff *= 2

    # ability buff

    if user['ability'] == 'Sheer Force':
        effects = None
        if 'secondary' in move:
            effects = move['secondary']
        elif 'secondaries' in move:
            effects = move['secondaries']
        if effects:
            other_buff *= 1.3

    if user['ability'] == 'Flare Boost' and user['status'] is 'brn' and ctg == 'Special':
        other_buff *= 1.5

    if user['ability'] == 'Toxic Boost' and user['status'] in ['tox', 'psn'] and ctg == 'Physical':
        other_buff *= 1.5

    # if user['ability'] == 'Flash Fire' and user.flash_fire and sk_type == 'Fire':
    #     other_buff *= 1.5

    if user['ability'] == 'Mega Launcher':
        if 'pulse' in flag:
            other_buff *= 1.5

    # if user['ability'] == 'Analytic' and last:
    #     other_buff *= 1.3

    if user['ability'] == 'Blaze' and user['hp'] <= user['maxhp'] / 3 and sk_type == 'Fire':
        other_buff *= 1.5

    if user['ability'] == 'Overgrow' and user['hp'] <= user['maxhp'] / 3 and sk_type == 'Grass':
        other_buff *= 1.5

    if user['ability'] == 'Torrent' and user['hp'] <= user['maxhp'] / 3 and sk_type == 'Water':
        other_buff *= 1.5

    if user['ability'] == 'Swarm' and user['hp'] <= user['maxhp'] / 3 and sk_type == 'Bug':
        other_buff *= 1.5

    if 'Dark Aura' in [user['ability'], target['ability']] and sk_type == 'Dark':
        other_buff *= 1.3

    if 'Fairy Aura' in [user['ability'], target['ability']] and sk_type == 'Fairy':
        other_buff *= 1.3

    if user['ability'] == 'Iron Fist' and 'Punch' in sk_name and sk_name != 'Sucker Punch':
        other_buff *= 1.2

    if user['ability'] == 'Neuroforce' and type_buff > 1:
        other_buff *= 1.25

    if user['ability'] == 'Reckless' and 'recoil' in flag:
        other_buff *= 1.2

    if user['ability'] == 'Rivalry' and user['gender'] in ['M', 'F'] and target['gender'] in ['M', 'F']:
        if user['gender'] == target['gender']:
            other_buff *= 1.25
        else:
            other_buff *= 0.75

    if user['ability'] == 'Sand Force' and env['weather'] == Weather.Sandstorm:
        if sk_type in ['Rock', 'Steel', 'Ground']:
            other_buff *= 1.3

    if user['ability'] == 'Strong Jaw' and 'bite' in flag:
        other_buff *= 1.5

    if user['ability'] == 'Technician' and power <= 60:
        other_buff *= 1.5

    if user['ability'] == 'Tinted Lens' and type_buff < 1:
        other_buff *= 2

    if user['ability'] == 'Tough Claws' and 'contact' in flag:
        other_buff *= 1.3

    if user['ability'] == 'Water Bubble' and sk_type == 'Water':
        other_buff *= 2

    # item buff
    if ctg == 'Physical' and user['item'] == 'Muscle Band':
        other_buff *= 1.1

    if ctg == 'Special' and user['item'] == 'Wise Glasses':
        other_buff *= 1.1

    if user['item'] == 'Expert Belt' and type_buff > 1:
        other_buff *= 1.2

    if user['item'] == 'Life Orb':
        other_buff *= 1.3

    if user['item'] == 'Normal Gem' and sk_type == 'Normal':
        other_buff *= 1.3

    if sk_type == 'Fire' and user['item'] in ['Flame Plate', 'Charcoal']:
        other_buff *= 1.2
    if sk_type == 'Grass' and user['item'] in ['Meadow Plate', 'Miracle Seed', 'Rose Incense']:
        other_buff *= 1.2
    if sk_type == 'Water' and user['item'] in ['Splash Plate', 'Mystic Water', 'Sea Incense', 'Wave Incense']:
        other_buff *= 1.2
    if sk_type == 'Ground' and user['item'] in ['Earth Plate', 'Soft Sand']:
        other_buff *= 1.2
    if sk_type == 'Bug' and user['item'] in ['Insect Plate', 'Silver Powder']:
        other_buff *= 1.2
    if sk_type == 'Ice' and user['item'] in ['Icicle Plate', 'Never-Melt Ice']:
        other_buff *= 1.2
    if sk_type == 'Steel' and user['item'] in ['Iron Plate', 'Metal Coat']:
        other_buff *= 1.2
    if sk_type == 'Fighting' and user['item'] in ['Fist Plate', 'Black Belt']:
        other_buff *= 1.2
    if sk_type == 'Psychic' and user['item'] in ['Mind Plate', 'Twisted Spoon', 'Odd Incense']:
        other_buff *= 1.2
    if sk_type == 'Flying' and user['item'] in ['Sky Plate', 'Sharp Beak']:
        other_buff *= 1.2
    if sk_type == 'Dark' and user['item'] in ['Dread Plate', 'Black Glasses']:
        other_buff *= 1.2
    if sk_type == 'Ghost' and user['item'] in ['Spooky Plate', 'Spell Tag']:
        other_buff *= 1.2
    if sk_type == 'Rock' and user['item'] in ['Stone Plate', 'Hard Stone', 'Rock Incense']:
        other_buff *= 1.2
    if sk_type == 'Electric' and user['item'] in ['Zap Plate', 'Magnet']:
        other_buff *= 1.2
    if sk_type == 'Poison' and user['item'] in ['Toxic Plate', 'Poison Barb']:
        other_buff *= 1.2
    if sk_type == 'Fairy' and user['item'] == 'Pixie Plate':
        other_buff *= 1.2
    if sk_type == 'Dragon' and user['item'] in ['Draco Plate', 'Dragon Fang']:
        other_buff *= 1.2
    if sk_type == 'Normal' and user['item'] == 'Silk Scarf':
        other_buff *= 1.2

    # berry buff
    if target['item'] in attr_berry and sk_type == attr_berry[target['item']] and type_buff > 1:
        other_buff *= 0.5

    if target['item'] == 'Chilan Berry' and sk_type == 'Normal':
        other_buff *= 0.5

    # env buff

    if not imm_ground(user, env) and env['terrain'] == 'psychicterrain' and sk_type == 'Psychic':
        other_buff *= 1.3

    if not imm_ground(user, env) and env['terrain'] == 'electricterrain' and sk_type == 'Electric':
        other_buff *= 1.3

    if not imm_ground(user, env) and env['terrain'] == 'grassyterrain' and sk_type == 'Grass':
        other_buff *= 1.3

    if not imm_ground(user, env) and env['terrain'] == 'grassyterrain' and sk_type == 'Ground':
        other_buff *= 0.5

    if not imm_ground(target, env) and env['terrain'] == 'mistyterrain' and sk_type == 'Dragon':
        other_buff *= 0.5

    if env['weather'] == 'sunnyday' and sk_type == 'Fire':
        other_buff *= 1.5

    if env['weather'] == 'RainDance' and sk_type == 'Water':
        other_buff *= 1.5

    if 'mudsport' in env['pseudo_weather'] and sk_type == 'Electric':
        other_buff *= 0.5

    if 'watersport' in env['pseudo_weather'] and sk_type == 'Fire':
        other_buff *= 0.5

    # Defence Buff
    if target['ability'] == 'Fluffy':
        if sk_type == 'Fire':
            other_buff *= 2
        if 'contact' in flag:
            other_buff *= 0.5

    if target['ability'] == 'Thick Fat':
        if sk_type in ['Ice', 'Fire']:
            other_buff *= 0.5

    if target['ability'] == 'Water Bubble' and sk_type == 'Fire':
        other_buff *= 0.5

    if target['ability'] == 'Dry Skin':
        if sk_type == 'Fire':
            other_buff *= 1.25

    if target['ability'] == 'Heatproof':
        if sk_type == 'Fire':
            other_buff *= 0.5
    if target['ability'] in ['Prism Armor', 'Filter', 'Solid Rock'] and type_buff > 1:
        other_buff *= 0.75

    if target['ability'] in ['Shadow Shield', 'Multiscale'] and target['hp_perc'] == 1:
        other_buff *= 0.5

    target_sidecond = env['sidecond'][belong]
    if user['ability'] != 'Infiltrator' and sk_name != 'ConfusionHit':
        if target_sidecond['lightscreen'] and ctg == 'Special':
            other_buff *= 0.5
        if target_sidecond['reflect'] and ctg == 'Physical':
            other_buff *= 0.5
        if target_sidecond['auroraveil']:
            other_buff *= 0.5

    base_dmg = dmg * stab_buff * type_buff * other_buff

    return base_dmg


def check_useful(user, target, move, env):
    sk_type = move['type']
    sk_name = move['name']
    sk_ctg = move['category']
    sk_flag = move['flags']

    if sk_ctg == 'Status':
        if move['target'] == 'normal' and 'Grass' in target['type'] and move['type'] == 'Grass':
            return False
        if 'status' in move:
            status = move['status']
            if status == 'brn' and 'Fire' in target['type']:
                return False
            if status == 'par' and 'Electric' in target['type']:
                return False
            if status in ['psn', 'tox'] and ('Poison' in target['type'] or 'Steel' in target['type']):
                return False
        if sk_name == 'Thunder Wave':
            if sk_type == 'Normal' and 'Ghost' in target['type'] or sk_type == 'Electric' and 'Ground' in target[
                'type']:
                return False

    if sk_type == 'Water':
        if target['ability'] == 'Water Absorb':
            return False
        if target['ability'] == 'Dry Skin':
            return False
        if target['ability'] == 'Storm Drain':
            return False

    if sk_type == 'Fire':
        if target['ability'] == 'Flash Fire':
            return False

    if sk_type == 'Electric':
        if target['ability'] == 'Lightning Rod':
            return False
        if target['ability'] == 'Motor Drive':
            return False
        if target['ability'] == 'Volt Absorb':
            return False

    if sk_type == 'Grass':
        if target['ability'] == 'Sap Sipper':
            return False

    if sk_type == 'Ground' and sk_ctg != 'Status':
        if imm_ground(target, env):
            return False

    if target['ability'] == 'Bulletproof' and 'bullet' in sk_flag:
        return False

    if target['ability'] == 'Soundproof' and 'sound' in sk_flag:
        return False

    # check no effect move type
    if sk_ctg != 'Status':
        type_buff = 1
        for attr in target['type']:
            if sk_type == 'Ground' and attr == 'Flying' and not imm_ground(target, env):
                continue
            type_buff *= get_attr_fac(sk_type, attr)
        if type_buff == 0:
            if not (user['ability'] == 'Scrappy' and sk_type == 'Normal' and 'Ghost' in target['type']):
                return False
        if target['ability'] == 'Wonder Guard' and type_buff <= 1:
            return False

    return True


def calc_type_buff(move, target):
    sk_name, sk_type = move['name'], move['type']
    type_buff = 1
    for attr in target['type']:
        if attr == 'Flying' and target['vstatus']['roost']:
            continue
        type_buff *= get_attr_fac(sk_type, attr)

    if sk_name == 'Flying Press':
        for attr in target['type']:
            type_buff *= get_attr_fac(Attr.Flying, attr)

    if sk_name == 'Freeze Dry' and target['type']:
        type_buff *= 4
    return type_buff


def imm_ground(pkm, env):
    return pkm['vstatus']['smackdown'] and 'Flying' in pkm['type'] and not pkm['vstatus']['roost'] or pkm[
        'ability'] == 'Levitate' or pkm[
               'item'] is 'Air Balloon' or pkm['vstatus']['magnetrise'] or pkm['vstatus']['telekinesis'] or \
           env['pseudo_weather']['gravity']


from docs.obs import obs

if __name__ == '__main__':
    print(gen_action(obs))
