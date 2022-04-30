import random

import numpy as np
from data.moves import Moves
from data.pokedex import pokedex
from functions import *
import copy
from const import *

Burn, Sleep, Toxic, Poison, Paralyse, Frozen = range(6)


class Pokemon:
    def __init__(self, info):
        # load team info
        self.name = info['Name']
        #    self.nickname = info['nickname']
        self.gender = info['Gender']
        self.evs = {key: None2Zero(value) for key, value in info.items() if
                    key in ['Atk', 'Def', 'SpA', 'SpD', 'Spe', 'HP']}
        self.ivs = {key[1:]: None2Zero(value) for key, value in info.items() if
                    key in ['iAtk', 'iDef', 'iSpA', 'iSpD', 'iSpe', 'iHP']}
        self.nature = info['Nature']
        self.moves = [info['Move1'], info['Move2'], info['Move3'], info['Move4']]
        self.lv = info['Lv']
        self.item = info['Item']
        self.base_ability = info['Ability']
        self.current_ability = info['Ability']
        self.ability = info['Ability']

        # load dex info
        pkm_info = pokedex[self.name.replace(' ', '').replace('-', '').lower()]
        self.sp = pkm_info['baseStats']
        self.attr = pkm_info['types']
        self.base_weight = pkm_info['weightkg']

        # state
        self.base_stats = gen_stats(self.sp, self.evs, self.ivs, self.lv, self.nature)
        self.stats = copy.deepcopy(self.base_stats)
        self.maxHP = self.stats['HP']
        self.HP = self.stats['HP']

        self.stat_lv = {
            'atk': 0,
            'def': 0,
            'spa': 0,
            'spd': 0,
            'spe': 0,
            'evasion': 0,
            'accuracy': 0
        }

        # battle stat
        self.status = None
        # {'brn': 0, 'slp': 0, 'tox': 0, 'psn': 0, 'par': 0, 'frz': 0}
        self.status_turn = 0
        self.metronome = 0
        self.move_mask = np.ones(4)

        # lock skill e.g. outrage, iceball
        self.lock_move = None
        self.lock_round = 0

        # multihit buff e.g. triple kick
        self.multi_count = 0

        # damage calc e.g. focus punch, counter
        self.dmg = 0
        self.dmg_calc = None  # Physical, Special, Any

        self.vstatus = {'aquaring': 0, 'attract': 0, 'banefulbunker': 0, 'bide': 0, 'partiallytrapped': 0, 'charge': 0,
                        'confusion': 0, 'curse': 0, 'defensecurl': 0, 'destinybond': 0, 'protect': 0, 'disable': 0,
                        'electrify': 0, 'embargo': 0, 'encore': 0, 'endure': 0, 'flinch': 0, 'focusenergy': 0,
                        'followme': 0, 'foresight': 0, 'gastroacid': 0, 'grudge': 0, 'healblock': 0, 'helpinghand': 0,
                        'imprison': 0,
                        'ingrain': 0, 'kingsshield': 0, 'laserfocus': 0, 'leechseed': 0, 'lockedmove': 0,
                        'magiccoat': 0,
                        'magnetrise': 0, 'maxguard': 0, 'minimize': 0, 'miracleeye': 0, 'nightmare': 0, 'noretreat': 0,
                        'obstruct': 0, 'octolock': 0, 'powder': 0, 'powertrick': 0, 'ragepowder': 0, 'smackdown': 0,
                        'snatch': 0, 'spikyshield': 0, 'spotlight': 0, 'stockpile': 0, 'substitute': 0, 'tarshot': 0,
                        'taunt': 0, 'telekinesis': 0, 'torment': 0, 'yawn': 0}

        self.future = []

        self.pkm_id = -1
        self.turn = 0
        self.alive = True

        self.player = None
        self.log = None

    def setup(self, pkm_id, player, env, log):
        self.pkm_id = pkm_id
        self.log = log
        self.player = player
        self.env = env

    def get_sidecond(self):
        return self.env.side_condition[self.player.pid]

    def faint(self):
        self.log.add(self, 'faint')
        self.player.faint(self.pkm_id)
        self.alive = False
        self.turn = False

    def add_cond(self, cond):
        if cond is not None:
            #  print(cond)
            pass

    def set_lock(self, move=None):
        self.lock_move = move
        if self.lock_move is None:
            self.lock_round = 0
        else:
            self.lock_round += 1

    def add_status(self, status):
        if self.status is None:
            self.status = status
            self.log.add(self, 'status', full_status[self.status])
            if status == 'slp':
                self.status_turn = random.randint(1, 3)
            else:
                self.status_turn = 1
        else:
            self.log.add(self, 'istatus', full_status[self.status])
            pass

    def add_vstate(self, vstatus, cond=None):
        if not self.alive:
            return
            # 已有相同状态
        if self.vstatus[vstatus] != 0:
            pass
        if vstatus == 'lockedmove':
            pass
        # 持续时间特殊
        turn = 1
        if cond is None:
            if vstatus == 'confusion':
                turn = random.randint(1, 3)
                self.log.add(self, 'confusion')
            elif vstatus in ['smackdown', 'partiallytrapped', 'foresight']:
                turn = -1
            elif vstatus == 'protect':
                turn = 1
        # 持续时间给出
        elif 'duration' in cond:
            turn = cond['duration']
        else:
            if vstatus in ['destinybond']:
                turn = 1
            elif vstatus == 'nightmare':
                if self.status['slp'] > 0:
                    turn = -1
                else:
                    pass
            else:
                turn = -1
        self.log.add(self, vstatus)
        self.vstatus[vstatus] = turn

    def add_sidecond(self, sidecond, cond=None):
        if sidecond == 'toxicspikes' and self.get_sidecond()[sidecond] > 1 or sidecond != 'toxicspikes' and \
                self.get_sidecond()[sidecond] > 0:
            self.log.add(event='fail')
            return
        if sidecond == 'auroraveil' and self.env.weather['hail'] == 0:
            self.log.add(event='fail')
            return

        turn = 1
        if cond:
            turn = cond['duration']
            if sidecond in ['lightscreen', 'reflect', 'auroraveil'] and self.item == 'Light Clay':
                turn = 8
        self.get_sidecond()[sidecond] += turn
        self.log.add(self, sidecond)

    def add_future(self, user, sk_name):
        if sk_name not in self.future:
            self.future.append({sk_name: {round: 2, user: user}})

        self.log(self, 'pred')

    def heal(self, val, perc=False):
        if perc:  # 百分比治疗
            val = int(self.maxHP * perc)

        if self.item == 'Big Root':
            val = int(val * 1.3)

        self.HP = min(self.maxHP, self.HP + val)
        self.log(self, 'heal', val / self.maxHP)

    def boost(self, stat, lv, src=None):
        if lv > 0:
            if self.stat_lv[stat] == 6:
                self.log.add(self, '+7', full_stat[stat])
            else:
                self.stat_lv[stat] = min(self.stat_lv[stat] + lv, 6)
                if lv == 1:
                    self.log.add(self, '+1', full_stat[stat])
                elif lv == 2:
                    self.log.add(self, '+2', full_stat[stat])
                elif lv == 3:
                    self.log.add(self, '+3', full_stat[stat])
                elif lv == 6:
                    self.log.add(self, '+6', full_stat[stat])
        else:
            if self.ability in ['White Smoke', 'Full Metal Body', 'Clear Body'] and src is not None:
                self.log.add(self, '-0', full_stat[stat])
                return
            if self.ability == 'Mirror Armor' and src is not None:
                src.boost(stat, lv)
                return
            if self.stat_lv[stat] == -6:
                self.log.add(self, '-7', full_stat[stat])
            else:
                val = min(-lv, 6 + self.stat_lv[stat])
                self.stat_lv[stat] = max(self.stat_lv[stat] + lv, -6)
                if lv == -1:
                    self.log.add(self, '-1', full_stat[stat])
                elif lv == -2:
                    self.log.add(self, '-2', full_stat[stat])
                if self.ability == 'Competitive' and src is not None:
                    self.boost('spa', 2 * val)
                    self.log.add(self, '+2', full_stat['spa'])
                if self.ability == 'Defiant' and src is not None:
                    self.boost('atk', 2 * val)
                    self.log.add(self, '+2', full_stat['atk'])

    def moldbreak(self):
        if self.current in ['Battle Armor', 'Clear Body', 'Damp', 'Dry Skin', 'Filter', 'Flash Fire',
                            'Flower Gift', 'Heatproof', 'Hyper Cutter', 'Immunity', 'Inner Focus', 'Insomnia',
                            'Keen Eye', 'Leaf Guard', 'Levitate', 'Lightning Rod', 'Limber', 'Magma Armor',
                            'Marvel Scale', 'Motor Drive', 'Oblivious', 'Own Tempo', 'Sand Veil', 'Shell Armor',
                            'Shield Dust', 'Simple', 'Snow Cloak', 'Solid Rock', 'Soundproof', 'Sticky Hold',
                            'Storm Drain', 'Sturdy', 'Suction Cups', 'Tangled Feet', 'Thick Fat', 'Unaware',
                            'Vital Spirit', 'Volt Absorb', 'Water Absorb', 'Water Veil', 'White Smoke',
                            'Wonder Guard,\tBig Pecks', 'Contrary', 'Friend Guard', 'Heavy Metal', 'Light Metal',
                            'Magic Bounce', 'Multiscale', 'Sap Sipper', 'Telepathy', 'Wonder Skin,Aroma Veil',
                            'Bulletproof', 'Flower Veil', 'Fur Coat', 'Overcoat', 'Sweet Veil,Dazzling',
                            'Disguise', 'Fluffy', 'Queenly Majesty', 'Water Bubble,\tMirror Armor', 'Punk Rock',
                            'Ice Scales', 'Ice Face', 'Pastel Veil ']:
            self.ability = ""

    def damage(self, val, perc=False, const=0, attr=Attr.NoAttr, in_turn=True):
        if val < 0:
            #    print('but it didn\'t work!')
            return False
        if in_turn and self.vstatus['protect'] != 0:
            self.log.add(self, 'protect_from')
            return False
        if perc:  # 百分比伤害
            val = int(self.maxHP * perc)
        if const:
            val = const
        for my_attr in self.attr:
            val *= Attr_Mat[attr][Attr_dict[my_attr]]
        if self.vstatus['substitute'] > 0:  # 替身伤害
            self.vstatus['substitute'] = minus(self.vstatus['substitute'], val)
            self.log.add(event='sub_dmg')
            if self.vstatus['substitute'] == 0:
                self.log.add(event='sub_fade')
        elif self.HP <= val:
            self.log.add(self, 'lost', int(self.HP / self.maxHP * 100))
            self.HP = 0
            if self.to_faint():
                self.faint()
            else:
                self.HP += 1
        else:
            self.log.add(self, 'lost', int(val / self.maxHP * 100))
            self.HP = self.HP - val
        return True

    def prep(self, env):
        self.ability = self.current_ability
        self.calc_stat(env)
        self.turn = True

    def end_turn(self):
        for vstate in self.vstatus:
            self.vstatus[vstate] = max(0, self.vstatus[vstate] - 1)
        if self.item == 'leftovers':
            self.log.add(self, 'leftovers')
            self.heal(0, perc=1 / 16)

        self.move_mask = np.ones(4)
        if self.lock_move is not None:
            self.move_mask = np.zeros(4)
            for move_id, move in enumerate(self.moves):
                if move == self.lock_move:
                    self.move_mask[move_id] = 1
                    break

        if self.vstatus['taunt'] > 0:
            for move_id, move in enumerate(self.moves):
                move = move.replace('-', '').replace(' ', '').lower()
                if Moves[move]['category'] == 'Status':
                    self.move_mask[move_id] = 0

        if self.ability == 'Speed Boost':
            self.log.add(self, 'speedboost')
            self.boost('spe', 1)

        if self.ability == 'Moody':
            inc, dec = random.sample(['atk', 'def', 'spa', 'spd', 'spe'])
            self.log.add(self, 'moody')
            self.boost(inc, 2)
            self.boost(dec, -1)

        if self.ability == 'Solar Power' and self.player.env.weather is 'sunnyday':
            self.log.add(self, 'solarpower')
            self.damage(0, 1 / 8)

        if self.status == 'tox':
            self.damage(val=0, perc=self.status_turn / 16, attr=Attr.NoAttr)
            self.status_turn += 1
        if self.status == 'psn':
            self.damage(val=0, perc=1 / 8, attr=Attr.NoAttr)
        if self.status == 'brn':
            self.damage(val=0, perc=1 / 16, attr=Attr.NoAttr)

        for vs in self.vstatus:
            if self.vstatus[vs] > 0:
                self.vstatus[vs] -= 1
                if self.vstatus[vs] == 0:
                    if vs == 'taunt':
                        self.log.add(self, '-taunt')

        for cond in ['auroraveil', 'craftyshield', 'lightscreen', 'luckychant', 'matblock', 'mist', 'quickguard',
                     'reflect', 'safeguard', 'tailwind', 'wideguard']:

            if self.get_sidecond()[cond] > 0:
                self.get_sidecond()[cond] -= 1
                if self.get_sidecond()[cond] == 0:
                    self.log.add(self, '-' + cond)

    def calc_stat(self, env, raw=False, moldbreak=False):
        _, self.Atk, self.Def, self.Satk, self.Sdef, self.Spe = self.stats.values()
        Atk_lv, Def_lv, Satk_lv, Sdef_lv, Spe_lv, Eva_lv, Acc_lv = self.stat_lv.values()

        if not raw:
            self.Atk *= calc_stat_lv(Atk_lv)
            self.Def *= calc_stat_lv(Def_lv)
            self.Satk *= calc_stat_lv(Satk_lv)
            self.Sdef *= calc_stat_lv(Sdef_lv)
            self.Spe *= calc_stat_lv(Spe_lv)
            self.Eva = calc_stat_lv(Eva_lv)
            self.Acc = calc_stat_lv(Acc_lv)

        # Ability Buff
        if not moldbreak:
            if self.ability == 'Defeatist' and self.HP / self.maxHP <= 1 / 2:
                self.Atk *= 0.5
                self.Satk *= 0.5
            if self.ability in ['Huge Power', 'Pure Power']:
                self.Atk *= 2
            if self.ability == 'Guts' and self.cond:
                self.Atk *= 1.5
            if self.ability == 'Quick Feet' and self.cond:
                self.Spe *= 1.5
            if self.ability == 'Tangled Feet' and self.vstatus['confusion']:
                self.Eva *= 2
            if self.ability == 'Solar Power' and env.weather == Weather.Harsh:
                self.Satk *= 2
            if self.ability == 'Chlorophyll' and env.weather == Weather.Harsh:
                self.Spe *= 2
            if self.ability == 'Swift Swim' and env.weather == Weather.Rain:
                self.Spe *= 2
            if self.ability == 'Sand Rush' and env.weather == Weather.Sandstorm:
                self.Spe *= 2
            if self.ability == 'Slush Rush' and env.weather == Weather.Hail:
                self.Spe *= 2
            if self.ability == 'Snow Clock' and env.weather == Weather.Hail:
                self.Eva *= 1.25
            if self.ability == 'Sand Veil' and env.weather == Weather.Sandstorm:
                self.Eva *= 1.25

        # Item Buff
        if self.item == 'Choice Band':
            self.Atk *= 1.5

        if self.item == 'Choice Specs':
            self.Satk *= 1.5

        if self.item == 'Choice Scarf':
            self.Spe *= 1.5

        if self.item == 'Assault Vest':
            self.Sdef *= 1.5

        if self.item == 'Eviolite' and self.name in evolved:
            self.Def *= 1.5
            self.Sdef *= 1.5

        # Status Buff
        if self.get_sidecond()['stickyweb']:
            self.Spe *= 0.5
        if self.status == Paralyse and self.ability != 'Quick Feet':
            self.Spe *= 0.5

        self.weight = self.base_weight

    def switch(self, pivot):
        if not imm_ground(self):
            if self.get_sidecond()['toxicspikes'] > 0:
                if 'Posion' in self.attr:
                    self.get_sidecond()['toxic_spikes'] = 0
                    self.log.add(self, '-toxicspikes')
                else:
                    self.log.add(self, '+toxicspikes')
                    if self.get_sidecond()['toxic_spikes'] == 1:
                        self.add_status('psn')
                    else:
                        self.add_status('tox')
            if self.get_sidecond()['spikes'] > 0 and self.ability != 'Magic Guard':
                self.log.add(self, '+spikes')
                self.damage(0, perc=self.get_sidecond()['spikes'] / 8, attr=Attr.NoAttr)
            if self.get_sidecond()['stickyweb'] > 0:
                self.log.add(self, '+stickyweb')
                self.boost('spe', -1)

        if self.get_sidecond()['stealthrock'] > 0 and self.ability != 'Magic Guard':
            self.log.add(self, '+stealthrock')
            self.damage(0, perc=1 / 8, attr=Attr.Rock)

    def act(self):
        if self.status == 'slp':
            self.status_turn -= 1
            if self.status_turn == 0:
                self.status = None
                pass
        if self.status == 'frz':
            if random.randint(1, 3) == 1:
                self.status = None

    def to_faint(self):
        if self.HP == self.maxHP and self.item == 'Focus Sash':
            self.log.add(self, 'sash')
        elif self.vstatus['endure']:
            self.log.add(self, 'endure')
        else:
            return True
