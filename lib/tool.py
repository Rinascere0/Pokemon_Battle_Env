from data import moves, pokedex
import numpy as np


def calc_stats(user, env):
    pass


def calc_dmg(user, target, move, env):
    pass


def check_useful(user, target, move, env):
    pass


def find_best_action(team, foe_team, pivot_id, foe_pivot_id, env):
    pivot = team[pivot_id]
    foe_pivot = foe_team[foe_pivot_id]
    greedy_move = find_best_move(pivot, foe_pivot, env)
    random_moves = find_status_move(pivot, foe_pivot, env)
    best_foe = find_best_foe(pivot, foe_team, env)
    predict_move = find_best_move(pivot, best_foe, env)
    predict_switch = find_best_counter(team, best_foe, env)
    utvs = check_utvs(pivot, foe_pivot, env)

    action_space = [greedy_move, predict_move, predict_switch, random_moves, utvs]

    prob = [0.4, 0.2, 0.2, 0.1 * (len(random_moves) > 0), 0.1 * (utvs is not None)]
    prob = prob / prob.sum()

    action = np.random.choice(action_space, p=prob)
    if type(action) is list:
        action = np.random.choice(random_moves)
    return action


def find_status_move(user, target, env):
    total_moves = []
    for move_name in user.moves:
        move = moves[move_name]
        if move['category'] == 'Status' and check_useful(user, target, move, env):
            total_moves.append(move)

    return total_moves


def check_utvs(user, target, env):
    for name in ['U-Turn', 'Volt Switch']:
        if name in user['moves'] and check_useful(user, target, moves[name], env):
            return moves[name]


def find_best_move(user, target, env):
    best_move = None
    max_dmg = 0
    for move_name in user['moves']:
        move = moves[move_name]
        if check_useful(user, target, move, env):
            dmg = calc_dmg(user, target, move, env)
            if dmg > max_dmg:
                best_move = move
                max_dmg = dmg
    return move, dmg


def find_best_foe(user, team, env):
    foe = None
    min_dmg = 1000
    for pkm in team:
        _, dmg = find_best_move(user, pkm, env)
        if dmg < min_dmg:
            foe = pkm
            min_dmg = dmg
    return foe, min_dmg


def find_best_counter(team, target, env):
    max_dmg = 0
    best_pkm = None
    for pkm in team:
        _, dmg = find_best_move(pkm, target, env)
        if dmg > max_dmg:
            best_pkm = pkm
            max_dmg = dmg
    return best_pkm
