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
        self.name = (info['Name'].split('-Mega')[0]).split('-Ash')[0]
        #    self.nickname = info['nicknam]e']
        self.gender = info['Gender']
        self.evs = {key: None2Zero(value) for key, value in info.items() if
                    key in ['Atk', 'Def', 'SpA', 'SpD', 'Spe', 'HP']}
        self.ivs = {key[1:]: None2Zero(value) for key, value in info.items() if
                    key in ['iAtk', 'iDef', 'iSpA', 'iSpD', 'iSpe', 'iHP']}
        self.nature = info['Nature']
        self.moves = [info['Move1'], info['Move2'], info['Move3'], info['Move4']]
        self.move_infos = [Moves[move_to_key(move)] for move in self.moves]
        self.pp = [move['pp'] * 1.6 for move in self.move_infos]
        self.lv = info['Lv']
        self.item = info['Item']
        self.base_item = info['Item']
        self.used_item = None
        self.base_ability = info['Ability']
        self.current_ability = info['Ability']
        self.ability = info['Ability']

        # load dex info
        pkm_info = pokedex[self.name.replace(' ', '').replace('-', '').lower()]
        #    if 'baseSpecies' in pkm_info:  # Mega & Ash
        #        self.name = pkm_info['baseSpecies']
        self.sp = pkm_info['baseStats']
        self.base_attr = pkm_info['types']
        if self.name == 'Silvally' and self.item in memories:
            self.base_attr = [memories[self.item]]
        if self.name == 'Arceus' and (self.item in plates or self.item in z_crystals):
            self.base_attr = [plates[self.item]]
        self.attr = copy.deepcopy(self.base_attr)

        self.base_weight = pkm_info['weightkg']
        self.can_evo = 'evos' in pkm_info

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
            'eva': 0,
            'acc': 0,
            'ct': 0
        }

        # battle stat
        self.status = None
        # {'brn': 0, 'slp': 0, 'tox': 0, 'psn': 0, 'par': 0, 'frz': 0}
        self.status_turn = 0
        self.protect_turn = 0
        self.last_move = None
        self.next_move = None
        self.metronome = 0
        self.unburden = False
        self.flash_fire = False

        # lock skill e.g. outrage, iceball
        self.lock_move = None
        self.lock_round = 0

        self.choice_move = None
        self.disable_move = None
        # charge move e.g. solar beam
        self.charge = None
        self.charge_round = 0

        # multihit buff e.g. triple kick
        self.multi_count = 0

        self.future = []
        self.alive = True

        # True if player can gen move next turn
        self.can_gen_move = True
        # True if it's the first turn after pkm switches on
        self.switch_on = True
        # True if pkm can switch
        self.can_switch = True
        # True if pkm is about to switch (for pursuit)
        self.to_switch = False
        # True if pkm should activate its ability
        self.activate = True
        # True if pkm still can move this turn
        self.turn = False
        # first turn switch on

        self.off_field = None

        self.round_dmg = {'Physical': 0, 'Special': 0}

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
                        'taunt': 0, 'telekinesis': 0, 'torment': 0, 'yawn': 0, 'roost': 0,'mustrecharge':0}

        self.pkm_id = -1
        self.player = None
        self.log = None

        self.move_mask = np.ones(4)
        self.z_mask = np.zeros(4)
        if self.item in z_crystals:
            sk_type = z_crystals[self.item]
            for move_id, move in enumerate(self.move_infos):
                if move['type'] == sk_type:
                    self.z_mask[move_id] = 1

    def bond_evolve(self):
        if self.name == 'Greninja':
            self.log.add(actor=self, event='Battle Bond', type=logType.ability)
            self.log.add(actor=self, event='transform', val='Greninja-Ash')
            self.name = 'Greninja-Ash'
            pkm_info = pokedex['greninjaash']
            self.sp = pkm_info['baseStats']
            self.base_attr = pkm_info['types']
            self.attr = copy.deepcopy(self.base_attr)
            self.base_weight = pkm_info['weightkg']

            # state
            self.base_stats = gen_stats(self.sp, self.evs, self.ivs, self.lv, self.nature)
            self.stats = copy.deepcopy(self.base_stats)

    def mega_evolve(self):
        mega_name = self.name + '-Mega'
        if self.item[-1] == 'X':
            mega_name = mega_name + '-X'
        elif self.item[-1] == 'Y':
            mega_name = mega_name + '-Y'
        self.log.add(actor=self, event='mega', val=mega_name)
        self.name = mega_name
        pkm_info = pokedex[self.name.replace(' ', '').replace('-', '').lower()]
        self.ability = pkm_info['abilities']['0']
        self.base_ability = pkm_info['abilities']['0']
        self.current_ability = pkm_info['abilities']['0']

        self.sp = pkm_info['baseStats']
        self.base_attr = pkm_info['types']
        self.attr = copy.deepcopy(self.base_attr)
        self.base_weight = pkm_info['weightkg']

        # stat
        self.base_stats = gen_stats(self.sp, self.evs, self.ivs, self.lv, self.nature)
        self.stats = copy.deepcopy(self.base_stats)
        self.activate = True

    def use_item(self, add_log=True):
        if add_log:
            self.log.add(actor=self, event='use_item', val=self.item)
        self.used_item = self.item
        self.base_item = None
        self.item = None
        if self.ability == 'Unburden':
            self.unburden = True

    def lose_item(self, sub=None):
        if self.item in mega_stones or self.item in z_crystals:
            return False
        if sub:
            temp = self.base_item
            self.base_item = sub
            self.item = sub
            self.log.add(actor=self, event='obtain', val=sub)
            return temp
        else:
            self.base_item = None
            self.item = None
            if self.ability == 'Unburden':
                self.unburden = True
            return

    def setup(self, pkm_id, player, env, log):
        self.pkm_id = pkm_id
        self.log = log
        self.player = player
        self.env = env

    def add_future(self, user, sk_name):
        if sk_name not in self.future:
            self.future.append({sk_name: {round: 2, user: user}})

        self.log.add(actor=self, event='pred')

    def loss_pp(self, move, pp):
        for i, m in enumerate(self.moves):
            if m == move['name']:
                self.pp[i] -= pp

    def faint(self):
        self.log.add(actor=self, event='faint')
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

    def cure_status(self):
        if self.status:
            self.log.add(actor=self, event='-status', val=self.status)
            self.status = None

    def cure_vstatus(self, vs):
        self.log.add(actor=self, event='-vstatus', val=vs)
        self.vstatus[vs] = 0

    def add_status(self, status, env, user=None):
        if not self.alive:
            return False
        if not imm_ground(
                self) and env.terrain == 'mistyterrain' or env.terrain == 'electricterrain' and status == 'slp':
            self.log.add(actor=self, event='+' + env.terrain)
            return False

        if self.ability == 'Leaf Guard' and env.weather == 'sunnyday':
            self.log.add(actor=self, event=self.ability, type=logType.ability)
            return False

        if status == 'slp' and self.ability == 'Vital Spirit':
            self.log.add(actor=self, event=self.ability, type=logType.ability)
            return False
        if status == 'brn' and self.ability == 'Water Bubble':
            self.log.add(actor=self, event=self.ability, type=logType.ability)
            return False
        if status in ['psn', 'tox'] and self.ability == 'Immunity':
            self.log.add(actor=self, event=self.ability, type=logType.ability)
            return False
        if status == 'frz' and self.ability == 'Magma Armor':
            self.log.add(actor=self, event=self.ability, type=logType.ability)
            return False
        if status == 'par' and self.ability == 'Limber':
            self.log.add(actor=self, event=self.ability, type=logType.ability)
            return False

        if not self.status:
            self.status = status
            self.log.add(actor=self, event='status', val=full_status[self.status])
            if status == 'slp':
                self.status_turn = random.randint(1, 3)
            else:
                self.status_turn = 1
            if user and user != self and self.ability == 'Synchronize' and status in ['brn', 'psn', 'tox', 'par']:
                self.log.add(actor=self, event=self.ability, type=logType.ability)
                user.add_status(status, env)
        else:
            self.log.add(actor=self, event='++status', val=full_status[self.status])

        if self.item == 'Lum Berry':
            self.use_item()
            self.cure_status()

    def add_vstate(self, vstatus, cond=None, user=None):
        if not self.alive:
            return False
            # 已有相同状态
        if self.vstatus[vstatus] != 0:
            self.log.add(actor=self, event='++' + vstatus)
            return False
        if vstatus in ['lockedmove', 'uproar']:
            pass
        # 持续时间特殊
        turn = 1
        val = ''
        if cond is None:
            if vstatus == 'confusion':
                if self.ability == 'Own Tempo':
                    self.log.add(actor=self, event=self.ability, type=logType.ability)
                turn = random.randint(1, 4)
            elif vstatus in ['smackdown', 'foresight']:
                turn = 10000
            # continuous protect count
            elif vstatus == 'protect':
                if random.uniform(0, 1) <= math.pow(1 / 2, self.protect_turn):
                    self.protect_turn += 1
                else:
                    self.protect_turn = 0
                    self.log.add(event='fail')
                    return False
            elif vstatus == 'partiallytrapped':
                turn = random.randint(4, 5)
                trap_move = user.next_move['name']
                self.trap_move = trap_move
                val = trap_move
            elif vstatus == 'roost':
                pass

                # 持续时间给出
        elif 'duration' in cond:
            turn = cond['duration']

        if vstatus == 'substitute':
            if self.HP > self.maxHP / 4:
                turn = self.maxHP / 4
            else:
                self.log.add(actor=self, event='--substitute')
                return False
        elif vstatus in ['destinybond']:
            turn = 1
        elif vstatus == 'nightmare':
            if self.status['slp'] > 0:
                turn = 10000
            else:
                return False
        elif vstatus == 'disable':
            self.disable_move = self.last_move
            turn = 5
        elif vstatus == 'attract':
            if self.gender and user.gender and self.gender != user.gender:
                turn = 10000
            else:
                return False

        self.log.add(actor=self, event=vstatus, val=val)
        self.vstatus[vstatus] = turn

        if self.item == 'Mental Herb' and vstatus in ['attract', 'disable', 'encore', 'healblock', 'taunt', 'torment']:
            self.use_item()
            self.cure_vstatus(vstatus)

    def can_force_switch(self):
        if self.ability == 'Suction Cups':
            self.log.add(actor=self, event=self.ability, type=logType.ability)
            self.log.add(actor=self, event='-forceswitch')
        elif self.alive:
            return True
        return False

    def heal(self, val=0, perc=False, target=None):
        if not self.alive:
            return
        if perc:  # 百分比治疗
            val = int(self.maxHP * perc)
        if self.item == 'Big Root':
            val = int(val * 1.3)
        if target and target.ability == 'Liquid Ooze':
            self.log.add(actor=self, event='ooze', type=logType.ability)
            self.damage(val)
        else:
            val = min(val, self.maxHP - self.HP)
            if val == 0:
                return
            self.HP += val
            self.log.add(actor=self, event='heal', val=round(100 * val / self.maxHP, 1))

    def boost(self, stat, lv, src=None):
        if not self.alive:
            return
        if stat == 'accuracy':
            stat = 'acc'
        if stat == 'evasion':
            stat = 'eva'
        if self.item == 'White Herb':
            self.log.add(event='+whiteherb')
            return
        if self.ability == 'Contrary':
            self.log.add(actor=self, event=self.ability, type=logType.ability)
            lv = -lv
        if lv > 0:
            if self.stat_lv[stat] == 6:
                self.log.add(actor=self, event='+7', val=full_stat[stat])
            else:
                self.stat_lv[stat] = min(self.stat_lv[stat] + lv, 6)
                if lv == 1:
                    self.log.add(actor=self, event='+1', val=full_stat[stat])
                elif lv == 2:
                    self.log.add(actor=self, event='+2', val=full_stat[stat])
                elif lv == 3:
                    self.log.add(actor=self, event='+3', val=full_stat[stat])
                elif lv == 6:
                    self.log.add(actor=self, event='+6', val=full_stat[stat])
        else:
            if self.ability in ['White Smoke', 'Full Metal Body', 'Clear Body'] and src is not None:
                self.log.add(actor=self, event=self.ability, type=logType.ability)
                self.log.add(actor=self, event='-0', val=full_stat[stat])
                return
            if self.ability == 'Mirror Armor' and src is not None:
                self.log.add(actor=self, event='Mirror Armor', type=logType.ability)
                src.boost(stat, lv)
                return
            if self.ability == 'Hyper Cutter' and stat == 'atk' and src is not None:
                self.log.add(actor=self, event=self.ability, type=logType.ability)
                self.log.add(actor=self, event='-0', val=full_stat[stat])
                return
            if self.ability == 'Keen Eye' and stat == 'acc' and src is not None:
                self.log.add(actor=self, event=self.ability, type=logType.ability)
                self.log.add(actor=self, event='-0', val=full_stat[stat])
                return

            if self.stat_lv[stat] == -6:
                self.log.add(actor=self, event='-7', val=full_stat[stat])
            else:
                val = min(-lv, 6 + self.stat_lv[stat])
                self.stat_lv[stat] = max(self.stat_lv[stat] + lv, -6)
                if lv == -1:
                    self.log.add(actor=self, event='-1', val=full_stat[stat])
                elif lv == -2:
                    self.log.add(actor=self, event='-2', val=full_stat[stat])
                if self.ability == 'Competitive' and src is not None:
                    self.log.add(actor=self, event='Competitive', type=logType.ability)
                    self.boost('spa', 2 * val)

                if self.ability == 'Defiant' and src is not None:
                    self.log.add(actor=self, event='Defiant', type=logType.ability)
                    self.boost('atk', 2 * val)

    def moldbreak(self):
        if self.ability in ['Battle Armor', 'Clear Body', 'Damp', 'Dry Skin', 'Filter', 'Flash Fire',
                            'Flower Gift', 'Heatproof', 'Hyper Cutter', 'Immunity', 'Inner Focus', 'Insomnia',
                            'Keen Eye', 'Leaf Guard', 'Levitate', 'Lightning Rod', 'Limber', 'Magma Armor',
                            'Marvel Scale', 'Motor Drive', 'Oblivious', 'Own Tempo', 'Sand Veil', 'Shell Armor',
                            'Shield Dust', 'Simple', 'Snow Cloak', 'Solid Rock', 'Soundproof', 'Sticky Hold',
                            'Storm Drain', 'Sturdy', 'Suction Cups', 'Tangled Feet', 'Thick Fat', 'Unaware',
                            'Vital Spirit', 'Volt Absorb', 'Water Absorb', 'Water Veil', 'White Smoke',
                            'Wonder Guard', 'Big Pecks', 'Contrary', 'Friend Guard', 'Heavy Metal',
                            'Light Metal',
                            'Magic Bounce', 'Multi Scale', 'Sap Sipper', 'Telepathy', 'Wonder Skin', 'Aroma Veil',
                            'Bulletproof', 'Flower Veil', 'Fur Coat', 'Overcoat', 'Sweet Veil,Dazzling',
                            'Disguise', 'Fluffy', 'Queenly Majesty', 'Water Bubble', 'Mirror Armor', 'Punk Rock',
                            'Ice Scales', 'Ice Face', 'Pastel Veil ']:
            self.ability = None

    def damage(self, val=0, perc=False, const=0, attr='NoAttr', user=None, category=None):
        if not self.alive:
            return False
        if self.ability == 'Magic Guard' and not user:
            return False
        if val < 0:
            #    print('but it didn\'t work!')
            return False
        if perc:  # 百分比伤害
            val = int(self.maxHP * perc)
        if const:
            val = const
        for my_attr in self.attr:
            val *= get_attr_fac(attr, my_attr)
        if user and user.ability != 'Infiltrator' and self.vstatus['substitute'] > 0:  # 替身伤害
            self.vstatus['substitute'] = max(0, self.vstatus['substitute'] - val)
            self.log.add(actor=self, event='+substitute')
            if self.vstatus['substitute'] == 0:
                self.log.add(actor=self, event='-substitute')
            return False
        elif user and self.name == 'Mimikyu' and self.ability == 'Disguise':
            self.log.add(actor=self, event=self.ability, type=logType.ability)
            self.log.add(actor=self, event='+disguise')
            self.name = 'Mimikyu-Busted'
            # TODO: should be no damage rather than false
            return False
        elif self.HP <= val:
            self.log.add(actor=self, event='lost', val=round(self.HP / self.maxHP * 100, 1))
            val = self.HP
            self.HP = 0
            if self.to_faint():
                self.faint()
                if user and user is not self:
                    if self.vstatus['destinybond']:
                        self.log.add(actor=self, event='destinybond', target=user)
                        user.faint()
                    if user.ability == 'Battle Bond':
                        user.bond_evolve()
                    if user.ability == 'Beast Boost':
                        max_stat = 'Atk'
                        max_val = 0
                        for stat, val in user.base_stats.items():
                            if stat != 'HP' and val > max_val:
                                max_stat = stat
                                max_val = val
                        self.log.add(actor=user, event='Beast Boost', type=logType.ability)
                        user.boost(max_stat.lower(), 1)
                foe_pivot = self.player.get_opponent_pivot()
                if foe_pivot.ability == 'Soul-Heart':
                    self.log.add(actor=foe_pivot, event='Soul Heart', type=logType.ability)
                    foe_pivot.boost('spa', 1)

            else:
                self.HP = 1
                val -= 1
        else:
            self.log.add(actor=self, event='lost', val=round(val / self.maxHP * 100, 1))
            self.HP = self.HP - val

        if self.item is 'Air Balloon':
            self.use_item()
            self.log.add(actor=self, event='-balloon')

        if self.HP <= 1 / 2 * self.maxHP and self.item == 'Sitrus Berry':
            self.use_item()
            self.heal(perc=1 / 4)

        if self.HP <= 1 / 4 * self.maxHP or self.HP <= 1 / 2 * self.maxHP and self.ability == 'Gluttony':
            if self.item in hp_berry:
                self.use_item()
                self.heal(perc=1 / 3)
            elif self.item in stat_berry:
                self.use_item()
                self.boost(stat_berry[self.item], 1)

        if category:
            self.round_dmg[category] += val
        return val

    def prep(self, env, target, next_move):
        self.calc_stat(env, target)
        self.turn = True
        self.can_switch = True
        if next_move['type'] == ActionType.Switch:
            self.next_move = None
        else:
            self.next_move = next_move['item']

    def end_turn(self, env, target):
        if not self.alive:
            return
        if self.activate:
            self.activate = False
        else:
            self.switch_on = False
        # TODO: Other forms of protect
        if self.last_move != 'Protect':
            self.protect_turn = 0

        if self.item == 'Leftovers':
            if self.HP < self.maxHP:
                self.log.add(actor=self, event='leftovers')
                self.heal(0, perc=1 / 16)

        if self.ability == 'Poison Heal' and self.status in ['tox', 'psn'] and self.HP < self.maxHP:
            self.log.add(actor=self, event=self.ability, type=logType.ability)
            self.heal(perc=1 / 8)

        if env.terrain == 'grassyterrain' and self.alive:
            if not imm_ground(self):
                if self.HP < self.maxHP:
                    self.log.add(actor=self, event='+grassyterrain')
                self.heal(0, 1 / 16)

        if self.item == 'Black Sludge':
            if 'Poison' in self.attr:
                self.log.add(actor=self, event='+blacksludge')
                self.heal(0, perc=1 / 16)
            else:
                self.log.add(actor=self, event='-blacksludge')
                self.damage(0, perc=1 / 8)

        if self.vstatus['nightmare']:
            self.log.add(actor=self, event='+nightmare')
            self.damage(perc=1 / 4)

        if self.status == 'tox' and self.alive:
            if self.ability != 'Poison Heal':
                self.log.add(actor=self, event='+psn')
                self.damage(val=0, perc=self.status_turn / 16)
            self.status_turn += 1
        if self.status == 'psn' and self.alive:
            if self.ability != 'Poison Heal':
                self.log.add(actor=self, event='+psn')
                self.damage(val=0, perc=1 / 8)
        if self.status == 'brn':
            self.log.add(actor=self, event='+brn')
            self.damage(val=0, perc=1 / 16)

        if self.status == 'slp' and self.vstatus['nightmare'] and self.alive:
            self.log.add(actor=self, event='+nightmare')
            self.damage(0, 1 / 8)

        if self.ability == 'Solar Power' and env.weather is 'sunnyday' and self.alive:
            self.log.add(actor=self, event='solarpower')
            self.damage(0, 1 / 8)

        if self.ability == 'Dry Skin' and env.weather is 'sunnyday' and self.alive:
            self.log.add(actor=self, event='dryskin')
            self.damage(0, 1 / 8)

        if self.ability == 'Dry Skin' and env.weather is 'Raindance' and self.alive:
            self.log.add(actor=self, event='dryskin')
            self.heal(0, 1 / 8)

        if env.weather == 'Raindance' and self.ability == 'Rain Dish' and self.alive:
            self.log.add(actor=self, event='Rain Dish')
            self.heal(0, 1 / 16)

        if env.weather == 'hail' and self.ability == 'Ice Body' and self.alive:
            self.log.add(actor=self, event='Ice Body')
            self.heal(0, 1 / 16)

        if self.ability not in ['Overcoat'] and self.item != 'Safety Goggles' and self.alive:
            if env.weather == 'hail' and 'Ice' not in self.attr:
                self.log.add(actor=self, event='+hail')
                self.damage(0, 1 / 16)

            if env.weather == 'Sandstorm' and not set(self.attr).intersection(set(['Ground', 'Rock', 'Steel'])):
                self.log.add(actor=self, event='+Sandstorm')
                self.damage(0, 1 / 16)

        if env.weather == 'Raindance' and self.ability == 'Hydration' and self.alive:
            if self.status:
                self.log.add(actor=self, event='Hydration', type=logType.ability)
                self.cure_status()

        if self.vstatus['leechseed'] and self.alive:
            self.log.add(actor=self, event='+leechseed')
            dmg = self.damage(val=0, perc=1 / 8)
            target.heal(dmg)

        print(self.vstatus['partiallytrapped'])
        if self.vstatus['partiallytrapped'] and self.alive:
            self.log.add(actor=self, event='+partiallytrapped', val=self.trap_move)
            self.damage(perc=1 / 8)

        if self.charge and self.alive:
            self.charge_round += 1
            if self.charge_round == 2:
                self.charge = None
                self.charge_round = 0

        if self.ability == 'Speed Boost' and self.alive:
            self.boost('spe', 1, 'Speed Boost')

        if self.ability == 'Moody' and self.alive:
            inc, dec = random.sample(['atk', 'def', 'spa', 'spd', 'spe'])
            self.log.add(actor=self, event='moody', type=logType.ability)
            self.boost(inc, 2)
            self.boost(dec, -1)

        if self.item == 'Toxic Orb'and self.alive:
            if not self.status:
                self.log.add(actor=self, event='toxicorb')
                self.add_status('tox', env)

        if self.item == 'Flame Orb'and self.alive:
            if not self.status:
                self.log.add(actor=self, event='flameorb')
                self.add_status('brn', env)

        if self.alive:
            for vs in vstatus_turn:
                if self.vstatus[vs] > 0:
                    self.vstatus[vs] -= 1
                    if self.vstatus[vs] == 0:
                        if vs == 'taunt':
                            self.log.add(actor=self, event='-taunt')

                        if vs == 'partiallytrapped':
                            self.log.add(actor=self, event='-partiallytrapped')
                            self.trap_move = None

        # TODO: ADD bide
        self.round_dmg = {'Physical': 0, 'Special': 0}

    def finish_turn(self, env, target):
        self.move_mask = np.ones(4)
        for move_id, move in enumerate(self.moves):
            if self.lock_move and move != self.lock_move:
                self.move_mask[move_id] = 0
            elif self.choice_move and self.item in ['Choice Band', 'Choice Specs',
                                                    'Choice Scarf'] and move != self.choice_move:
                self.move_mask[move_id] = 0
            elif self.charge and move != self.charge:
                self.move_mask[move_id] = 0
            elif move == self.disable_move:
                self.move_mask[move_id] = 0
            elif self.vstatus['taunt'] > 0 and self.move_infos[move_id]['category'] == 'Status':
                self.move_mask[move_id] = 0
            elif self.pp[move_id] == 0:
                self.move_mask[move_id] = 0

        self.can_gen_move = not self.vstatus['mustrecharge']

        self.can_switch = True
        if target.ability == 'Magnet Pull' and 'Steel' in target.attr:
            self.can_switch = False
        if target.ability == 'Arena Trap' and not imm_ground(target):
            self.can_switch = False
        if target.ability == 'Shadow Tag' and not target.ability == 'Shadow Tag':
            self.can_switch = False
        if self.item == 'Shed Shell':
            self.can_switch = True
        if self.lock_move or self.vstatus['mustrecharge']:
            self.can_switch = False

    def calc_stat(self, env, target, raw=False):
        _, self.Atk, self.Def, self.Satk, self.Sdef, self.Spe = self.stats.values()
        Atk_lv, Def_lv, Satk_lv, Sdef_lv, Spe_lv, Eva_lv, Acc_lv, _ = self.stat_lv.values()

        if not raw:
            self.Atk *= calc_stat_lv(Atk_lv)
            self.Def *= calc_stat_lv(Def_lv)
            self.Satk *= calc_stat_lv(Satk_lv)
            self.Sdef *= calc_stat_lv(Sdef_lv)
            self.Spe *= calc_stat_lv(Spe_lv)
            self.Eva = calc_stat_lv(Eva_lv)
            self.Acc = calc_stat_lv(Acc_lv)

        # Ability Buff
        self.ability = self.current_ability

        if self.ability == 'Defeatist' and self.HP / self.maxHP <= 1 / 2:
            self.Atk *= 0.5
            self.Satk *= 0.5
        if self.ability in ['Huge Power', 'Pure Power']:
            self.Atk *= 2
        if self.ability == 'Guts' and self.status:
            self.Atk *= 1.5
        if self.ability == 'Quick Feet' and self.status:
            self.Spe *= 1.5
        if self.ability == 'Tangled Feet' and self.vstatus['confusion']:
            self.Eva *= 2
        if self.ability == 'Solar Power' and env.weather == 'sunnyday':
            self.Satk *= 2
        if self.ability == 'Chlorophyll' and env.weather == 'sunnyday':
            self.Spe *= 2
        if self.ability == 'Swift Swim' and env.weather == 'Raindance':
            self.Spe *= 2
        if self.ability == 'Sand Rush' and env.weather == 'Sandstorm':
            self.Spe *= 2
        if self.ability == 'Slush Rush' and env.weather == 'hail':
            self.Spe *= 2
        if self.ability == 'Snow Clock' and env.weather == 'hail':
            self.Eva *= 1.25
        if self.ability == 'Sand Veil' and env.weather == 'Sandstorm':
            self.Eva *= 1.25
        if self.unburden:
            self.Spe *= 2

        # Item Buff
        if env.pseudo_weather['magicroom'] or self.ability == 'Klutz':
            self.item = None
        else:
            self.item = self.base_item

        if self.item and 'Berry' in self.item and (self.ability == 'Unnerve' or target.ability == 'Unnerve'):
            self.item = None

        if self.item == 'Choice Band':
            self.Atk *= 1.5

        if self.item == 'Choice Specs':
            self.Satk *= 1.5

        if self.item == 'Choice Scarf':
            self.Spe *= 1.5

        if self.item == 'Assault Vest':
            self.Sdef *= 1.5

        if self.item == 'Eviolite' and self.can_evo:
            self.Def *= 1.5
            self.Sdef *= 1.5

        # Status Buff

        if env.get_sidecond(self)['stickyweb']:
            self.Spe *= 0.5
        if self.status == 'par' and self.ability != 'Quick Feet':
            self.Spe *= 0.5

        if env.pseudo_weather['wonderroom']:
            self.Def, self.Sdef = self.Sdef, self.Def

        if self.vstatus['roost'] and 'Flying' in self.attr:
            self.attr.remove('Flying')
            if not self.attr:
                self.attr = ['Normal']

        self.weight = self.base_weight
        self.ability = self.current_ability

    def reset_stat_lv(self, nega=False):
        for stat in self.stat_lv:
            if not (nega and self.stat_lv[stat] > 0):
                self.stat_lv[stat] = 0

    def reset(self):
        if self.alive:
            self.reset_stat_lv()
            for vstatus in self.vstatus:
                self.vstatus[vstatus] = 0
            self.current_ability = self.base_ability
            self.attr = self.base_attr

            # battle stat
            self.status_turn = 0
            self.protect_turn = 0
            self.last_move = None
            self.next_move = None
            self.metronome = 0
            self.unburden = False
            self.flash_fire = False

            # lock skill e.g. outrage, iceball
            self.lock_move = None
            self.lock_round = 0

            self.choice_move = None
            self.disable_move = None

            self.charge = None
            self.charge_round = 0

            self.multi_count = 0

            self.future = []

            self.off_field = None
            self.round_dmg = {'Physical': 0, 'Special': 0}

            self.can_gen_move = True
            self.switch_on = False
            self.can_switch = True
            self.to_switch = False
            self.activate = True
            self.turn = False

            if self.ability == 'Natural Cure':
                if self.status:
                    self.log.add(actor=self, event=self.ability, type=logType.ability)
                    self.cure_status()

            if self.ability == 'Regenerator':
                if self.HP < self.maxHP:
                    self.log.add(actor=self, event=self.ability, type=logType.ability)
                    self.heal(perc=1 / 3)

    def can_lose_item(self):
        return self.item and self.item not in mega_stones and self.item not in z_crystals and not (
                self.name == 'Silvally' and self.item in memories) and not (
                self.name == 'Arceus' and self.item in plates) and self.ability != 'Sticky Hold'

    def switch(self, env, old_pivot=None, boton=False):
        if old_pivot:
            if boton:
                self.stat_lv = old_pivot.stat_lv
                self.vstatus['substitute'] = copy.deepcopy(old_pivot['substitute'])
                self.vstatus['leechseed'] = copy.deepcopy(old_pivot['leechseed'])
            old_pivot.reset()

            slotcond = env.get_slotcond(self)
            if slotcond['healingwish']:
                self.log.add(actor=self, event='healingwish')
                self.heal(self.maxHP)
                self.cure_status()
                slotcond['healingwish'] = 0
            elif slotcond['lunardance']:
                self.log.add(actor=self, event='lunardance')
                self.heal(self.maxHP)
                self.cure_status()
                slotcond['lunardance'] = 0
            elif slotcond['heal']:
                self.heal(self.maxHP)
                slotcond['heal'] = 0
        self.can_switch = True
        self.to_switch = False

        self.switch_on = True
        self.activate = True
        self.turn = False

        sidecond = env.get_sidecond(self)
        if not imm_ground(self):
            if sidecond['toxicspikes'] > 0:
                if 'Poison' in self.attr:
                    sidecond['toxicspikes'] = 0
                    self.log.add(actor=self, event='-toxicspikes')
                elif not imm_poison(self):
                    self.log.add(actor=self, event='+toxicspikes')
                    if sidecond['toxicspikes'] == 1:
                        self.add_status('psn', env)
                    else:
                        self.add_status('tox', env)
            if sidecond['spikes'] > 0:
                if self.ability != 'Magic Guard':
                    self.log.add(actor=self, event='+spikes')
                    self.damage(0, perc=sidecond['spikes'] / 8)
            if sidecond['stickyweb'] > 0:
                self.log.add(actor=self, event='+stickyweb')
                self.boost('spe', -1)

        if sidecond['stealthrock'] > 0:
            if self.ability!='Magic Guard':
                self.log.add(actor=self, event='+stealthrock')
                self.damage(0, perc=1 / 8, attr='Rock')

    def to_faint(self):
        if self.HP == self.maxHP and self.item == 'Focus Sash':
            self.log.add(actor=self, event='sash')
            self.use_item()
        elif self.vstatus['endure']:
            self.log.add(actor=self, event='endure')
        else:
            return True
        return False
