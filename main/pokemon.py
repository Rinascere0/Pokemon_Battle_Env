import random

import numpy as np

from data.moves import Moves
from data.pokedex import pokedex
from lib.functions import *
import copy
from lib.const import *
import math

Burn, Sleep, Toxic, Poison, Paralyse, Frozen = range(6)


class Pokemon:
    def __init__(self, info):
        # pokemon name
        self.name = (info['Name'].split('-Mega')[0]).split('-Ash')[0]
        # revealed name, e.g. illusion
        self.base_name = self.name

        self.gender = info['Gender']
        self.evs = {key: None2Zero(value) for key, value in info.items() if
                    key in ['atk', 'def', 'spa', 'spd', 'spe', 'hp']}
        self.ivs = {key[1:]: None2Zero(value, 31) for key, value in info.items() if
                    key in ['iatk', 'idef', 'ispa', 'ispd', 'ispe', 'ihp']}
        self.nature = info['Nature']

        # move names
        self.moves = []
        for i in range(4):
            key = 'Move' + str(i + 1)
            if key in info:
                self.moves.append(info[key].replace('[', '').replace(']', ''))

        # move infos
        self.move_infos = [Moves[move_to_key(move)] for move in self.moves]

        self.pp = [int(move['pp'] * 1.6) for move in self.move_infos]
        self.maxpp = copy.deepcopy(self.pp)
        self.lv = info['Lv']

        # item carried
        self.base_item = info['Item']
        # current useful item in battle, could be temporarily set to None, e.g. Magic Room
        self.item = info['Item']
        # used item
        self.used_item = None

        # ability in dex
        self.base_ability = info['Ability']
        # base ability during this switch on, could be changed by other abilities, e.g. mummy
        self.current_ability = info['Ability']
        # ability in battle, could be temporarily set to None, e.g. Moldbreaker
        self.ability = info['Ability']
        self.ability_revealed = False

        # load dex info
        pkm_info = pokedex[self.name.replace(' ', '').replace('-', '').lower()]
        # gender
        if 'gender' not in pkm_info and not self.gender:
            self.gender = random.choice(['M', 'F'])
        # specie stat
        self.sp = pkm_info['baseStats']
        # types of pkm in dex
        self.base_attr = pkm_info['types']
        if self.name == 'Silvally' and self.item in memories:
            self.base_attr = [memories[self.item]]
        if self.name == 'Arceus' and (self.item in plates or self.item in z_crystals):
            self.base_attr = [plates[self.item]]

        # types of pkm in battle, could be temporarily changed, e.g. soak
        self.attr = copy.deepcopy(self.base_attr)

        # weight in dex
        self.base_weight = pkm_info['weightkg']
        # weight in battle, could be temporarily changed, e.g. light metal
        self.weight = self.base_weight
        self.can_evo = 'evos' in pkm_info

        #  base stats
        self.base_stats = gen_stats(self.sp, self.evs, self.ivs, self.lv, self.nature)
        # stats in battle, calculated before any move
        self.stats = copy.deepcopy(self.base_stats)

        # HP
        self.maxHP = self.stats['hp']
        self.HP = self.stats['hp']

        # stat levels
        self.stat_lv = {
            'atk': 0,
            'def': 0,
            'spa': 0,
            'spd': 0,
            'spe': 0,
            'evasion': 0,
            'accuracy': 0,
            'ct': 0
        }

        # battle stat
        self.status = None
        self.status_turn = 0

        # move used last turn
        self.used_move = None
        self.last_move = None
        # move to use this turn
        self.next_move = None

        # if transformed
        self.transform = False

        # move traps pkm
        self.trap_move = None
        self.trap_user = None

        # metronome turn
        self.metronome = 0

        # continue protect turn
        self.protect_move = None
        self.protect_turn = 0

        # if unburden activates
        self.unburden = False

        # if flash fire activates
        self.flash_fire = False

        # lock skill e.g. outrage, ice ball
        self.lock_move = None
        self.lock_round = 0

        # choice item locked move
        # Q: Why not use last move?
        # A: Magic Room
        self.choice_move = None

        # move disabled by curse skin, disable etc.
        self.disable_move = None

        # move during charge, e.g. solar beam
        self.charge = None
        self.charge_round = 0

        # multi-hit buff, e.g. triple kick
        self.multi_count = 0

        # move name if pkm is off field
        self.off_field = None

        # True if pkm is alive
        self.alive = True

        # True if my pkm died last turn
        self.retalitate = False

        # True if player can gen action next turn
        self.can_gen_action = True
        # True if player can gen action next turn
        self.can_gen_move = True
        # True if pkm can switch
        self.can_switch = True

        # True if it's the first turn after pkm switches on
        self.switch_on = True
        # True if pkm is about to switch (for pursuit)
        self.to_switch = False
        # True if pkm should activate its ability
        self.activate = True
        # True if pkm still can move this turn
        self.turn = False
        # first turn switch on

        # dmg bear this turn
        self.round_dmg = {'Physical': 0, 'Special': 0}

        # volatile status
        self.vstatus = {'aquaring': 0, 'attract': 0, 'banefulbunker': 0, 'bide': 0, 'partiallytrapped': 0, 'charge': 0,
                        'confusion': 0, 'curse': 0, 'defensecurl': 0, 'destinybond': 0, 'protect': 0, 'cantescape': 0,
                        'disable': 0, 'electrify': 0, 'embargo': 0, 'encore': 0, 'endure': 0, 'flinch': 0,
                        'focusenergy': 0, 'followme': 0, 'foresight': 0, 'gastroacid': 0, 'grudge': 0, 'healblock': 0,
                        'helpinghand': 0, 'imprison': 0, 'ingrain': 0, 'kingsshield': 0, 'laserfocus': 0,
                        'leechseed': 0, 'lockedmove': 0, 'magiccoat': 0, 'lockon': 0,
                        'magnetrise': 0, 'maxguard': 0, 'minimize': 0, 'miracleeye': 0, 'nightmare': 0, 'noretreat': 0,
                        'obstruct': 0, 'octolock': 0, 'powder': 0, 'powertrick': 0, 'ragepowder': 0, 'smackdown': 0,
                        'snatch': 0, 'spikyshield': 0, 'spotlight': 0, 'stockpile': 0, 'substitute': 0, 'tarshot': 0,
                        'taunt': 0, 'telekinesis': 0, 'torment': 0, 'yawn': 0, 'roost': 0, 'mustrecharge': 0}

        # register to current game
        self.pkm_id = -1
        self.player = None
        self.log = None

        # masks of the valid move and z-use
        self.move_mask = np.ones(4)
        self.z_mask = np.zeros(4)
        if self.item in z_crystals:
            sk_type = z_crystals[self.item]
            for move_id, move in enumerate(self.move_infos):
                if move['type'] == sk_type:
                    self.z_mask[move_id] = 1

    def set_ability(self, move=None, sub=None):
        if move in ['Simple Beam', 'Worry Seed']:
            if {self.ability, sub}.intersection(
                    {'Truant', 'Stance Change', 'Multitype', 'Comatose', 'Shields Down', 'Disguise',
                     'Schooling', 'RKS System', 'Battle Bond', 'Power Construct'}):
                return False
        if move == 'Skill Swap':
            if {self.ability, sub}.intersection(
                    {'Zen Mode', 'Illusion', 'Stance Change', 'Multitype', 'Comatose', 'Shields Down',
                     'Disguise', 'Schooling', 'RKS System', 'Battle Bond', 'Power Construct'}):
                return False
        if move == 'Gastro Acid':
            if self.ability in ['Stance Change', 'Multitype', 'Comatose', 'Shields Down', 'Disguise', 'Schooling',
                                'RKS System', 'Battle Bond', 'Power Construct']:
                return False
        if move == 'Entrainment':
            if sub in ['Illusion', 'Power of Alchemy', 'Zen Mode', 'Trace', 'Flower Gift', 'Forecast', 'Disguise',
                       'Power Construct', 'Receiver'] or self.ability in ['Truant', 'Stance Change', 'Comatose',
                                                                          'Multitype', 'Zen Mode', 'Shields Down',
                                                                          'Disguise',
                                                                          'Schooling', 'RKS System', 'Battle Bond']:
                return False

        temp = self.current_ability
        self.current_ability = sub
        self.ability = sub
        # TODO: Moldbreak?

        # air lock
        if temp in ('Air Lock', 'Cloud Nine'):
            self.env.set_air_lock(-1)
        if sub in ('Air Lock', 'Cloud Nine'):
            self.env.set_air_lock(1)
        self.log.add(actor=self, event='change_ability', val=sub)
        return temp

    # for aegislash
    def stance_change(self):
        if self.name == 'Aegislash':
            target = 'Aegislash-Blade'
        else:
            target = 'Aegislash'
        self.log.add(actor=self, event='Stance Change', type=logType.ability)
        self.log.add(actor=self, event='self_transform', val=target)
        self.name = target
        pkm_info = pokedex[target.replace('-', '').lower()]
        self.sp = pkm_info['baseStats']
        self.base_attr = pkm_info['types']
        self.attr = copy.deepcopy(self.base_attr)
        self.base_weight = pkm_info['weightkg']

        # state
        self.base_stats = gen_stats(self.sp, self.evs, self.ivs, self.lv, self.nature)
        self.stats = copy.deepcopy(self.base_stats)

    # for ditto
    def transpose(self, target):
        self.transform = True
        self.log.add(actor=self, event='transform', target=target)
        self.base_info = {
            'stats': self.stats,
            'gender': self.gender,
            'lv': self.lv,
            'nature': self.nature,
            'weight': self.base_weight,
            'moves': self.moves,
            'move_infos': self.move_infos,
            'pp': self.pp,
            'maxpp': self.maxpp,
        }

        self.name = target.name
        self.gender = target.gender
        self.stats = copy.deepcopy(target.stats)
        self.stat_lv = copy.deepcopy(target.stat_lv)
        self.attr = target.attr
        self.set_ability(move=None, sub=target.current_ability)
        self.lv = target.lv
        self.nature = target.nature
        self.base_weight = target.base_weight
        self.moves = target.moves
        self.move_infos = target.move_infos
        self.pp = target.pp
        self.maxpp = target.maxpp

    def bond_evolve(self):
        if self.name == 'Greninja':
            self.log.add(actor=self, event='Battle Bond', type=logType.ability)
            self.log.add(actor=self, event='self_transform', val='Greninja-Ash')
            self.name = 'Greninja-Ash'
            self.base_name = self.name
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
        self.base_name = mega_name
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

        temp = self.base_item
        if sub:
            self.base_item = sub
            self.item = sub
            self.log.add(actor=self, event='obtain', val=sub)
        else:
            self.base_item = None
            self.item = None
            if self.ability == 'Unburden':
                self.unburden = True
        return temp

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
        self.can_switch = True
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

    def cure_status(self, status=None):
        if self.status and (not status or self.status == status):
            self.log.add(actor=self, event='-status', val=self.status)
            self.status = None

    def cure_vstatus(self, vs):
        self.log.add(actor=self, event='-vstatus', val=vs)
        self.vstatus[vs] = 0

    # TODO: Differ between return True and Nolog
    def add_status(self, status, env, user=None):
        if not self.alive:
            return False
        if self.vstatus['substitute'] and user:
            return False
        if not imm_ground(
                self, env) and env.terrain == 'mistyterrain' or env.terrain == 'electricterrain' and status == 'slp':
            self.log.add(actor=self, event='+' + env.terrain)
            return False
        if self.ability == 'Flower Veil' and 'Grass' in self.attr:
            self.log.add(actor=self, event=self.ability, type=logType.ability)
            return False
        if self.ability == 'Leaf Guard' and env.weather == 'sunnyday':
            self.log.add(actor=self, event=self.ability, type=logType.ability)
            return False
        if status == 'slp' and self.ability in ['Insomnia', 'Vital Spirit', 'Sweet Veil']:
            self.log.add(actor=self, event=self.ability, type=logType.ability)
            return False
        if status == 'brn':
            if self.ability in ['Water Bubble', 'Water Veil']:
                self.log.add(actor=self, event=self.ability, type=logType.ability)
                return False
            if 'Fire' in self.attr:
                return False
        if status in ['psn', 'tox']:
            if self.ability == 'Immunity':
                self.log.add(actor=self, event=self.ability, type=logType.ability)
                return False
            if {'Poison', 'Steel'}.intersection(self.attr):
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
            return True

        if self.item == 'Lum Berry':
            self.use_item()
            self.cure_status()

        return True

    def add_vstate(self, vstatus, cond=None, user=None):
        # fail if already dead
        if not self.alive:
            return False

        # fail if already had same v-status
        if self.vstatus[vstatus] != 0:
            self.log.add(actor=self, event='++' + vstatus)
            # here True means no log
            return True

        if self.vstatus['substitute'] and vstatus in ['confusion', 'flinch', 'leechseed', 'drowsy', 'nightmare',
                                                      'lockon', 'healblock', 'embargo',
                                                      'telekinesis', 'cantescape']:
            return False

        # oblivous immues attract and taunt
        if self.ability == 'Oblivious' and vstatus in ['attract', 'taunt']:
            self.log.add(actor=self, event=self.ability, type=logType.ability)

        # the turn of v-status, default 1
        turn = 1
        # v-status detail for log
        val = ''

        # the turn is given in cond
        if cond and 'duration' in cond:
            turn = cond['duration']

        if vstatus == 'confusion':
            if self.ability == 'Own Tempo':
                self.log.add(actor=self, event=self.ability, type=logType.ability)
                return False
            turn = random.randint(1, 4)
        elif vstatus in ['smackdown', 'foresight', 'curse']:
            turn = 10000
        elif vstatus == 'attract':
            if self.gender and user.gender and self.gender != user.gender:
                turn = 10000
            else:
                return False
        elif vstatus == 'nightmare':
            if self.status['slp'] > 0:
                turn = 10000
            else:
                return False
        elif vstatus in ['protect', 'spikeshield', 'kingsshield', 'banefulbunker', 'endure']:
            # TODO: Quick Guard etc. are also influenced by chance, but don't count up
            if random.uniform(0, 1) >= math.pow(1 / 3, self.protect_turn):
                self.protect_turn = 0
                print('fail')
                return False
            else:
                self.protect_turn += 1
                if vstatus != 'endure':
                    self.protect_move = vstatus

        elif vstatus == 'partiallytrapped':
            turn = random.randint(4, 5)
            trap_move = user.next_move['name']
            self.trap_move = trap_move
            self.trap_user = user
            val = trap_move

        elif vstatus == 'substitute':
            if self.HP > self.maxHP / 4:
                self.damage(perc=1 / 4)
                turn = self.maxHP / 4
            else:
                self.log.add(actor=self, event='--substitute')
                return True
        elif vstatus == 'disable':
            self.disable_move = self.last_move
            turn = 5

        self.log.add(actor=self, event=vstatus, val=val)
        self.vstatus[vstatus] = turn

        print(vstatus, self.vstatus[vstatus])

        # remove bad v-status
        if self.item == 'Mental Herb' and vstatus in ['attract', 'disable', 'encore', 'healblock', 'taunt', 'torment']:
            self.use_item()
            self.cure_vstatus(vstatus)

        return True

    # heal the pkm
    '''
    Inputs: 
        val: the value of heal
        perc: the percentage of heal
        target: the source of the heal, deal with Liquid Ooze
    '''

    def heal(self, val=0, perc=0, target=None, move=False):
        def handle_heal(val, perc, target):
            if not self.alive:
                return True
            if perc:  # 百分比治疗
                val = self.maxHP * perc
            if self.item == 'Big Root':
                val = val * 1.3
            val = max(int(val), 1)
            if target and target.ability == 'Liquid Ooze':
                self.log.add(actor=self, event='ooze', type=logType.ability)
                self.damage(val)
            else:
                val = min(val, self.maxHP - self.HP)
                if val == 0:
                    return False
                self.HP += val
                self.log.add(actor=self, event='heal', val=round(100 * val / self.maxHP, 1))
            return True

        if not handle_heal(val, perc, target) and move:
            self.log.add(actor=self, event='0heal')
            return False
        return True

    # pkm boost stats
    '''
    Inputs: 
        stat: the stat to boost
        lv: the lv of boost, range(-6,6)
        src: the pkm  the boost
    '''

    def boost(self, stat, lv, src=None, z_move=False, val=None):
        if not self.alive:
            return

        if self.vstatus['substitute'] and src is not self:
            self.log.add(actor=self, event='+substitute_block', target=src, val=val)
            return

        def ability_log(stat):
            self.log.add(actor=self, event=self.ability, type=logType.ability)
            self.log.add(actor=self, event='-0', val=full_stat[stat])

        def lv_log(stat, lv):
            if 3 < lv < 6:
                lv = 3
            elif lv >= 6 and lv != 7:
                lv = 6
            elif -6 <= lv < -3:
                lv = -3
            lv = '+' + str(lv) if lv > 0 else str(lv)
            self.log.add(actor=self, event=lv, val=full_stat[stat])

        def handle_boost(stat, lv, src=src, val=None):
            if self.ability == 'Contrary':
                self.log.add(actor=self, event=self.ability, type=logType.ability)
                lv = -lv

            if self.ability == 'Simple':
                self.log.add(actor=self, event=self.ability, type=logType.ability)
                lv = 2 * lv
            if lv > 0:
                if self.stat_lv[stat] == 6:
                    lv_log(stat, 7)
                else:
                    self.stat_lv[stat] = min(self.stat_lv[stat] + lv, 6)
                    lv_log(stat, lv)
            else:
                if self.item == 'White Herb':
                    self.use_item()
                    self.log.add(event='+whiteherb')
                    return
                if self.ability == 'Flower Veil' and 'Grass' in self.attr:
                    ability_log(stat)
                    return
                if self.ability in ['White Smoke', 'Full Metal Body', 'Clear Body'] and src:
                    ability_log(stat)
                    return
                if self.ability == 'Mirror Armor' and src:
                    self.log.add(actor=self, event='Mirror Armor', type=logType.ability)
                    src.boost(stat, lv)
                    return
                if self.ability == 'Keen Eye' and stat == 'accuracy' and src:
                    ability_log(stat)
                    return
                if self.ability == 'Hyper Cutter' and stat == 'atk' and src:
                    ability_log(stat)
                    return
                if self.ability == 'Big Pecks' and stat == 'atk':
                    ability_log(stat)
                    return

                if self.stat_lv[stat] == -6:
                    lv_log(stat, -7)
                else:
                    self.stat_lv[stat] = max(self.stat_lv[stat] + lv, -6)
                    lv_log(stat, lv)
                    val = min(-lv, 6 + self.stat_lv[stat])
                    if self.ability == 'Competitive' and src is not None:
                        self.log.add(actor=self, event='Competitive', type=logType.ability)
                        self.boost('spa', 2 * val)

                    if self.ability == 'Defiant' and src is not None:
                        self.log.add(actor=self, event='Defiant', type=logType.ability)
                        self.boost('atk', 2 * val)

        handle_boost(stat, lv, src)

    def damage(self, val=0, perc=False, const=0, attr=None, user=None, category=None):
        if not self.alive:
            return False
        if self.ability == 'Magic Guard' and not user:
            return False
        if val < 0:
            return False
        if perc:
            val = int(self.maxHP * perc)

        if const:
            val = const

        val = max(val, 1)

        # judge where have substitute before this damage
        # stealth rock
        if not user:
            if attr == 'Rock':
                for my_attr in self.attr:
                    val *= get_attr_fac(attr, my_attr)
            # brn
            if attr == 'Fire' and self.ability == 'Heatproof':
                val *= 0.5

        val = int(val)
        # substitute block damage
        if user and user.ability != 'Infiltrator' and self.vstatus['substitute'] > 0:
            self.vstatus['substitute'] = max(0, self.vstatus['substitute'] - val)
            self.log.add(actor=self, event='+substitute')
            if self.vstatus['substitute'] == 0:
                self.log.add(actor=self, event='-substitute')
            return -1
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
                if user and user is not self and user.alive:
                    if self.vstatus['destinybond']:
                        self.log.add(actor=self, event='destinybond', target=user)
                        user.faint()
                    if user.ability == 'Battle Bond':
                        user.bond_evolve()
                    if user.ability == 'Moxie':
                        self.log.add(actor=user, event='Moxie', type=logType.ability)
                        user.boost('atk', 1)
                    if user.ability == 'Beast Boost':
                        max_stat = 'atk'
                        max_val = 0
                        for stat, val in user.base_stats.items():
                            if stat != 'hp' and val > max_val:
                                max_stat = stat
                                max_val = val
                        self.log.add(actor=user, event='Beast Boost', type=logType.ability)
                        user.boost(max_stat, 1)
                foe_pivot = self.player.get_opponent_pivot()
                if foe_pivot.alive and foe_pivot.ability == 'Soul-Heart':
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

        if self.ability == 'Illusion':
            self.log.add(actor=user, event=self.ability, type=logType.ability)
            self.name = self.base_name
            self.log.add(actor=user, event='+illusion')

        if self.ability == 'Color Change' and user:
            self.log.add(actor=user, event=self.ability, type=logType.ability)
            self.change_type(attr)

        if category == 'Physical' and self.ability == 'Weak Armor':
            self.log.add(actor=user, event=self.ability, type=logType.ability)
            self.boost('def', -1)
            self.boost('spe', 2)

        # eat HP restore berry
        if self.HP <= 1 / 2 * self.maxHP and self.item == 'Sitrus Berry':
            self.use_item()
            self.heal(perc=1 / 4)

        if self.HP <= 1 / 4 * self.maxHP or self.HP <= 1 / 2 * self.maxHP and self.ability == 'Gluttony':
            if self.item in hp_berry:
                self.use_item()
                self.heal(perc=1 / 3)

        if self.ability == 'Emergency Exit' and self.HP < self.maxHP / 2 <= self.HP + val:
            self.log.add(actor=foe_pivot, event=self.ability, type=logType.ability)
            self.player.game.call_switch(self.player)
            return

        # eat ability boost berry
        # Q: Why separate from HP berry?
        # A: Emergency Exit judges HP berry first
        if self.HP <= 1 / 4 * self.maxHP or self.HP <= 1 / 2 * self.maxHP and self.ability == 'Gluttony':
            if self.item in stat_berry:
                self.use_item()
                self.boost(stat_berry[self.item], 1)

        if category:
            self.round_dmg[category] += val

        return val

    def prep(self, env, target, next_move):
        self.calc_stat(env, target)
        self.turn = True
        self.next_move = None
        if next_move['type'] != ActionType.Switch:
            self.next_move = next_move['item']

    def end_turn(self, env, target):
        if not self.alive:
            return
        if self.activate:
            self.activate = False
        else:
            self.switch_on = False
        # TODO: Other forms of protect
        if self.last_move not in protect_moves:
            self.protect_turn = 0
        self.protect_move = None
        self.used_move = False
        self.retalitate = False
        self.can_switch = True

        if self.item == 'Leftovers':
            if self.HP < self.maxHP:
                self.log.add(actor=self, event='leftovers')
                self.heal(0, perc=1 / 16)

        if self.ability == 'Poison Heal' and self.status in ['tox', 'psn'] and self.HP < self.maxHP:
            self.log.add(actor=self, event=self.ability, type=logType.ability)
            self.heal(perc=1 / 8)

        if self.ability == 'Shed Skin' and random.uniform(0, 1) < 1 / 3:
            self.log.add(actor=self, event=self.ability, type=logType.ability)
            self.cure_status()

        if env.terrain == 'grassyterrain' and self.alive:
            if not imm_ground(self, env):
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
            self.status_turn += 1
            if self.ability != 'Poison Heal':
                self.log.add(actor=self, event='+psn')
                self.damage(val=0, perc=(self.status_turn - 1) / 16)

        if self.status == 'psn' and self.alive:
            if self.ability != 'Poison Heal':
                self.log.add(actor=self, event='+psn')
                self.damage(val=0, perc=1 / 8)

        if self.status == 'brn':
            self.log.add(actor=self, event='+brn')
            self.damage(val=0, perc=1 / 16, attr='Fire')

        if self.status == 'slp' and self.vstatus['nightmare'] and self.alive:
            self.log.add(actor=self, event='+nightmare')
            self.damage(0, 1 / 8)

        if self.ability == 'Solar Power' and env.weather is 'sunnyday' and self.alive:
            self.log.add(actor=self, event='solarpower')
            self.damage(0, 1 / 8)

        if self.ability == 'Dry Skin' and env.weather is 'sunnyday' and self.alive:
            self.log.add(actor=self, event='dryskin')
            self.damage(0, 1 / 8)

        if self.ability == 'Dry Skin' and env.weather is 'RainDance' and self.alive:
            self.log.add(actor=self, event='dryskin')
            self.heal(0, 1 / 8)

        if env.weather == 'RainDance' and self.ability == 'Rain Dish' and self.alive:
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

        if env.weather == 'RainDance' and self.ability == 'Hydration' and self.alive:
            if self.status:
                self.log.add(actor=self, event='Hydration', type=logType.ability)
                self.cure_status()

        if self.vstatus['leechseed'] and self.alive and target.alive:
            self.log.add(actor=self, event='+leechseed')
            dmg = self.damage(val=0, perc=1 / 8)
            target.heal(dmg)

        if self.vstatus['partiallytrapped'] and self.alive:
            if not target.alive or target is not self.trap_user:
                self.trap_move = None
                self.trap_user = None
                self.vstatus['partiallytrapped'] = 0
            else:
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

        if self.item == 'Toxic Orb' and self.alive:
            if not self.status:
                self.log.add(actor=self, event='toxicorb')
                self.add_status('tox', env)

        if self.item == 'Flame Orb' and self.alive:
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

        if self.alive and self.ability == 'Harvest' and self.used_item and 'Berry' in self.use_item:
            if env.weather == 'sunnyday' or random.randint(0, 1) == 0:
                self.log.add(actor=self, event=self.ability, type=logType.ability)
                self.lose_item(self.used_item)
                self.used_item = None

        self.round_dmg = {'Physical': 0, 'Special': 0}
        # TODO: ADD bide

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

        self.can_gen_action = not self.vstatus['mustrecharge']
        self.can_gen_move = not (self.next_move and self.ability == 'Truant')

        self.can_switch = True
        if target.ability == 'Magnet Pull' and 'Steel' in target.attr:
            self.can_switch = False
        if target.ability == 'Arena Trap' and not imm_ground(target, env):
            self.can_switch = False
        if target.ability == 'Shadow Tag' and not target.ability == 'Shadow Tag':
            self.can_switch = False
        if self.vstatus['partiallytrapped']:
            self.can_switch = False
        if self.item == 'Shed Shell':
            self.can_switch = True
        if self.lock_move or self.vstatus['mustrecharge']:
            self.can_switch = False

    def calc_stat(self, env, target=None, raw=False, moldbreak=False):
        _, self.Atk, self.Def, self.Satk, self.Sdef, self.Spe = self.stats.values()
        # print(self.name, self.Atk, self.Def, self.Satk, self.Sdef, self.Spe)

        Atk_lv, Def_lv, Satk_lv, Sdef_lv, Spe_lv, Eva_lv, Acc_lv, _ = self.stat_lv.values()

        if not raw:
            self.Atk *= calc_stat_lv(Atk_lv)
            self.Def *= calc_stat_lv(Def_lv)
            self.Satk *= calc_stat_lv(Satk_lv)
            self.Sdef *= calc_stat_lv(Sdef_lv)
            self.Spe *= calc_stat_lv(Spe_lv)
            self.Eva = calc_stat_lv(Eva_lv)
            self.Acc = calc_stat_lv(Acc_lv)

        if moldbreak and self.ability in ['Battle Armor', 'Clear Body', 'Damp', 'Dry Skin', 'Filter', 'Flash Fire',
                                          'Flower Gift', 'Heatproof', 'Hyper Cutter', 'Immunity', 'Inner Focus',
                                          'Insomnia',
                                          'Keen Eye', 'Leaf Guard', 'Levitate', 'Lightning Rod', 'Limber',
                                          'Magma Armor',
                                          'Marvel Scale', 'Motor Drive', 'Oblivious', 'Own Tempo', 'Sand Veil',
                                          'Shell Armor',
                                          'Shield Dust', 'Simple', 'Snow Cloak', 'Solid Rock', 'Soundproof',
                                          'Sticky Hold',
                                          'Storm Drain', 'Sturdy', 'Suction Cups', 'Tangled Feet', 'Thick Fat',
                                          'Unaware',
                                          'Vital Spirit', 'Volt Absorb', 'Water Absorb', 'Water Veil', 'White Smoke',
                                          'Wonder Guard', 'Big Pecks', 'Contrary', 'Friend Guard', 'Heavy Metal',
                                          'Light Metal',
                                          'Magic Bounce', 'Multi Scale', 'Sap Sipper', 'Telepathy', 'Wonder Skin',
                                          'Aroma Veil',
                                          'Bulletproof', 'Flower Veil', 'Fur Coat', 'Overcoat', 'Sweet Veil',
                                          'Dazzling',
                                          'Disguise', 'Fluffy', 'Queenly Majesty', 'Water Bubble', 'Mirror Armor',
                                          'Punk Rock',
                                          'Ice Scales', 'Ice Face', 'Pastel Veil ']:
            self.ability = None
        else:
            self.ability = self.current_ability

        # Ability Buff
        if self.ability == 'Defeatist' and self.HP / self.maxHP <= 1 / 2:
            self.Atk *= 0.5
            self.Satk *= 0.5
        if self.ability in ['Huge Power', 'Pure Power']:
            self.Atk *= 2
        if self.ability == 'Guts' and self.status:
            self.Atk *= 1.5
        if self.ability == 'Marvel Scale' and self.status:
            self.Def *= 1.5
        if self.ability == 'Quick Feet' and self.status:
            self.Spe *= 1.5
        if self.ability == 'Tangled Feet' and self.vstatus['confusion']:
            self.Eva *= 2
        if self.ability == 'Solar Power' and env.weather == 'sunnyday':
            self.Satk *= 2
        if self.ability == 'Chlorophyll' and env.weather == 'sunnyday':
            self.Spe *= 2
        if self.ability == 'Swift Swim' and env.weather == 'RainDance':
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
        if env.pseudo_weather['magicroom'] or self.ability == 'Klutz' or self.vstatus[
            'embargo'] or self.item and 'Berry' in self.item and (
                self.ability == 'Unnerve' or target and target.ability == 'Unnerve'):
            self.item = None
        else:
            self.item = self.base_item

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

        if self.status == 'par' and self.ability != 'Quick Feet':
            self.Spe *= 0.5

        if env.pseudo_weather['wonderroom']:
            self.Def, self.Sdef = self.Sdef, self.Def

        self.weight = self.base_weight
        if self.ability == 'Heavy Metal':
            self.weight *= 2
        if self.ability == 'Light Metal':
            self.weight /= 2

        self.Atk = int(self.Atk)
        self.Def = int(self.Def)
        self.Satk = int(self.Satk)
        self.Sdef = int(self.Sdef)
        self.Spe = int(self.Spe)

    def reset_stat_lv(self, nega=False):
        for stat in self.stat_lv:
            if not (nega and self.stat_lv[stat] > 0):
                self.stat_lv[stat] = 0

    def reset(self):
        if self.alive:
            self.reset_stat_lv()
            for vstatus in self.vstatus:
                self.vstatus[vstatus] = 0

            self.attr = self.base_attr

            if self.status == 'tox':
                self.status_turn = 1
            self.protect_move = 0
            self.protect_turn = 0
            self.last_move = None
            self.next_move = None
            self.metronome = 0
            self.unburden = False
            self.flash_fire = False

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

            self.can_gen_action = True
            self.switch_on = False
            self.can_switch = True
            self.to_switch = False
            self.activate = True
            self.turn = False
            self.used_move = False
            self.retalitate = False

            if self.ability == 'Natural Cure':
                if self.status:
                    self.log.add(actor=self, event=self.ability, type=logType.ability)
                    self.cure_status()

            if self.ability == 'Regenerator':
                if self.HP < self.maxHP:
                    self.log.add(actor=self, event=self.ability, type=logType.ability)
                    self.heal(perc=1 / 3)

            self.current_ability = self.base_ability
            self.ability = self.base_ability

    def switch(self, env, old_pivot=None, foe=None, boton=False):
        if old_pivot:
            if boton:
                self.stat_lv = old_pivot.stat_lv
                self.vstatus['substitute'] = copy.deepcopy(old_pivot['substitute'])
                self.vstatus['leechseed'] = copy.deepcopy(old_pivot['leechseed'])
            if old_pivot.ability in ['Cloud Nine', 'Air Lock']:
                self.env.set_air_lock(-1)
            old_pivot.reset()
            if old_pivot.transform:
                old_pivot.transform = False

                base_info = old_pivot.base_info
                old_pivot.name = old_pivot.base_name
                old_pivot.stats = base_info['stats']
                old_pivot.gender = base_info['gender']
                old_pivot.nature = base_info['nature']
                old_pivot.lv = base_info['lv']
                old_pivot.base_weight = base_info['weight']
                old_pivot.moves = base_info['moves']
                old_pivot.move_infos = base_info['move_infos']
                old_pivot.pp = base_info['pp']
                old_pivot.maxpp = base_info['maxpp']

            slotcond = env.get_slotcond(self)
            if slotcond['healingwish']:
                self.log.add(actor=self, event='+healingwish')
                self.heal(self.maxHP)
                self.cure_status()
                slotcond['healingwish'] = 0
            elif slotcond['lunardance']:
                self.log.add(actor=self, event='+lunardance')
                self.heal(self.maxHP)
                self.cure_status()
                slotcond['lunardance'] = 0
            elif slotcond['heal']:
                self.heal(self.maxHP)
                slotcond['heal'] = 0

            if not old_pivot.alive:
                self.retalitate = True

        if self.ability == 'Illusion':
            self.name = self.player.get_last_alive().name
        self.can_switch = True
        self.to_switch = False

        self.switch_on = True
        self.activate = True
        self.turn = False
        self.last_move = None

        self.stats = copy.deepcopy(self.base_stats)

        sidecond = env.get_sidecond(self)
        if not imm_ground(self, env):
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
            if self.ability != 'Magic Guard':
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

    def change_type(self, attr, add=False):
        if add == True:
            self.log.add(actor=self, event='add_type', val=attr)
            self.attr.append(attr)
        elif add == -1:
            self.log.add(actor=self, event='remove_type', val=attr)
            self.attr.remove(attr)
        else:
            self.log.add(actor=self, event='change_type', val=attr)
            self.attr = [attr]

    # for sleep talk
    # TODO: Cat hand
    def get_random_move(self, neq=None):
        p = np.ones(4)
        for move_id, move in enumerate(self.moves):
            if move == neq:
                p[move_id] = 0
        return np.random.choice(self.move_infos, p=p / p.sum())

    def can_lose_item(self):
        return self.item and self.item not in mega_stones and self.item not in z_crystals and not (
                self.name == 'Silvally' and self.item in memories) and not (
                self.name == 'Arceus' and self.item in plates) and self.ability != 'Sticky Hold'

    # if pkm can be forced to switch, e.g. red card
    def can_force_switch(self):
        if self.ability == 'Suction Cups':
            self.log.add(actor=self, event=self.ability, type=logType.ability)
            self.log.add(actor=self, event='-forceswitch')
        elif self.alive:
            return True
        return False
