import time

from env import Env
from player import RandomPlayer
from log import BattleLog
from utils import Utils
from const import *


class Game:
    def __init__(self):
        self.env = Env()
        self.log = BattleLog()
        self.utils = Utils(self.log)
        self.players = []
        self.moves = []
        self.round_players = []

        for _ in range(2):
            self.add_player(RandomPlayer())

    def add_player(self, player):
        player.set_game(self, len(self.players), self.env, self.log)
        self.players.append(player)

    def send(self, pid, move):
        self.round_players.append(self.players[pid])
        self.moves.append(move)

    def reset_round(self):
        self.round_players = []
        self.moves = []

    def start(self):
        for player in self.players:
            player.start()
        time.sleep(0.1)
        self.log.reset(self.players)

        Round = 1
        done = False
        self.moves = []
        while not done:
            print('Round', Round)
            self.players[0].signal(Signal.Move)
            self.players[1].signal(Signal.Move)
            while len(self.moves) < 2:
                time.sleep(0.01)
            done, to_switch = self.utils.step_turn(self.env, self.round_players, self.moves)
            self.reset_round()
            if len(to_switch) > 0:
                for player in to_switch:
                    player.signal(Signal.Switch)
                while len(self.moves) < len(to_switch):
                    time.sleep(0.01)
                for player, move in zip(self.round_players, self.moves):
                    player.switch(move)
                self.reset_round()

            Round += 1
            self.log.step_print()
        for player in self.players:
            player.signal(Signal.End)


if __name__ == '__main__':
    game = Game()
    game.start()
