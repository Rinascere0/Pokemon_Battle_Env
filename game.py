import time

from main.env import Env
# import your own player class
from main.player import RandomPlayer
from main.ui_player import myPlayer
from main.log import BattleLog
from main.utils import Utils
from lib.functions import *

from threading import Thread

# set total game nums
game_nums = 1

# whether show log in terminal or save log in file
save_log = False


class Game:
    def __init__(self):
        self.env = Env()
        self.log = BattleLog(self, save_log)
        self.utils = Utils(self.log)
        self.players = []
        self.moves = []
        self.round_players = []
        self.switch_in_turn = []
        self.Round = 0
        self.end = False

        # if use ui
        self.ui = None

        # change to your own player class!
        self.add_player(RandomPlayer())
        # self.add_player(RandomPlayer())
        self.add_player(myPlayer())

    def add_player(self, player):
        player.set_game(self, len(self.players), self.env, self.log)
        self.players.append(player)

    def set_ui(self, ui):
        self.ui = ui

    def get_ui_player(self):
        return self.players[1]

    def send_log(self, log):
        if self.ui:
            self.ui.send_log(log)

    def force_end(self):
        for player in self.players:
            player.signal(Signal.End)
        self.end = True

    def force_wait(self):
        for player in self.players:
            player.signal(Signal.Wait)

    def send(self, pid, move, in_turn=False):
        if not move:
            self.end = True
        if move['type'] == ActionType.Switch:
            # in turn switch
            if in_turn:
                self.switch_in_turn.append(move)
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
        if player.alive.sum() <= 1:
            return
        player.signal(Signal.Switch_in_turn)
        while len(self.switch_in_turn) == 0:
            time.sleep(0.01)
        self.switch_in_turn.append(None)
        self.utils.check_switch(self.env, [player, self.players[1 - player.pid]], self.switch_in_turn,
                                check=False)
        self.switch_in_turn = []

    def start(self):
        self.thread = Thread(target=self.mainloop, args=())
        self.thread.start()

    def mainloop(self):
        for player in self.players:
            player.start()
        time.sleep(0.1)

        for game_id in range(game_nums):
            for player in self.players:
                player.set_team()
            self.log.reset(self.players)
            self.env.reset()

            # Match-up
            self.moves = []
            self.players[0].signal(Signal.Switch)
            self.players[1].signal(Signal.Switch)
            while len(self.moves) < 2:
                time.sleep(0.01)
                if self.end:
                    return
            done = self.utils.match_up(self.env, self.round_players, self.moves)
            self.reset_round()

            # Mainloop
            self.Round = 1
            while not done:
                self.log.add(event='round', val=self.Round)
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
                        if self.end:
                            return

                    if len(to_switch) < 2:
                        self.round_players.append(self.players[1 - self.round_players[0].pid])
                        self.moves.append(None)
                    done, to_switch = self.utils.check_switch(self.env, self.round_players, self.moves)
                    self.reset_round()
                self.utils.finish_turn(self.env, self.players)

                self.log.step_print()
                self.Round += 1

        self.force_end()

    def get_state(self, pid):
        player = self.players[pid]
        foe = self.players[1 - pid]
        state = {}
        my_team = {}
        pkms = []
        for pkm_id, pkm in enumerate(player.pkms):
            pkm_info = {'name': pkm.name,
                        'id': pkm_id,
                        'type': pkm.attr,
                        'gender': pkm.gender,
                        'nature': pkm.nature,
                        'item': pkm.base_item,
                        'ability': pkm.current_ability,
                        'weight': pkm.weight,
                        'hp': pkm.HP,
                        'maxhp': pkm.maxHP,
                        'hp_perc': pkm.HP / pkm.maxHP,
                        'atk': pkm.Atk,
                        'def': pkm.Def,
                        'spa': pkm.Satk,
                        'spd': pkm.Sdef,
                        'spe': pkm.Spe,
                        'status': pkm.status,
                        'status_turn': pkm.status_turn,
                        'stat_lv': pkm.stat_lv,
                        'alive': pkm.alive}
            moves = []
            for move_id, move in enumerate(pkm.moves):
                moves.append({'name': move, 'pp': pkm.pp[move_id], 'maxpp': pkm.maxpp[move_id]})
            pkm_info['moves'] = moves
            total_vstatus = {}
            for vstatus, turn in pkm.vstatus.items():
                if turn:
                    total_vstatus[vstatus] = turn
            pkm_info['vstatus'] = total_vstatus
            pkms.append(pkm_info)

        sideconds = {}
        for sidecond, turn in self.env.side_condition[pid].items():
            if turn > 0:
                sideconds[sidecond] = turn

        slotconds = {}
        for slotcond, turn in self.env.slot_condition[pid].items():
            if turn:
                slotconds[slotcond] = turn

        my_pivot_id = player.pivot
        my_pivot = player.get_pivot()
        masks = {'switch': my_pivot.can_switch, 'move': my_pivot.move_mask,
                 'mega': player.mega[my_pivot_id], 'z': my_pivot.z_mask}
        my_team['pkms'] = pkms
        my_team['pivot'] = player.pivot
        my_team['sidecond'] = sideconds
        my_team['slotcond'] = slotconds
        my_team['masks'] = masks

        foe_team = {}
        foe_pkms = []
        for pkm_id, pkm in enumerate(foe.pkms):
            pkm_info = {'name': pkm.name,
                        'id': pkm_id,
                        'type': pkm.attr,
                        'hp_perc': pkm.HP / pkm.maxHP,
                        'status': pkm.status,
                        'status_turn': pkm.status_turn,
                        'stat_lv': pkm.stat_lv,
                        'alive': pkm.alive}
            if pkm.ability_revealed:
                pkm_info['ability'] = pkm.ability
            else:
                pkm_info['ability'] = 'unrevealed'
            for move_id, (move, pp, maxpp) in enumerate(zip(pkm.moves, pkm.pp, pkm.maxpp)):
                if pp < maxpp:
                    pkm_info['move' + str(move_id + 1)] = {'name': move, 'pp': pkm.pp[move_id]}
                else:
                    pkm_info['move' + str(move_id + 1)] = {'name': 'unrevealed'}
            for vstatus, turn in pkm.vstatus.items():
                if turn:
                    total_vstatus[vstatus] = turn
            pkm_info['vstatus'] = total_vstatus
            foe_pkms.append(pkm_info)

        sideconds = {}
        for sidecond, turn in self.env.side_condition[1 - pid].items():
            if turn > 0:
                sideconds[sidecond] = turn

        slotconds = {}
        for slotcond, turn in self.env.slot_condition[1 - pid].items():
            if turn:
                slotconds[slotcond] = turn

        foe_team['pkms'] = foe_pkms
        foe_team['pivot'] = foe.pivot
        foe_team['sidecond'] = sideconds
        foe_team['slotcond'] = slotconds

        env = {'weather': {'name': self.env.weather, 'remain': self.env.weather_turn},
               'terrain': {'name': self.env.terrain, 'remain': self.env.terrain_turn}}

        pseudo_weather = {}
        for pd_weather, turn in self.env.pseudo_weather.items():
            if turn:
                pseudo_weather[pd_weather] = turn
        env['pseudo_weather'] = pseudo_weather

        state['round'] = self.Round
        state['my_team'] = my_team
        state['foe_team'] = foe_team
        state['env'] = env
        state['loser'] = self.log.loser

        return state


if __name__ == '__main__':
    game = Game()
    game.start()
