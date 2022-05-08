import time

from env import Env
from player import RandomPlayer
from log import BattleLog
from utils import Utils
from const import *
from functions import *


class Game:
    def __init__(self):
        self.env = Env()
        self.log = BattleLog()
        self.utils = Utils(self.log)
        self.players = []
        self.moves = []
        self.round_players = []
        self.switch_in_turn = []

        for _ in range(2):
            self.add_player(RandomPlayer())

    def add_player(self, player):
        player.set_game(self, len(self.players), self.env, self.log)
        self.players.append(player)

    def send(self, pid, move, in_turn=False):
        # check_valid
        if move['type'] == ActionType.Switch:
            # in turn switch
            if in_turn:
                if move == self.players[pid].pivot and self.players[pid].alive.sum() > 1:
                    self.players[pid].signal(Signal.Switch_in_turn)
                else:
                    self.switch_in_turn.append(move)
            else:
                # common switch
                if move == self.players[pid].pivot:
                    self.players[pid].signal(Signal.Switch)
                else:
                    self.round_players.append(self.players[pid])
                    self.moves.append(move)
        else:
            # use move
            self.round_players.append(self.players[pid])
            if move['type'] == ActionType.Z_Move:
                move['item'] = gen_z_move(move['item'])
            self.moves.append(move)

    def reset_round(self):
        self.round_players = []
        self.moves = []

    def call_switch(self, player):
        player.signal(Signal.Switch_in_turn)
        while len(self.switch_in_turn) == 0:
            time.sleep(0.01)
        self.switch_in_turn.append(None)
        self.utils.check_switch(self.env, [player, self.players[1 - player.pid]], self.switch_in_turn,
                                check=False)
        self.switch_in_turn = []

    def start(self):
        for player in self.players:
            player.start()
        time.sleep(0.1)
        self.log.reset(self.players)

        # Match-up
        self.moves = []
        self.players[0].signal(Signal.Switch)
        self.players[1].signal(Signal.Switch)
        while len(self.moves) < 2:
            time.sleep(0.01)
        done = self.utils.match_up(self.env, self.round_players, self.moves)
        self.reset_round()

        # Mainloop
        Round = 1
        while not done:
            print('Round', Round)
            self.players[0].signal(Signal.Move)
            self.players[1].signal(Signal.Move)
            while len(self.moves) < 2:
                time.sleep(0.01)
            done, to_switch = self.utils.step_turn(self, self.env, self.round_players, self.moves)
            self.reset_round()

            self.env.step(self.players, self.log)
            while not done and len(to_switch) > 0:
                for player in to_switch:
                    player.signal(Signal.Switch)
                while len(self.moves) < len(to_switch):
                    time.sleep(0.01)

                if len(to_switch) < 2:
                    self.round_players.append(self.players[1 - self.round_players[0].pid])
                    self.moves.append(None)
                done, to_switch = self.utils.check_switch(self.env, self.round_players, self.moves)
                self.reset_round()
            self.utils.finish_turn(self.env,self.players)


            self.log.step_print()
            Round += 1

        for player in self.players:
            player.signal(Signal.End)


if __name__ == '__main__':
    game = Game()
    game.start()
