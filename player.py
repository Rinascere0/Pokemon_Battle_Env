import random
import time
import numpy as np
from abc import abstractmethod

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

    def mainloop(self):
        self.load_team(read_team())
        while True:
            time.sleep(0.1)
            if self.status == Signal.Move:
                self.status = Signal.Wait
                self.game.send(self.pid, self.gen_move())
            elif self.status == Signal.Switch:
                self.status = Signal.Wait
                self.game.send(self.pid, self.gen_switch())
            elif self.status == Signal.Switch_in_turn:
                self.status = Signal.Wait
                self.game.send(self.pid, self.gen_switch(), in_turn=True)
            elif self.status == Signal.End:
                return

    @abstractmethod
    def gen_move(self):
        # TODO
        return

    @abstractmethod
    def gen_switch(self):
        # TODO
        return


class RandomPlayer(Player):
    def __init__(self):
        super(RandomPlayer, self).__init__()

    def gen_move(self):
        pivot = self.pkms[self.pivot]
        move = np.random.choice(pivot.move_infos, p=pivot.move_mask / pivot.move_mask.sum())
        if self.mega[self.pivot]:
            return {'type': ActionType.Mega, 'item': move}
        else:
            return {'type': ActionType.Common, 'item': move}

    def gen_switch(self):
        p = self.alive
        if self.pivot != -1:
            p[self.pivot] = 0
        if not p.any():
            return {'type': ActionType.Switch, 'item': self.pivot}
        else:
            return {'type': ActionType.Switch, 'item': int(np.random.choice(np.arange(0, 6), p=p / p.sum()))}

    def switch(self, env, pivot, withdraw=False):
        if withdraw and pivot == self.pivot:
            self.log.add(actor=self, event='withdraw', val=self.get_pivot().name)
        self.log.add(actor=self, event='switch', val=self.pkms[pivot].name)
        if self.pivot == -1:
            self.pkms[pivot].switch(env, None)
        else:
            self.pkms[pivot].switch(env, self.get_pivot())
        self.pivot = pivot

    def make_switch(self, random=False):
        if random:
            self.switch(np.random.choice(np.arange(0, 6), self.alive / self.alive.sum()))
        else:
            self.switch(np.random.choice(np.arange(0, 6), self.alive / self.alive.sum()))
