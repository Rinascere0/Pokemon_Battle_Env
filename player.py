import random
import time
import numpy as np
from abc import abstractmethod

from pokemon import Pokemon
from const import *
from threading import Thread
from read_team import read_team

import numpy


class Player:
    def __init__(self):
        self.pkms = []
        self.pivot = 0
        self.alive = self.alive = np.ones(6)
        self.status = Signal.Wait
        self.name = ""
        self.game = None
        self.pid = -1
        self.log = None

    def load_team(self, team):
        self.pkms = team
        self.alive = np.ones(6)
        self.pivot = 0
        for pkm_id, pkm in enumerate(self.pkms):
            pkm.setup(pkm_id, self, self.env, self.log)

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

    def mainloop(self):
        self.load_team(read_team())
        while True:
            time.sleep(0.1)
            if self.status == Signal.Move:
                self.game.send(self.pid, self.gen_move())
                self.status = Signal.Wait
            elif self.status == Signal.Switch:
                self.game.send(self.pid, self.gen_switch())
                self.status = Signal.Wait
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
        return np.random.choice(pivot.move_infos, p=pivot.move_mask / pivot.move_mask.sum())

    def gen_switch(self):
        return np.random.choice(np.arange(0, 6), p=self.alive / self.alive.sum())

    def switch(self, env, pivot, withdraw=False):
        if withdraw:
            self.log.add(self, 'withdraw', self.get_pivot().name)
        self.log.add(self, 'switch', self.pkms[pivot].name)
        self.pkms[pivot].switch(env, self.get_pivot())
        self.pivot = pivot

    def make_switch(self, random=False):
        if random:
            self.switch(np.random.choice(np.arange(0, 6), self.alive / self.alive.sum()))
        else:
            self.switch(np.random.choice(np.arange(0, 6), self.alive / self.alive.sum()))
