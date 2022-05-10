import random
import time
import numpy as np
from abc import abstractmethod
from data.moves import Moves

from pokemon import Pokemon
from const import *
from threading import Thread
from read_team import read_team

import numpy

Common, Mega, Z_Move = range(3)


class Player:
    def __init__(self):
        self.pkms = []
        self.pivot = -1
        self.alive = np.ones(6)
        self.status = Signal.Wait
        self.name = None
        self.game = None
        self.pid = -1
        self.log = None
        self.env = None
        self.mega = np.zeros(6)
        self.zmove = np.zeros((6, 4))

    def load_team(self, team):
        self.pkms = team
        self.alive = np.ones(6)
        self.pivot = -1
        for pkm_id, pkm in enumerate(self.pkms):
            pkm.setup(pkm_id, self, self.env, self.log)
            if pkm.item in mega_stones and pkm.name == mega_stones[pkm.item]:
                self.mega[pkm_id] = 1
            if pkm.item in z_crystals:
                attr = z_crystals[pkm.item]
                for move_id, move in enumerate(pkm.move_infos):
                    if move['type'] == attr:
                        self.zmove[pkm_id][move_id] = 1

    def set_game(self, game, pid, env, log):
        self.game = game
        self.pid = pid
        self.log = log
        self.env = env
        self.name = names[pid]


    def get_last_alive(self):
        for pkm in reversed(self.pkms):
            if pkm.alive:
                return pkm

    def start(self):
        thread = Thread(target=self.mainloop, args=())
        thread.start()

    def signal(self, sign):
        self.status = sign

    def get_pivot(self):
        return self.pkms[self.pivot]

    def lose(self):
        return not self.alive.any()

    def get_opponent_pivot(self):
        return self.game.players[1 - self.pid].get_pivot()

    def faint(self, pkm_id):
        self.alive[pkm_id] = False

    def use_mega(self):
        self.mega = np.zeros(6)

    def use_z(self):
        for pkm in self.pkms:
            pkm.z_mask = np.zeros(4)

    def cure_all(self):
        for pkm in self.pkms:
            if pkm.alive:
                pkm.cure_status()

    def check_valid_action(self, action):
        try:
            if action['type'] == ActionType.Switch:
                return self.check_valid_switch(action, common_action=True)
            else:
                pivot = self.get_pivot()
                move_id = action['item']
                # check valid move index
                if not 0 <= move_id < 4:
                    raise ValueError('Invalid move id!')
                else:
                    move = pivot.move_infos[move_id]
                # check valid mega
                if action['type'] == ActionType.Mega:
                    if not self.mega[self.pivot]:
                        raise ValueError(pivot.name + ' cannot mega now!')
                # check valid z
                if action['type'] == ActionType.Z_Move and not pivot.z_mask[move_id]:
                    raise ValueError(pivot.name + ' cannot use Z now!')
                # check valid move
                if not pivot.move_mask[move_id]:
                    if pivot.move_mask.sum() == 0:
                        return Moves['struggle']
                    else:
                        raise ValueError(pivot.name + ' cannot use ' + move['name'] + ' now!')
                action['item'] = move
                return action
        except ValueError as e:
            print(repr(e))
            return False

    def check_valid_switch(self, action, common_action=False):
        try:
            pivot = action['item']
            if action['type'] != ActionType.Switch:
                raise ValueError('Invalid switch action type!')
            elif not 0 <= action['item'] < 6:
                raise ValueError('Invalid switch action index!')
            elif action['item'] == self.pivot and self.alive.sum() > 1:
                raise ValueError('Cannot switch to the pokemon on field!')
            elif not self.alive[action['item']]:
                raise ValueError('Cannot switch to exhausted pokemon!(' + self.pkms[pivot].name + ')')
            elif not self.get_pivot().can_switch_out() and common_action:
                raise ValueError(self.get_pivot().name + ' cannot switch now！')
        except ValueError as e:
            print(repr(e))
            return False
        else:
            return action

    def gen_valid_action(self):
        action = self.gen_action()
        if self.check_valid_action(action):
            return action
        else:
            self.game.force_end()

    def gen_valid_switch(self):
        action = self.gen_switch()
        if self.check_valid_switch(action):
            return action
        else:
            self.game.force_end()

    def mainloop(self):
        self.set_team()
        while True:
            time.sleep(0.1)
            if self.status == Signal.Move:
                self.status = Signal.Wait
                self.game.send(self.pid, self.gen_valid_action())
            elif self.status == Signal.Switch:
                self.status = Signal.Wait
                self.game.send(self.pid, self.gen_valid_switch())
            elif self.status == Signal.Switch_in_turn:
                self.status = Signal.Wait
                self.game.send(self.pid, self.gen_valid_switch(), in_turn=True)
            elif self.status == Signal.End:
                return

    def switch(self, env, pivot, foe=None, withdraw=False):
        if withdraw:
            self.log.add(actor=self, event='withdraw', val=self.get_pivot().name)
        self.log.add(actor=self, event='switch', val=self.pkms[pivot].name)
        if self.pivot == -1:
            self.pkms[pivot].switch(env, None, foe)
        else:
            self.pkms[pivot].switch(env, self.get_pivot(), foe)
        self.pivot = pivot

    # Change tid into your own team name!
    def set_team(self):
        self.load_team(read_team(tid=0))


    @abstractmethod
    # You should return a dict:{'type':ActionType.Switch,'item':pivot}
    # where pivot represents the index of pkm in team you want to switch: range (0,6), type Int
    def gen_switch(self):
        # TODO
        return

    @abstractmethod
    # You should return a dict:{'type':your action_type,'item':move_id}
    # where action_type includes ActionType.mega, ActionType.z_move and ActionType.common representing not using former two
    # and move_id represents the index of move you want to use in your pkm on field: range (0,4), type Int
    def gen_action(self):
        # TODO
        return

    # functional method
    def get_state(self):
        return self.game.get_state(self.pid)


class RandomPlayer(Player):
    def __init__(self):
        super(RandomPlayer, self).__init__()

    def set_team(self):
        self.load_team(read_team(tid=0))
        # for test
        for pkm in self.pkms:
            pkm.calc_stat(self.env)

    def gen_action(self):
        rnd = random.uniform(0, 1)
        if rnd >= 0.9 and self.alive.sum() > 1:
            return self.gen_switch()
        else:
            return self.gen_move()

    def gen_switch(self):
        p = np.copy(self.alive)
        if self.pivot != -1:
            p[self.pivot] = 0
        if not p.any():
            return {'type': ActionType.Switch, 'item': self.pivot}
        else:
            return {'type': ActionType.Switch, 'item': int(np.random.choice(np.arange(0, 6), p=p / p.sum()))}

    def gen_move(self):
        pivot = self.pkms[self.pivot]
        use_z = False
        if not pivot.move_mask.any():
            move_id = 0
        else:
            move_id = np.random.choice(np.arange(4), p=pivot.move_mask / pivot.move_mask.sum())
            if pivot.z_mask[move_id] and random.uniform(0, 1) < 0.5:
                use_z = True

        if self.mega[self.pivot]:
            return {'type': ActionType.Mega, 'item': move_id}
        elif use_z:
            return {'type': ActionType.Z_Move, 'item': move_id}
        else:
            return {'type': ActionType.Common, 'item': move_id}
