import random

from pokemon import Pokemon
from functions import *
from data.moves import Moves

from read_team import *
from player import Player
from env import Env
from const import *

from log import BattleLog

Hit, Miss, NoEffect, Onhold = 0, 1, 2, 3


class Utils:
    def __init__(self, log):
        self.log = log

    def step_turn(self, game, env, players, moves):
        pkms = [players[0].get_pivot(), players[1].get_pivot()]
        pkms[0].prep(env)
        pkms[1].prep(env)
        megas = [None, None]
        z_moves = [False, False]
        prior = np.zeros(2)
        if pkms[0].Spe > pkms[1].Spe:
            prior[0] += 0.1
        elif pkms[0].Spe < pkms[1].Spe:
            prior[1] += 0.1
        else:
            prior[random.randint(0, 1)] += 0.1

        if env.pseudo_weather['trickroom'] > 0:
            prior = - prior

        if moves[0]['type'] == ActionType.Switch:
            prior[0] += 50
        else:
            prior[0] += moves[0]['item']['priority']
            if moves[0]['type'] == ActionType.Mega:
                megas[0] = True
            if moves[0]['type'] == ActionType.Z_Move:
                z_moves[0] = True

        if type(moves[1]) == ActionType.Switch:
            prior[1] += 50
        else:
            prior[1] += moves[1]['item']['priority']
            if moves[1]['type'] == ActionType.Mega:
                megas[1] = True
            if moves[1]['type'] == ActionType.Z_Move:
                z_moves[1] = True

        if prior[0] > prior[1]:
            first = 0
        else:
            first = 1
        last = 1 - first
        # mega

        if megas[first]:
            pkms[first].mega_evolve()
            players[first].use_mega()
            self.switch_on(players, env)

        if megas[last]:
            pkms[last].mega_evolve()
            players[last].use_mega()
            self.switch_on(players, env)

        # switch

        if type(moves[first]) is int:
            if moves[last]['name'] != 'Pursuit' or z_moves[last]:
                players[first].switch(moves[first]['item'])
            else:
                # pursuit
                self.use_move(user=pkms[last], target=pkms[first], move=moves[last]['item'], env=env, game=game,
                              z_move=z_moves[last], last=True)
                if pkms[first].turn:
                    players[first].switch(moves[first]['item'], withdraw=True)
                    pkms[last].turn = False
                return
        else:
            self.use_move(user=pkms[first], target=pkms[last], move=moves[first]['item'], env=env, game=game,
                          z_move=z_moves[first], last=False)

        # move last
        if pkms[last].turn:
            if type(moves[last]) is int:
                players[last].switch(moves[last]['item'])
            else:
                self.use_move(user=players[last].get_pivot(), target=players[first].get_pivot(),
                              move=moves[last]['item'], env=env, game=game, z_move=z_moves[last],
                              last=True)

        # end turn
        for pid, player in enumerate(players):
            player.get_pivot().end_turn(env, players[1 - pid].get_pivot())

        done, to_switch = self.check_switch(env, players)

        return done, to_switch

    def match_up(self, env, players, moves):
        for pid, (player, move) in enumerate(zip(players, moves)):
            player.switch(env, move['item'])
        self.switch_on(players, env)
        self.log.step_print()

    def check_switch(self, env, players, moves=[None, None], check=True):
        done = False
        to_switch = []
        for pid, (player, move) in enumerate(zip(players, moves)):
            if move is not None:
                pivot = move['item']
                if pivot == player.pivot:
                    continue
                player.switch(env, pivot, not check)

            if check:
                if not player.get_pivot().alive:
                    if player.lose():
                        self.log.add(actor=player, event='lose')
                        done = True
                    else:
                        to_switch.append(player)

        if not to_switch and not done:
            self.switch_on(players, env)

        return done, to_switch

    def switch_on(self, players, env):
        for pid, player in enumerate(players):
            user = player.get_pivot()
            target = players[1 - pid].get_pivot()
            if user.activate:
                target.can_switch = True
                if user.ability == 'Magnet Pull' and 'Steel' in target.attr:
                    target.can_switch = False
                if user.ability == 'Arena Trap' and not imm_ground(target):
                    target.can_switch = False
                if user.ability == 'Shadow Tag' and not target.ability == 'Shadow Tag':
                    target.can_switch = False

                if user.ability == 'Trace':
                    self.log.add(actor=user, event='Trace', type=logType.ability)
                    self.log.add(actor=user, event='+trace', val=target.ability)
                    user.current_ability = target.ability
                    user.ability = target.ability

                if user.ability == 'Anticipation':
                    for move in target.move_infos:
                        if calc_type_buff(move, user) > 1 or 'ohko' in move:
                            self.log.add(actor=user, event='anticipate', type=logType.ability)
                            break

                if user.ability == 'Frisk':
                    if target.item:
                        self.log.add(actor=user, event='Frisk', type=logType.ability)
                        self.log.add(actor=user, event='identify', val=target.item)

                if user.ability == 'Mold Breaker':
                    self.log.add(actor=user, event='Mold Breaker', type=logType.ability)

                if user.ability == 'Pressure':
                    self.log.add(actor=user, event='Pressure', type=logType.ability)

                if user.ability == 'Unnerve':
                    self.log.add(actor=user, event='Unnerve', type=logType.ability)

                if user.ability == 'Drizzle':
                    self.log.add(actor=user, event=user.ability, type=logType.ability)
                    env.set_weather(weather='Raindance', item=user.item, log=self.log)

                if user.ability == 'Drought':
                    self.log.add(actor=user, event=user.ability, type=logType.ability)
                    env.set_weather(weather='sunnyday', item=user.item, log=self.log)

                if user.ability == 'Snow Warning':
                    self.log.add(actor=user, event=user.ability, type=logType.ability)
                    env.set_weather(weather='hail', item=user.item, log=self.log)

                if user.ability == 'Sand Stream':
                    self.log.add(actor=user, event=user.ability, type=logType.ability)
                    env.set_weather(weather='Sandstorm', item=user.item, log=self.log)

                if user.ability == 'Electric Surge':
                    self.log.add(actor=user, event=user.ability, type=logType.ability)
                    env.set_terrain(terrain='electricterrain', item=user.item, log=self.log)

                if user.ability == 'Grassy Surge':
                    self.log.add(actor=user, event=user.ability, type=logType.ability)
                    env.set_terrain(terrain='grassyterrain', item=user.item, log=self.log)

                if user.ability == 'Misty Surge':
                    self.log.add(actor=user, event=user.ability, type=logType.ability)
                    env.set_terrain(terrain='mistyterrain', item=user.item, log=self.log)

                if user.ability == 'Psychic Surge':
                    self.log.add(actor=user, event=user.ability, type=logType.ability)
                    env.set_terrain(terrain='psychicterrain', item=user.item, log=self.log)

                if user.ability == 'Download':
                    self.log.add(actor=user, event='download', type=logType.ability)
                    if target.Def > target.SpD:
                        user.boost('spa', 1)
                    else:
                        user.boost('atk', 1)

                if user.ability == 'Intimidate':
                    self.log.add(actor=user, event='intimidate', type=logType.ability)
                    target.boost('atk', -1, user)

            if user.switch_on:
                if user.item is 'Air Balloon':
                    self.log.add(actor=user, event='balloon')

                if user.item in ['Electric Seed', 'Grassy Seed']:
                    self.log.add(actor=user, event='use item')
                    user.use_item()
                    user.boost('def', 1)

                if user.item in ['Psychic Seed', 'Misty Seed']:
                    self.log.add(actor=user, event='use item')
                    user.use_item()
                    user.boost('spd', 1)

            user.activate = False

    def step_turn_pkm(self, env, pkms, moves):
        pkms[0].prep(env)
        pkms[1].prep(env)
        moves = [Moves[moves[0]], Moves[moves[1]]]
        prior = np.zeros(2)
        if pkms[0].Spe > pkms[1].Spe:
            prior[0] += 0.1
        elif pkms[0].Spe < pkms[1].Spe:
            prior[1] += 0.1
        else:
            prior[random.randint(0, 1)] += 0.1

        if env.pseudo_weather['trickroom'] > 0:
            prior = 1 - prior

        prior[0] += moves[0]['priority']
        prior[1] += moves[1]['priority']

        if prior[0] > prior[1]:
            first = 0
        else:
            first = 1

        last = 1 - first

        self.use_move(user=pkms[first], target=pkms[last], move=moves[first], env=env, game=None, last=False)
        self.use_move(user=pkms[last], target=pkms[first], move=moves[last], env=env, game=None, last=True)

        self.log.step_print()

    def use_move(self, user: Pokemon, target: Pokemon, move, env, game, z_move, last):
        if user.vstatus['flinch']:
            self.log.add(actor=user, event='+flinch')
            if user.ability == 'Steadfast':
                self.log.add(actor=user, event='Steadfast', type=logType.ability)
                user.boost('spe', 1)
            return
        if user.status is 'slp':
            if user.status_turn > 0:
                self.log.add(actor=user, event='+slp')
                user.status_turn -= 1
                return
            else:
                self.log.add(actor=user, event='-slp')
                user.status = None
                user.vstatus['nightmare'] = 0
        if user.status is 'frz':
            if random.uniform(0, 1) <= 0.2:
                self.log.add(actor=user, event='-frz')
            else:
                self.log.add(actor=user, event='+frz')
                return
        if user.vstatus['confusion']:
            if random.uniform(0, 1) >= 0.3:
                self.log.add(actor=user, event='-confusion')
            else:
                self.log.add(actor=user, event='+confusion')
                dmg = self.calc_dmg(user, user, move='ConfusionHit', env=env, last=False)
        self.log.add(actor=user, event='use', val=move['name'])
        if user.vstatus['taunt']:
            if move['category'] == 'Status':
                self.log.add(actor=user, event='+taunt', val=move['name'])
                return
        if target.ability == 'Pressure':
            user.loss_pp(move, 2)
        else:
            user.loss_pp(move, 1)

        if not user.choice_move:
            user.choice_move = move['name']

        if user.ability == 'Protean':
            self.log.add(actor=user, event='Protean', type=logType.ability)
            self.log.add(actor=user, event='change_type', val=move['type'])
            user.attr = [move['type']]

        if move['name'] == 'Splash':
            self.log.add(event='splash')

        if move['name'] in ['Fake Out', 'First Impression'] and not user.switch_on:
            self.log.add(event='fail')
            return

        if move['priority'] > 0 and env.terrain == 'psychicterrain':
            self.log.add(actor=target, event='+psychicterrain')
            return

        user.calc_stat(env)
        target.calc_stat(env)
        if move['target'] == 'self':
            target = user

        self_destruct = None
        if 'selfdestruct' in move:
            self_destruct = move['selfdestruct']
            if self_destruct == 'always':
                user.damage(0, 100)

        count = 1
        if 'multiaccuracy' in move:
            count = move['multihit']

        for i in range(count):
            if not target.alive:
                if i == 0:
                    self.log.add(event='fail')
                break
            useful = self.check_useful(env, user, target, move)
            if useful == Hit:
                if self_destruct == 'ifHit':
                    user.damage(0, 100)
                self.effect_move(user, target, move, env, last)
                if move['name'] in ['U-turn', 'Volt Switch', 'Boton Pass']:
                    game.call_switch(user.player)

            elif useful == Miss:
                self.log.add(actor=target, event='avoid')
                user.multi_count = 0
                if move['name'] in ['Jump Kick', 'High Jump Kick']:
                    self.log.add(actor=user, event='drop')
                    user.damage(0, 1 / 2)
            elif useful == NoEffect:
                self.log.add(actor=target, event='0effect')
                user.set_lock()
                break

    def effect_move(self, user: Pokemon, target: Pokemon, move, env, last):
        ctg = move['category']
        if ctg != 'Status':
            if 'isFutureMove' in move:
                target.add_future(user, move['name'])
            if move['name'] in ['Rollout', 'Ice Ball']:
                user.set_lock(move['name'])

            count = 1
            if 'multihit' in move and 'multiaccuracy' not in move:
                count = move['multihit']
                if user.ability == 'Skill Link':
                    count = 5
                elif type(count) is list:
                    count = np.random.choice([2, 3, 4, 5], p=[1 / 3, 1 / 3, 1 / 6, 1 / 6])

            if move['name'] in ['Psychic Fangs', 'Brick Break']:
                for wall in ['lightscreen', 'reflect', 'auroraveil']:
                    if target.get_sidecond()[wall]:
                        self.log.add(actor=target.player, event='--' + wall)
                    target.get_sidecond()[wall] = 0

            for _ in range(count):
                dmg = self.calc_dmg(user, target, move, env, last)
                target.damage(val=dmg, perc=False, attr='NoAttr', user=user)

            sec_target = target
            if 'secondary' in move:
                effects = [move['secondary']]
            else:
                effects = move['secondaries']
            if 'self' in move:
                effects = move['self']
                sec_target = user
                if type(effects) is not list:
                    effects = [effects]
            if len(effects) > 0:
                for effect in effects:
                    if effect is None:
                        continue
                    chance = effect['chance'] / 100 if 'chance' in effect else 1
                    hit = np.random.choice([True, False], p=[chance, 1 - chance])
                    if hit:
                        if 'self' in effect:
                            effect = effect['self']
                        if 'status' in effect:
                            sec_target.add_status(effect['status'], env)
                        if 'volatileStatus' in effect:
                            sec_target.add_vstate(effect['volatileStatus'])
                        if 'boosts' in effect:
                            for stat, lv in effect['boosts'].items():
                                sec_target.boost(stat, lv)
                        if move['name'] == 'Tri Attack':
                            status = random.randint(0, 2)
                            if status == 0:
                                sec_target.add_status('par', env)
                            elif status == 1:
                                sec_target.add_status('brn', env)
                            else:
                                sec_target.add_status('frz', env)

            # drain move
            if 'drain' in move:
                heal = int(move['drain'][0] / move['drain'][1] * dmg)
                user.heal(heal, False, target)

            if 'recoil' in move:
                recoil = int(move['recoil'][0] / move['recoil'][1] * dmg)
                self.log.add(actor=user, event='recoil')
                user.damage(recoil)

            # lock round move
            if move['name'] in ['Outrage', 'Petal Dance', 'Thrash']:
                if user.lock_round == 3:
                    user.add_vstate('confusion')
                    user.set_lock()
                else:
                    user.set_lock(move['name'])

            if move['name'] in ['Rollout', 'Ice Ball']:
                if user.lock_round == 5:
                    user.set_lock()
            if move['name'] == 'Uproar':
                if user.lock_round == 3:
                    user.set_lock()
            if move['name'] == 'Rapid Spin':
                env.clear_field(user.player, type='spike', log=self.log)

            # same round move
            if move['name'] in ['Triple Axel', 'Triple Kick']:
                user.multi_count += 1

        else:
            if move['target'] == 'self':
                target = user
            if 'boosts' in move:
                boosts = move['boosts']
                for stat in boosts:
                    val = boosts[stat]

                    if move['target'] == 'self':
                        user.boost(stat, val)
                    else:
                        target.boost(stat, val)

            if 'status' in move:
                status = move['status']
                target.add_status(status, env)

            if 'volatileStatus' in move:
                vstatus = move['volatileStatus']
                cond = None
                if 'condition' in move:
                    cond = move['condition']
                target.add_vstate(vstatus, cond)

            #     if 'sideCondition' in move:
            #        side_cond = move['sideCondition']
            if 'condition' in move:
                cond = move['condition']
            else:
                cond = None

            target.add_cond(cond)

            if 'weather' in move:
                weather = move['weather']
                env.set_weather(weather, user.item, self.log)

            if 'pseudoWeather' in move:
                pseudo_weather = move['pseudoWeather']
                env.set_pseudo_weather(pseudo_weather, self.log)

            if 'terrain' in move:
                terrain = move['terrain']
                env.set_terrain(terrain, user.item, self.log)

            if 'sideCondition' in move:
                sidecond = move['sideCondition']
                target.add_sidecond(sidecond)

            # TODO: Multiple types of heal
            if 'heal' in move:
                if target.maxHP == target.HP:
                    self.log.add(event='fail')
                else:
                    target.heal(0, move['heal'][0] / move['heal'][1])
            if move['name'] == 'Belly Drum':
                if user.HP > user.maxHP / 2:
                    if user.stat_lv['atk'] == 6:
                        self.log.add(actor=user, event='belly_fail_atk')
                    else:
                        user.damage(0, perc=1 / 2)
                        user.boost('atk', 6)
                else:
                    self.log.add(actor=user, event='belly_fail_hp')

            if move['name'] == 'Defog':
                target.boost('eva', -1)
                env.clear_field(user.player, type='spike', log=self.log)
                env.clear_field(target.player, type='spike', log=self.log)
                env.clear_field(target.player, type='wall', log=self.log)

            if move['name'] == 'Trick':
                self.log.add(actor=user, event='trick', target=target)
                item = user.lose_item(target.item)
                if item:
                    target.lose_item(item)

            if move['name'] == 'Pain Split':
                self.log.add(actor=user, event='painsplit', target=target)
                avg_hp = (user.HP + target.HP) / 2
                user.HP = avg_hp
                target.HP = avg_hp

            if move['name'] == 'Healing Wish':
                user.healing_wish = True

            if move['name'] == 'Heal Bell':
                self.log.add(event='healbell')
                user.player.cure_all()

            if move['name'] == 'Aromatherapy':
                self.log.add(event='aromatherapy')
                user.player.cure_all()

            if move['name'] == 'Synthesis':
                if env.weather == 'sunnyday':
                    user.heal(0, 3 / 4)
                elif env.weather:
                    user.heal(0, 1 / 4)
                else:
                    user.heal(0, 1 / 2)
            if 'self' in move:
                side_effect = move['self']
                if 'volatileStatus' in side_effect:
                    user.add_vstate(side_effect['volatileStatus'])

        if 'contact' in move['flags']:
            if target.ability in ['Iron Barbs', 'Rough Skin']:
                self.log.add(actor=target, event=target.ability, type=logType.ability)
                user.damage(0, perc=1 / 8)

            if target.item == 'Rocky Helmet':
                self.log.add(actor=user, event='rockyhelmet')
                user.damage(0, perc=1 / 6)

        if move['name'] == 'Knock Off' and target.can_lose_item() and target.alive:
            self.log.add(actor=user, event='knockoff', target=target, val=target.item)
            target.lose_item()

    def check_useful(self, env, user, target, move):
        sk_type = move['type']
        sk_name = move['name']
        sk_ctg = move['category']
        sk_flag = move['flags']
        acc = move['accuracy']
        acc_buff = 1
        # 特性修正

        if sk_name in ['Shadow Force', 'Phantom Force', 'Fly', 'Dig']:
            if user.off_field:
                user.off_field = None
        else:
            user.off_field = sk_name

        if 'charge' in move['flags']:
            if user.charge is None:
                user.charge = move['name']
                if move['name'] in ['Solar Beam', 'Solar Blade']:
                    self.log.add(actor=user, event='solar')
                    if env.weather is 'sunnyday':
                        user.charge = None
                if user.charge is not None:
                    return Onhold
            else:
                user.charge = None

        if target.vstatus['protect'] == True:
            if sk_name == 'Feint':
                self.log.add(actor=user, event='feint', target=target)
                target.unprotect = True
            else:
                self.log.add(actor=target, event='+protect')
                return NoEffect

        if user.ability in ['Mold Breaker', 'Teravolt', 'Turboblaze']:
            target.moldbreak()

        if sk_ctg == 'Status':
            return Hit

        if move['name'] in ['Thunder', 'Hurricane']:
            if env.weather is 'sunnyday':
                acc = 50
            if env.weather is 'Raindance':
                acc = 100

        if move['name'] == 'Blizzard' and env.weather is 'hail':
            acc = 100

        if move['name'] == 'Weather Ball':
            if env.weather is 'hail':
                sk_type = 'Ice'
            elif env.weather is 'sunnyday':
                sk_type = 'Fire'
            elif env.weather is 'Raindance':
                sk_type = 'Water'
            elif env.weather is 'Sandstorm':
                sk_type = 'Rock'

        if sk_type == 'Water':
            if target.ability == 'Water Absorb':
                self.log.add(actor=target, event=target.ability, type=logType.ability)
                target.heal(1 / 4, perc=Hit)
                return NoEffect
        if target.ability == 'Dry Skin':
            target.heal(1 / 4, perc=Hit)
            self.log.add(actor=target, event=target.ability, type=logType.ability)
            return NoEffect
        if target.ability == 'Storm Drain':
            self.log.add(actor=target, event=target.ability, type=logType.ability)
            target.stat_lv['spa'] += 1
            return NoEffect

        if sk_type == 'Fire':
            if target.ability == 'Flash Fire':
                self.log.add(actor=target, event=target.ability, type=logType.ability)
                target.flash_fire = Hit
                return NoEffect

        if sk_type == 'Electric':
            if target.ability == 'Lightning Rod':
                self.log.add(actor=target, event=target.ability, type=logType.ability)
                target.stat_lv['spa'] += 1
                return NoEffect
            if target.ability == 'Motor Drive':
                self.log.add(actor=target, event=target.ability, type=logType.ability)
                target.stat_lv['spe'] += 1
                return NoEffect
            if target.ability == 'Volt Absorb':
                self.log.add(actor=target, event=target.ability, type=logType.ability)
                target.heal(1 / 4, perc=Hit)
                return NoEffect

        if sk_type == 'Grass':
            if target.ability == 'Sap Sipper':
                self.log.add(actor=target, event=target.ability, type=logType.ability)
                target.stat_lv['atk'] += 1
                return NoEffect

        if sk_type == 'Ground':
            if imm_ground(target):
                return NoEffect

        if target.ability == 'Bulletproof' and 'bullet' in sk_flag:
            self.log.add(actor=target, event=target.ability, type=logType.ability)
            return NoEffect

        if target.ability == 'Soundproof' and 'sound' in sk_flag:
            self.log.add(actor=target, event=target.ability, type=logType.ability)
            return NoEffect

        type_buff = 1
        for attr in target.attr:
            if sk_type == 'Ground' and attr == 'Flying' and not imm_ground(target):
                continue
            type_buff *= get_attr_fac(sk_type, attr)
        if type_buff == 0:
            if not (user.ability == 'Scrappy' and sk_type == 'Normal' and 'Ghost' in target.attr):
                return NoEffect
        if target.ability == 'Wonder Guard' and type_buff <= 1:
            self.log.add(actor=target, event=target.ability, type=logType.ability)
            return NoEffect

        if target.ability == 'Wonder Skin' and sk_ctg == 'Status':
            acc_buff *= 0.5

        if user.ability == 'Hustle' and sk_ctg == 'Physical':
            acc_buff *= 0.8

        # 命中判定
        #   if target == user:
        #       return Hit

        user_acc = user.Acc
        target_eva = target.Eva
        if acc is True:
            return Hit

        final_acc = acc * user_acc / target_eva * acc_buff / 100
        if final_acc >= 1:
            return Hit
        hit = np.random.choice([0, 1], p=[final_acc, 1 - final_acc])
        return hit

    def calc_dmg(self, user, target, move, env, last):
        sk_type = move['type']
        sk_name = move['name']
        ctg = move['category']
        flag = move['flags']
        power = move['basePower']

        # specific power
        if 'damage' in move:
            if move['damage'] == 'level':
                return user.lv
            else:
                return int(move['damage'])
        if sk_name == 'Endeavor':
            return target.HP - user.HP

        if sk_name == 'Nature\'s Madness':
            return max(target.HP // 2, 1)

        if 'ohko' in move:
            return target.HP

        if sk_name == 'Knock Off':
            if target.item and target.item not in mega_stones and not (
                    target.name == 'Arceus' and target.item in plates) and not (
                    target.name == 'Silvally' and target.item in memories) and 'ium Z' not in target.item:
                power *= 1.5

        if sk_name == 'Stored Power':
            for key, boost in user.stat_lv.items():
                if boost > 0:
                    power += boost * 20

        if sk_name == 'Return':
            power = 102

        if sk_name == 'Acrobatics' and user.item is None:
            power *= 2

        if sk_name in ['Low Kick', 'Grass Knot']:
            if target.weight < 10:
                power = 20
            elif 10 <= target.weight < 25:
                power = 40
            elif 25 <= target.weight < 50:
                power = 60
            elif 50 <= target.weight < 100:
                power = 80
            elif 100 <= target.weight < 200:
                power = 100
            else:
                power = 120

        if sk_name in ['Heavy Slam', 'Heat Crash']:
            ratio = user.weight / target.weight
            if ratio < 2:
                power = 40
            elif ratio < 3:
                power = 60
            elif ratio < 4:
                power = 80
            elif ratio < 5:
                power = 100
            else:
                power = 120

        if sk_name == 'Electro Ball':
            ratio = user.Spe / target.Spe
            if ratio < 1:
                power = 40
            elif ratio < 2:
                power = 60
            elif ratio < 3:
                power = 80
            elif ratio < 4:
                power = 120
            else:
                power = 150

        if sk_name == 'Gyro Ball':
            power = min(150, int(25 * target.Spe / user.Spe))

        # 相克补正
        type_buff = 1
        for attr in target.attr:
            type_buff *= get_attr_fac(sk_type, attr)

        if sk_name == 'Flying Press':
            for attr in target.attr:
                type_buff *= get_attr_fac('Flying', attr)

        if sk_name == 'Freeze Dry' and target.attr:
            # should be effective
            type_buff *= 4

        if type_buff > 1:
            self.log.add(event='effect')
        if type_buff < 1:
            self.log.add(event='neffect')

        # ct
        ct_lv = 0
        if sk_name in ct_move:
            ct_lv += 1
        if user.vstatus['focusenergy'] != 0:
            ct_lv += 2
        if user.item in ['Scope Lens', 'Razor Claw']:
            ct_lv += 1
        if user.ability == 'Super Luck':
            ct_lv += 1
        ct_rate = get_ct(ct_lv)
        if user.ability == 'Merciless' and (target.poison or target.toxic):
            ct_rate = 1
        if user.ability == 'Sniper':
            ct = 9 / 4
        else:
            ct = 1.5
        ct_buff = np.random.choice([ct, 1], p=[ct_rate, 1 - ct_rate])
        if target.ability in ['Shell Armor', 'Battle Armor']:
            ct_buff = 1

        if ct_buff > 1:
            self.log.add(event='ct')

        # physical/special
        if ctg == 'Physical':
            Atk = user.Atk
            Def = target.Def
        else:
            Atk = user.Satk
            Def = target.Sdef

        if 'defensiveCategory' in move:
            if move['defensiveCategory'] == 'Physical':
                Def = target.Def

        if sk_name == 'Foul Play':
            Atk = target.Atk

        lv = user.lv
        dmg = (2 * lv + 10) / 250 * Atk / Def * power + 2

        # 本系加成
        stab_buff = 1
        if sk_type in user.attr:
            if user.ability == 'Adaptability':
                stab_buff = 2
            else:
                stab_buff = 1.5

        # other
        other_buff = 1

        if sk_name in ['Rollout', 'Ice Ball']:
            other_buff *= math.pow(2, user.lock_round - 1)

        if sk_name in ['Triple Kick', 'Triple Axel']:
            other_buff *= math.pow(2, user.multi_count)

        # status buff
        if user.status is 'brn' and user.ability != 'Guts' and sk_name != 'Facade' and ctg == 'Physical':
            other_buff *= 0.5

        # skill buff
        if sk_name == 'Facade' and (user.status is not None):
            other_buff *= 2

        # item buff
        if ctg == 'Physical' and user.item == 'Muscle Band':
            other_buff = 1.1

        if ctg == 'Special' and user.item == 'Wise Glasses':
            other_buff = 1.1

        if user.item == 'Expert Belt' and type_buff > 1:
            other_buff = 1.2

        if user.item == 'Life Orb':
            other_buff = 1.3

        if user.metronome > 0:
            other_buff = 1 + 0.1 * user.metronome

        if sk_type == 'Fire' and user.item == 'Flame Plate':
            other_buff = 1.2
        if sk_type == 'Grass' and user.item == 'Meadow Plate':
            other_buff = 1.2
        if sk_type == 'Water' and user.item == 'Splash Plate':
            other_buff = 1.2
        if sk_type == 'Ground' and user.item == 'Earth Plate':
            other_buff = 1.2
        if sk_type == 'Bug' and user.item == 'Insect Plate':
            other_buff = 1.2
        if sk_type == 'Ice' and user.item == 'Icicle Plate':
            other_buff = 1.2
        if sk_type == 'Steel' and user.item == 'Iron Plate':
            other_buff = 1.2
        if sk_type == 'Fighting' and user.item == 'Fist Plate':
            other_buff = 1.2
        if sk_type == 'Psychic' and user.item == 'Mind Plate':
            other_buff = 1.2
        if sk_type == 'Flying' and user.item == 'Sky Plate':
            other_buff = 1.2
        if sk_type == 'Dark' and user.item == 'Dread Plate':
            other_buff = 1.2
        if sk_type == 'Ghost' and user.item == 'Spooky Plate':
            other_buff = 1.2
        if sk_type == 'Rock' and user.item == 'Stone Plate':
            other_buff = 1.2
        if sk_type == 'Electric' and user.item == 'Zap Plate':
            other_buff = 1.2
        if sk_type == 'Poison' and user.item == 'Toxic Plate':
            other_buff = 1.2
        if sk_type == 'Fairy' and user.item == 'Pixie Plate':
            other_buff = 1.2
        if sk_type == 'Dragon' and user.item == 'Draco Plate':
            other_buff = 1.2

        # berry buff
        if target.item in attr_berry and sk_type == attr_berry[target.item] and type_buff > 1:
            target.use_item()
            self.log.add(actor=target, event=target.item)

        if target.item == 'Chilan Berry' and sk_type == 'Normal':
            target.use_item()
            self.log.add(actor=target, event=target.item)

        # ability buff
        if user.ability == 'Aerilate' and sk_type == 'Normal':
            sk_type = 'Flying'
            other_buff *= 1.3

        if user.ability == 'Galvanize' and sk_type == 'Normal':
            sk_type = 'Electric'
            other_buff *= 1.3

        if user.ability == 'Refrigerate' and sk_type == 'Normal':
            sk_type = 'Ice'
            other_buff *= 1.3

        if user.ability == 'Pixilate' and sk_type == 'Normal':
            sk_type = 'Fairy'
            other_buff *= 1.3

        if user.ability == 'Liquid Voice':
            if sk_name in sound_move:
                sk_type = 'Water'

        if user.ability == 'Normalize':
            sk_type = 'Normal'
            other_buff *= 1.2

        if user.ability == 'Flare Boost' and user.status is 'brn' and ctg == 'Special':
            other_buff *= 1.5

        if user.ability == 'Toxic Boost' and (user.poison or user.toxic) and ctg == 'Physical':
            other_buff *= 1.5

        if user.ability == 'Mega Launcher':
            if sk_name in pulse_move:
                other_buff *= 1.5

        if user.ability == 'Analytic' and last:
            other_buff *= 1.3

        if user.ability == 'Blaze' and user.HP <= user.maxHP / 3 and sk_type == 'Fire':
            other_buff *= 1.5

        if user.ability == 'Overgrow' and user.HP <= user.maxHP / 3 and sk_type == 'Grass':
            other_buff *= 1.5

        if user.ability == 'Torrent' and user.HP <= user.maxHP / 3 and sk_type == 'Water':
            other_buff *= 1.5

        if user.ability == 'Swarm' and user.HP <= user.maxHP / 3 and sk_type == 'Bug':
            other_buff *= 1.5

        if 'Dark Aura' in [user.ability, target.ability] and sk_type == 'Dark':
            other_buff *= 1.3

        if 'Fairy Aura' in [user.ability, target.ability] and sk_type == 'Fairy':
            other_buff *= 1.3

        if user.ability == 'Iron Fist' and 'Punch' in sk_name and sk_name != 'Sucker Punch':
            other_buff *= 1.2

        if user.ability == 'Neuroforce' and type_buff > 1:
            other_buff *= 1.25

        if user.ability == 'Reckless' and sk_name in recoil_move:
            other_buff *= 1.2

        if user.ability == 'Rivalry' and user.gender in ['Male', 'Female'] and target.gender in ['Male', 'Female']:
            if user.gender == target.gender:
                other_buff *= 1.25
            else:
                other_buff *= 0.75

        if user.ability == 'Sand Force' and env.weather == Weather.Sandstorm:
            if sk_type in ['Rock', 'Steel', 'Ground']:
                other_buff *= 1.3

        if user.ability == 'Strong Jaw' and sk_name in biting_move:
            other_buff *= 1.5

        if user.ability == 'Technician' and power <= 60:
            other_buff *= 1.5

        if user.ability == 'Tinted Lens' and type_buff < 1:
            other_buff *= 2

        if user.ability == 'Tough Claws' and 'contact' in flag:
            other_buff *= 1.3

        if user.ability == 'Water Bubble' and sk_type == 'Water':
            other_buff *= 2

        if not imm_ground(user) and env.terrain == 'psychicterrain' and sk_type == 'Psychic':
            other_buff *= 1.3

        if not imm_ground(user) and env.terrain == 'electricterrain' and sk_type == 'Electric':
            other_buff *= 1.3

        if not imm_ground(user) and env.terrain == 'grassyterrain' and sk_type == 'Grass':
            other_buff *= 1.3

        if not imm_ground(user) and env.terrain == 'grassyterrain' and sk_type == 'Ground':
            other_buff *= 0.5

        if not imm_ground(target) and env.terrain == 'mistyterrain' and sk_type == 'Dragon':
            other_buff *= 0.5

        if env.weather == 'sunnyday' and sk_type == 'Fire':
            other_buff *= 1.5

        if env.weather == 'Raindance' and sk_type == 'Water':
            other_buff *= 1.5

        if env.pseudo_weather['mudsport'] and sk_type == 'Electric':
            other_buff *= 0.5

        if env.pseudo_weather['watersport'] and sk_type == 'Fire':
            other_buff *= 0.5

        # Defence Buff
        if target.ability == 'Fluffy':
            if sk_type == 'Fire':
                other_buff *= 2
            if 'contact' in flag:
                other_buff *= 0.5

        if target.ability == 'Thick Fat':
            if sk_type in ['Ice', 'Fire']:
                other_buff *= 0.5

        if target.ability == 'Water Bubble' and sk_type == 'Fire':
            other_buff *= 0.5

        if target.ability == 'Dry Skin':
            if sk_type == 'Fire':
                other_buff *= 1.25

        if target.ability in ['Prism Armor', 'Filter', 'Solid Rock'] and type_buff > 1:
            other_buff *= 0.75

        if target.ability in ['Shadow Shield', 'Multiscale'] and target.maxHP == target.HP:
            other_buff *= 0.5

        if user.ability != 'Infiltrator' and sk_name != 'ConfusionHit':
            if target.get_sidecond()['lightscreen'] and ctg == 'Special':
                other_buff *= 0.5
            if target.get_sidecond()['reflect'] and ctg == 'Physical':
                other_buff *= 0.5
            if target.get_sidecond()['auroraveil']:
                other_buff *= 0.5

        base_dmg = dmg * stab_buff * type_buff * ct_buff * other_buff
        rnd = random.uniform(0.85, 1)

        return int(base_dmg * rnd)


if __name__ == '__main__':
    log = BattleLog()
    utils = Utils(log)
    env = Env()
    player = Player()
    pkms1 = read_team()
    pkms2 = read_team()
    for pkm in pkms1 + pkms2:
        pkm.setup(0, player, env, log)
    env = Env()

    utils.step_turn_pkm(env=env, pkms=[pkms1[2], pkms2[5]], moves=['gigadrain', 'shadowball'])
