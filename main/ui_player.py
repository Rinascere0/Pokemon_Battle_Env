import time
import copy

from lib.const import *
from threading import Thread
from lib.read_team import read_team, read_team_by_id, parse_team_sheet

from main.player import Player


class UI_Player(Player):
    def __init__(self):
        super(UI_Player, self).__init__()
        self.last_status = Signal.Wait
        self.ui_inited = False

    def ui_init(self):
        self.ui_inited = True

    def set_game(self, game, pid, env, log, name=None):
        self.game = game
        self.pid = pid
        self.log = log
        self.env = env
        self.name = name if name else names[pid]

    def check_valid_switch(self, action, common_action=False):
        try:
            pivot = action['item']
            if action['type'] != ActionType.Switch:
                raise ValueError('Invalid switch action type!')
            elif not 0 <= action['item'] < 6:
                raise ValueError('Invalid switch action index!')
            elif action['item'] == self.pivot and sum(self.alive) > 1:
                raise ValueError('Cannot switch to the pokemon on field!')
            elif not self.alive[action['item']]:
                raise ValueError('Cannot switch to exhausted pokemon!(' + self.pkms[pivot].name + ')')
            elif not self.get_pivot().can_switch and common_action:
                raise ValueError(self.get_pivot().name + ' cannot switch now！')
        except ValueError as e:
            print(repr(e))
            return False
        else:
            return True

    def gen_valid_action(self):
        action = self.gen_action()
        if self.status == Signal.End:
            return
        if self.check_valid_action(action):
            return action
        else:
            self.game.force_end()

    def gen_valid_switch(self, switch_type):
        action = self.gen_switch(switch_type)
        if self.status == Signal.End:
            return
        if self.check_valid_switch(action):
            return action
        else:
            self.game.force_end()

    def signal(self, sign):
        self.last_status = self.status
        self.status = sign
        while not self.ui_inited:
            time.sleep(0.1)
            if self.status == Signal.End:
                return
        self.game.update(self.pid, self.status)

    def mainloop(self):
        while True:
            time.sleep(0.1)
            if self.status == Signal.Move:
                self.status = Signal.Wait
                self.game.send(self.pid, self.gen_valid_action())
            elif self.status == Signal.Switch:
                self.status = Signal.Wait
                self.game.send(self.pid, self.gen_valid_switch(SwitchType.End_turn))
            elif self.status == Signal.Switch_in_turn:
                self.status = Signal.Wait
                self.game.send(self.pid, self.gen_valid_switch(SwitchType.In_turn), in_turn=True)
            elif self.status == Signal.End:
                return

    # Change tid into your own team name!
    def set_team(self):
        self.load_team(read_team(tid=0))


class myPlayer(UI_Player):
    def __init__(self):
        super(myPlayer, self).__init__()
        self.action = None
        self._team_configured = False
        self._team_load_mode = None
        self._team_preset_id = None
        self._team_showdown_text = None

    def apply_team_choice(self, choice):
        """由客户端 UI 在开局前注入（离线）；在线由 apply_team_wire_to_my_player 设置。"""
        if choice.mode == 'text':
            self._team_load_mode = 'text'
            self._team_showdown_text = choice.showdown_text
            self._team_preset_id = None
        elif choice.mode == 'preset':
            self._team_load_mode = 'preset'
            self._team_preset_id = choice.preset_id
            self._team_showdown_text = None
        else:
            self._team_load_mode = 'random'
            self._team_preset_id = None
            self._team_showdown_text = None
        self._team_configured = True

    def set_team(self):
        if self._team_load_mode == 'text' and self._team_showdown_text:
            self.load_team(parse_team_sheet(self._team_showdown_text))
        elif self._team_load_mode == 'preset' and self._team_preset_id is not None:
            self.load_team(read_team_by_id(self._team_preset_id))
        else:
            self.load_team(read_team(tid=0))
        for pkm in self.pkms:
            pkm.calc_stat(self.env)

    def set_action(self, action_type, item):
        self.action = {'type': action_type, 'item': item}

    def gen_action(self):
        while not self.action:
            time.sleep(0.1)
            if self.status == Signal.End:
                return
        temp = copy.deepcopy(self.action)
        self.action = None
        print(f'actrion{temp}')
        return temp

    def gen_switch(self, switch_type):
        while not self.action:
            time.sleep(0.1)
            if self.status == Signal.End:
                return
        temp = copy.deepcopy(self.action)
        self.action = None
        return temp
