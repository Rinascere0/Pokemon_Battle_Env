import copy
import random

from pokemon import Pokemon
from functions import *
from data.moves import Moves

from read_team import *
from player import Player
from env import Env
from const import *

from log import BattleLog

Hit, Miss, NoEffect, Onhold, NoLog = 0, 1, 2, 3, 4


class Utils:
    def __init__(self, log):
        self.log = log

    def check_prior(self, env, pkms, moves=None):
        prior = np.zeros(2)
        if pkms[0].Spe > pkms[1].Spe:
            prior[0] += 0.1
        elif pkms[0].Spe < pkms[1].Spe:
            prior[1] += 0.1
        else:
            prior[random.randint(0, 1)] += 0.1

        if env.pseudo_weather['trickroom'] > 0:
            prior = - prior

        if moves:
            for pkm_id, (pkm, move_set) in enumerate(zip(pkms, moves)):
                if move_set['type'] == ActionType.Switch:
                    continue
                move = move_set['item']
                prior[pkm_id] += move['priority']
                if pkm.ability == 'Prankster' and move['category'] == 'Status':
                    prior[pkm_id] += 1
                if pkm.ability == 'Triage' and 'heal' in move['flags']:
                    prior[pkm_id] += 3
                if pkm.ability == 'Gale Wings' and move['type'] == 'Flying' and pkm.HP == pkm.maxHP:
                    prior[pkm_id] += 1

        return int(prior[0] < prior[1])

    def switch(self, game, env, players, pkms, moves, first):
        last = 1 - first
        if moves[last]['type'] == ActionType.Switch or moves[last]['item']['name'] != 'Pursuit':
            players[first].switch(env, moves[first]['item'], withdraw=True)
        else:
            # pursuit
            pkms[first].to_switch = True
            self.use_move(user=pkms[last], target=pkms[first], move=moves[last]['item'], env=env, game=game,
                          last=True)
            pkms[first].to_switch = False
            if pkms[first].turn:
                players[first].switch(env, moves[first]['item'], withdraw=True)
                pkms[last].turn = False
            else:
                return

        self.switch_on(players, env)

    def step_turn(self, game, env, players, moves):
        pkms = [players[0].get_pivot(), players[1].get_pivot()]
        pkms[0].prep(env, pkms[1], moves[0])
        pkms[1].prep(env, pkms[0], moves[1])
        megas = [None, None]

        # check mega and z
        if moves[0]['type'] == ActionType.Mega:
            megas[0] = True
        if moves[1]['type'] == ActionType.Mega:
            megas[1] = True

        #  calc speed for switch and mega
        first = self.check_prior(env, pkms)
        last = 1 - first

        #  print(moves[first]['type'])
        #  print(moves[last]['type'])
        # switch first
        if moves[first]['type'] == ActionType.Switch:
            self.switch(game, env, players, pkms, moves, first)

        if moves[last]['type'] == ActionType.Switch:
            self.switch(game, env, players, pkms, moves, last)

        if megas[first]:
            pkms[first].mega_evolve()
            players[first].use_mega()
            self.switch_on(players, env)

        if megas[last]:
            pkms[last].mega_evolve()
            players[last].use_mega()
            self.switch_on(players, env)

        # calc speed again for moves, with new stat (after mega)
        pkms = [players[0].get_pivot(), players[1].get_pivot()]
        pkms[0].calc_stat(env, pkms[1])
        pkms[1].calc_stat(env, pkms[0])
        first = self.check_prior(env, pkms, moves)
        last = 1 - first

        if pkms[first].turn:
            # if opponent stepped turn, it actually moves last
            #  print('turn',pkms[first].name)
            move_last = not pkms[last].turn
            self.use_move(pkms[first], pkms[last], moves[first]['item'], env, game, move_last)

        if pkms[last].turn:
            # print('turn', pkms[last].name)
            # always move last
            self.use_move(pkms[last], players[first].get_pivot(), moves[last]['item'], env, game, True)

        # end turn
        for pid, player in enumerate(players):
            player.get_pivot().end_turn(env, players[1 - pid].get_pivot())

        done, to_switch = self.check_switch(env, players)

        return done, to_switch

    def finish_turn(self, env, players):
        for pid, player in enumerate(players):
            player.get_pivot().finish_turn(env, players[1 - pid].get_pivot())

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
                    self.log.add(actor=user, event='+moldbreaker')

                if user.ability == 'Pressure':
                    self.log.add(actor=user, event='Pressure', type=logType.ability)
                    self.log.add(actor=user, event='+pressure')

                if user.ability == 'Unnerve':
                    self.log.add(actor=user, event='Unnerve', type=logType.ability)
                    self.log.add(actor=user, event='+unnerve')

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
                    if target.item == 'Adrenaline Orb':
                        target.use_item()
                        target.boost('spe', 1)

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

    def use_move(self, user: Pokemon, target: Pokemon, move, env, game, last):
        if not user.turn:
            return
        user.turn = False
        if user.vstatus['flinch']:
            if user.ability == 'Inner Focus':
                self.log.add(actor=user, event=user.ability, type=logType.ability)
            else:
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
        if user.status is 'par':
            if random.uniform(0, 1) <= 0.25:
                self.log.add(actor=user, event='+par')
                return
        if user.vstatus['confusion']:
            if random.uniform(0, 1) <= 0.3:
                self.log.add(actor=user, event='+confusion')
                dmg = self.calc_dmg(user, user, move=Moves['ConfusionHit'], env=env, last=False)
                user.damage(dmg)
                return

        if target.ability == 'Pressure':
            user.loss_pp(move, 2)
        else:
            user.loss_pp(move, 1)

        if not user.choice_move and user.item in ['Choice Band', 'Choice Scarf', 'Choice Specs']:
            user.choice_move = move['name']

        z_move = 'is_z_move' in move
        if z_move:
            self.log.add(actor=user, event='zmove')
            user.player.use_z()
        elif 'basePower' in move:
            sk_type = move['type']
            power = move['basePower']
            if user.ability == 'Aerilate' and sk_type == 'Normal':
                sk_type = 'Flying'
                power *= 1.2
            if user.ability == 'Galvanize' and sk_type == 'Normal':
                sk_type = 'Electric'
                power *= 1.2
            if user.ability == 'Refrigerate' and sk_type == 'Normal':
                sk_type = 'Ice'
                power *= 1.2
            if user.ability == 'Pixilate' and sk_type == 'Normal':
                sk_type = 'Fairy'
                power *= 1.2
            if user.ability == 'Normalize':
                sk_type = 'Normal'
                sk_type *= 1.2
            if user.ability == 'Liquid Voice' and 'sound' in move['flags']:
                sk_type = 'Water'
            move = copy.deepcopy(move)
            move['type'] = sk_type
            move['basePower'] = power

        self.log.add(actor=user, event='use', val=move['name'])

        if user.ability == 'Protean':
            self.log.add(actor=user, event='Protean', type=logType.ability)
            self.log.add(actor=user, event='change_type', val=move['type'])
            user.attr = [move['type']]

        if z_move and 'zMove' in move:
            if 'effect' in move['zMove']:
                effect = move['zMove']['effect']
                if effect == 'crit2':
                    user.boost('ct', 2)
                elif effect == 'clearnegativeboost':
                    user.reset_stat_lv(nega=True)
                elif effect == 'heal':
                    user.heal(perc=100)
                elif effect == 'healreplacement':
                    user.slotCondition['heal'] = True
                elif effect == 'redirect':
                    user.add_vstate('followme')
                elif effect == 'curse':
                    if 'Ghost' in user.attr:
                        user.heal(perc=100)
                    else:
                        user.boost('atk', 1)
            elif 'boost' in move['zMove']:
                boost = move['zMove']['boost']
                for stat, lv in boost.items():
                    user.boost(stat, lv)

        if user.vstatus['taunt']:
            if move['category'] == 'Status' and not z_move:
                self.log.add(actor=user, event='+taunt', val=move['name'])
                return

        if move['name'] == 'Sucker Punch':
            if last or target.next_move and target.next_move['category'] == 'Status':
                self.log.add(event='fail')
                return

        if move['name'] == user.last_move:
            user.metronome += 1
        else:
            user.metronome = 0
            user.last_move = move['name']

        if 'reflectable' in move['flags']:
            reflect = False
            if target.ability == 'Magic Bounce':
                self.log.add(actor=target, event=target.ability, type=logType.ability)
                reflect = True
            if reflect or target.vstatus['magiccoat']:
                self.log.add(actor=target, event='+magiccoat', val=move['name'])
                target = user

        if move['name'] == 'Splash':
            self.log.add(event='splash')
            return

        if move['name'] in ['Fake Out', 'First Impression'] and not user.switch_on:
            self.log.add(event='fail')
            return

        if move['priority'] > 0 and env.terrain == 'psychicterrain':
            self.log.add(actor=target, event='+psychicterrain')
            return

        self_destruct = None
        if 'selfdestruct' in move:
            self_destruct = move['selfdestruct']
            if self_destruct == 'always':
                user.damage(0, 100)

        if 'multiaccuracy' in move:
            count = move['multihit']
        else:
            count = 1

        user.calc_stat(env, target)
        target.calc_stat(env, user)
        if move['target'] == 'self':
            target = user

        for i in range(count):
            if not target.alive:
                if i == 0:
                    self.log.add(event='fail')
                break
            useful = self.check_useful(env, user, target, move, last)
            if useful == Hit:
                if self_destruct == 'ifHit':
                    user.damage(0, 100)
                self.effect_move(user, target, move, game, env, last)
                # eject button
                if target.item == 'Eject Button':
                    target.use_item()
                    game.call_switch(target.player)
                # switch if not opponent eject button
                elif target.item == 'Red Card':
                    target.use_item()
                    if user.can_force_switch():
                        game.call_switch(user.player)

                elif move['name'] in ['U-turn', 'Volt Switch', 'Boton Pass']:
                    if target.next_move and target.next_move['name'] == 'Pursuit' and target.turn:
                        self.use_move(target, user, target.next_move, env, game, True)
                    if user.alive:
                        game.call_switch(user.player)
                elif move['name'] in ['Dragon Tail', 'Circle Throw']:
                    if user.can_force_switch():
                        game.call_switch(target.player)

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
            elif useful == NoLog:
                user.set_lock()
                break

    def effect_move(self, user: Pokemon, target: Pokemon, move, game, env, last):
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
                if user.name == 'Greninja-Ash' and move['name'] == 'Water Shuriken':
                    count = 3
                elif type(count) is list:
                    count = np.random.choice([2, 3, 4, 5], p=[1 / 3, 1 / 3, 1 / 6, 1 / 6])

            target_sidecond = env.get_sidecond(target)
            if move['name'] in ['Psychic Fangs', 'Brick Break']:
                for wall in ['lightscreen', 'reflect', 'auroraveil']:
                    if target_sidecond[wall]:
                        self.log.add(actor=target.player, event='--' + wall)
                    target_sidecond[wall] = 0

            total_damage = 0
            for _ in range(count):
                dmg = self.calc_dmg(user, target, move, env, last)
                target.damage(val=dmg, perc=False, attr='NoAttr', user=user, category=ctg)
                total_damage += dmg
                if not target.alive:
                    break

            # no side effects for non-status z-move

            sec_target = target
            effects=[]
            if 'secondary' in move:
                effects .append(move['secondary'])
            elif 'secondaries' in move:
                effects+=['secondaries']
            elif 'volatileStatus' in move:
                effects .append(move['volatileStatus'])

            if user.ability == 'Sheer Force':
                effects = None

            # TODO: Does it exist move that have side effects to both?

            if 'self' in move:
                effects = move['self']
                sec_target = user
                if type(effects) is not list:
                    effects = [effects]

            if sec_target == target and target.ability == 'Shield Dust':
                self.log.add(actor=target, event=target.ability, log=logType.ability)
            elif effects:
                for effect in effects:
                    if effect is None:
                        continue
                    chance = effect['chance'] / 100 if 'chance' in effect else 1
                    if user.ability == 'Serene Grace':
                        chance = min(1, 2 * chance)
                    hit = np.random.choice([True, False], p=[chance, 1 - chance])
                    if hit:
                        if 'self' in effect:
                            effect = effect['self']
                        if 'status' in effect:
                            sec_target.add_status(effect['status'], env, user)
                        if 'volatileStatus' in effect:
                            # mustrecharge
                            sec_target.add_vstate(effect['volatileStatus'])
                        if 'boosts' in effect:
                            for stat, lv in effect['boosts'].items():
                                sec_target.boost(stat, lv)
                        if move['name'] == 'Tri Attack':
                            status = random.randint(0, 2)
                            if status == 0:
                                sec_target.add_status('par', env, user)
                            elif status == 1:
                                sec_target.add_status('brn', env, user)
                            else:
                                sec_target.add_status('frz', env, user)

            # drain move
            if 'drain' in move:
                heal = int(move['drain'][0] / move['drain'][1] * dmg)
                user.heal(heal, False, target)

            if 'recoil' in move:
                if user.ability == 'Rock Head':
                    self.log.add(actor=user, event=user.ability, type=logType.ability)
                else:
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

            if move['name'] == 'Uproar':
                if user.lock_round == 3:
                    user.set_lock()
                    env.uproar = True
                else:
                    user.set_lock(move['name'])
                    env.uproar = True

            if move['name'] in ['Rollout', 'Ice Ball']:
                if user.lock_round == 5:
                    user.set_lock()

            if move['name'] == 'Rapid Spin':
                env.clear_field(user.player, type='spike', log=self.log)

            # same round move
            if move['name'] in ['Triple Axel', 'Triple Kick']:
                user.multi_count += 1

            if user.item == 'Shell Bell':
                self.log.add(actor=user, event='shellbell')
                user.heal(total_damage / 8)

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
                target.add_status(status, env, user)

            if 'volatileStatus' in move:
                vstatus = move['volatileStatus']
                cond = None
                if 'condition' in move:
                    cond = move['condition']
                target.add_vstate(vstatus, cond, user)

            #     if 'sideCondition' in move:
            #        side_cond = move['sideCondition']
            if 'condition' in move:
                cond = move['condition']
            else:
                cond = None

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
                env.add_sidecond(sidecond, target, cond, self.log)

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
                if item != False:
                    target.lose_item(item)
                else:
                    self.log.add(event='fail')

            if move['name'] == 'Pain Split':
                self.log.add(actor=user, event='painsplit', target=target)
                avg_hp = (user.HP + target.HP) / 2
                user.HP = avg_hp
                target.HP = avg_hp

            if 'slotCondition' in move:
                env.add_slotcond(move['slotCondition'], user)

            if move['name'] == 'Haze':
                self.log.add(event='haze')
                user.reset_stat_lv()
                target.reset_stat_lv()

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

            if move['name'] in ['Roar', 'Whirlwind']:
                if target.can_force_switch():
                    game.call_switch(target.player)

        if 'contact' in move['flags']:
            if target.ability in ['Iron Barbs', 'Rough Skin']:
                self.log.add(actor=target, event=target.ability, type=logType.ability)
                user.damage(0, perc=1 / 8)

            if target.item == 'Rocky Helmet':
                self.log.add(actor=user, event='rockyhelmet')
                user.damage(0, perc=1 / 6)

            if target.ability == 'Gooey':
                self.log.add(actor=target, event=target.ability, type=logType.ability)
                user.boost('spe', -1)

            if target.ability == 'Cute Charm':
                if random.uniform(0, 1) < 0.3:
                    self.log.add(actor=target, event=target.ability, type=logType.ability)
                    user.add_vstate('attract', cond=None, user=user)

            if target.ability == 'Poison Point':
                if random.uniform(0, 1) < 0.3:
                    self.log.add(actor=target, event=target.ability, type=logType.ability)
                    user.add_status('psn', env, user)

            if target.ability == 'Flame Body':
                if random.uniform(0, 1) < 0.3:
                    self.log.add(actor=target, event=target.ability, type=logType.ability)
                    user.add_status('brn', env, user)

            if target.ability == 'Static':
                if random.uniform(0, 1) < 0.3:
                    self.log.add(actor=target, event=target.ability, type=logType.ability)
                    user.add_status('par', env, user)

            if target.ability == 'Effect Spore':
                rnd = random.uniform(0, 1)
                if rnd < 0.1:
                    self.log.add(actor=target, event=target.ability, type=logType.ability)
                    user.add_status('psn', env, user)
                elif rnd < 0.2:
                    self.log.add(actor=target, event=target.ability, type=logType.ability)
                    user.add_status('par', env, user)
                elif rnd < 0.3:
                    self.log.add(actor=target, event=target.ability, type=logType.ability)
                    user.add_status('slp', env, user)

            if target.ability == 'Poison Touch':
                if random.uniform(0, 1) < 0.3:
                    self.log.add(actor=user, event=user.ability, type=logType.ability)
                    target.add_status('psn', env, user)
        if move['name'] == 'Knock Off' and target and target.alive and target.base_item:
            self.log.add(actor=user, event='knockoff', target=target, val=target.item)
            target.lose_item()

        if user.ability in ['Magician', 'Pickpocket'] and not user.base_item:
            item = target.lose_item()
            self.log.add(actor=target, event=target.ability, type=logType.ability)
            user.lose_item(item)

    def check_useful(self, env, user, target, move, last):
        sk_type = move['type']
        sk_name = move['name']
        sk_ctg = move['category']
        sk_flag = move['flags']
        acc = move['accuracy']
        acc_buff = 1
        always_hit = False

        # 特性修正

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

        if sk_name in ['Shadow Force', 'Phantom Force', 'Fly', 'Dig', 'Bounce']:
            if user.off_field:
                user.off_field = None
            else:
                user.off_field = sk_name

        if target.vstatus['protect'] and target is not user and 'protect' in move['flags']:
            if sk_name == 'Feint':
                self.log.add(actor=user, event='feint', target=target)
                target.vstatus['protect'] = 0
            elif 'is_z_move' in move:
                self.log.add(actor=user, event='zprotect')
            else:
                self.log.add(actor=target, event='+protect')
                return NoLog

        if 'No Guard' in [user.ability, target.ability]:
            always_hit = True

        if target.off_field and not always_hit:
            if target.off_field == 'Dig':
                if sk_name != 'Earthquake':
                    return NoEffect
            elif target.off_field in ['Bounce', 'Fly']:
                if sk_name != 'Thunder':
                    return NoEffect
            else:
                return NoEffect

        if sk_ctg == 'Status':
            if move['target'] == 'normal' and 'Grass' in target.attr and move['type'] == 'Grass':
                return NoEffect
            if 'status' in move:
                status = move['status']
                if status == 'brn' and 'Fire' in target.attr:
                    return NoEffect
                if status == 'par' and 'Electric' in target.attr:
                    return NoEffect
                if status in ['psn', 'tox'] and ('Poison' in target.attr or 'Steel' in target.attr):
                    return NoEffect
            if sk_name == 'Thunder Wave':
                if sk_type == 'Normal' and 'Ghost' in target.attr or sk_type == 'Electric' and 'Ground' in target.attr:
                    return NoEffect

        if user.ability in ['Mold Breaker', 'Teravolt', 'Turboblaze']:
            target.moldbreak()

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
                target.boost('spa', 1)
                return NoEffect

        if sk_type == 'Fire':
            if target.ability == 'Flash Fire':
                self.log.add(actor=target, event=target.ability, type=logType.ability)
                target.flash_fire = True
                return NoEffect

        if sk_type == 'Electric':
            if target.ability == 'Lightning Rod':
                self.log.add(actor=target, event=target.ability, type=logType.ability)
                target.boost('spa', 1)
                return NoEffect
            if target.ability == 'Motor Drive':
                self.log.add(actor=target, event=target.ability, type=logType.ability)
                target.boost('spe', 1)
                return NoEffect
            if target.ability == 'Volt Absorb':
                self.log.add(actor=target, event=target.ability, type=logType.ability)
                target.heal(1 / 4, perc=Hit)
                return NoEffect

        if sk_type == 'Grass':
            if target.ability == 'Sap Sipper':
                self.log.add(actor=target, event=target.ability, type=logType.ability)
                target.boost('atk', 1)
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

        if sk_ctg != 'Status':
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

        if always_hit:
            return True

        if user.item == 'Wide Lens':
            acc_buff *= 1.1

        if user.item == 'Zoom Lens' and last:
            acc_buff *= 1.2

        if user.ability == 'Victory Star':
            acc_buff *= 1.1

        if user.ability == 'Compound Eyes':
            acc_buff *= 1.3

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
        if sk_name == 'Counter':
            return user.round_dmg['Physical'] * 2

        if sk_name == 'Mirror Coat':
            return user.round_dmg['Special'] * 2

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

        if sk_name == 'Earthquake' and target.off_field == 'Dig':
            power *= 2

        if sk_name == 'Pursuit' and target.to_switch:
            power *= 2

        if sk_name == 'Return':
            power = 102

        if sk_name == 'Water Shuriken' and user.name == 'Greninja-Ash':
            power = 20

        if sk_name == 'Acrobatics' and user.item is None:
            power *= 2

        if move['name'] == 'Weather Ball':
            power = 100
            if env.weather is 'hail':
                sk_type = 'Ice'
            elif env.weather is 'sunnyday':
                sk_type = 'Fire'
            elif env.weather is 'Raindance':
                sk_type = 'Water'
            elif env.weather is 'Sandstorm':
                sk_type = 'Rock'
            else:
                power = 50

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
        ct_lv += user.stat_lv['ct']
        ct_rate = get_ct(ct_lv)
        if user.ability == 'Merciless' and target.status in ['psn', 'tox']:
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

        # ability buff

        if user.ability == 'Sheer Force':
            effects = None
            if 'secondary' in move:
                effects = move['secondary']
            elif 'secondaries' in move:
                effects = move['secondaries']
            if effects:
                other_buff *= 1.3

        if user.ability == 'Flare Boost' and user.status is 'brn' and ctg == 'Special':
            other_buff *= 1.5

        if user.ability == 'Toxic Boost' and (user.poison or user.toxic) and ctg == 'Physical':
            other_buff *= 1.5

        if user.ability == 'Flash Fire' and user.flash_fire and sk_type == 'Fire':
            other_buff *= 1.5

        if user.ability == 'Mega Launcher':
            if 'pulse' in flag:
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

        if user.ability == 'Reckless' and 'recoil' in flag:
            other_buff *= 1.2

        if user.ability == 'Rivalry' and user.gender in ['M', 'F'] and target.gender in ['M', 'F']:
            if user.gender == target.gender:
                other_buff *= 1.25
            else:
                other_buff *= 0.75

        if user.ability == 'Sand Force' and env.weather == Weather.Sandstorm:
            if sk_type in ['Rock', 'Steel', 'Ground']:
                other_buff *= 1.3

        if user.ability == 'Strong Jaw' and 'bite' in flag:
            other_buff *= 1.5

        if user.ability == 'Technician' and power <= 60:
            other_buff *= 1.5

        if user.ability == 'Tinted Lens' and type_buff < 1:
            other_buff *= 2

        if user.ability == 'Tough Claws' and 'contact' in flag:
            other_buff *= 1.3

        if user.ability == 'Water Bubble' and sk_type == 'Water':
            other_buff *= 2

        # item buff
        if ctg == 'Physical' and user.item == 'Muscle Band':
            other_buff *= 1.1

        if ctg == 'Special' and user.item == 'Wise Glasses':
            other_buff *= 1.1

        if user.item == 'Expert Belt' and type_buff > 1:
            other_buff *= 1.2

        if user.item == 'Life Orb':
            other_buff *= 1.3

        if user.item == 'Normal Gem' and sk_type == 'Normal':
            user.use_item()
            other_buff *= 1.3

        if user.item == 'Metronome':
            other_buff *= 1 + 0.1 * user.metronome

        if sk_type == 'Fire' and user.item in ['Flame Plate', 'Charcoal']:
            other_buff *= 1.2
        if sk_type == 'Grass' and user.item in ['Meadow Plate', 'Miracle Seed', 'Rose Incense']:
            other_buff *= 1.2
        if sk_type == 'Water' and user.item in ['Splash Plate', 'Mystic Water', 'Sea Incense', 'Wave Incense']:
            other_buff *= 1.2
        if sk_type == 'Ground' and user.item in ['Earth Plate', 'Soft Sand']:
            other_buff *= 1.2
        if sk_type == 'Bug' and user.item in ['Insect Plate', 'Silver Powder']:
            other_buff *= 1.2
        if sk_type == 'Ice' and user.item in ['Icicle Plate', 'Never-Melt Ice']:
            other_buff *= 1.2
        if sk_type == 'Steel' and user.item in ['Iron Plate', 'Metal Coat']:
            other_buff *= 1.2
        if sk_type == 'Fighting' and user.item in ['Fist Plate', 'Black Belt']:
            other_buff *= 1.2
        if sk_type == 'Psychic' and user.item in ['Mind Plate', 'Twisted Spoon', 'Odd Incense']:
            other_buff *= 1.2
        if sk_type == 'Flying' and user.item in ['Sky Plate', 'Sharp Beak']:
            other_buff *= 1.2
        if sk_type == 'Dark' and user.item in ['Dread Plate', 'Black Glasses']:
            other_buff *= 1.2
        if sk_type == 'Ghost' and user.item in ['Spooky Plate', 'Spell Tag']:
            other_buff *= 1.2
        if sk_type == 'Rock' and user.item in ['Stone Plate', 'Hard Stone', 'Rock Incense']:
            other_buff *= 1.2
        if sk_type == 'Electric' and user.item in ['Zap Plate', 'Magnet']:
            other_buff *= 1.2
        if sk_type == 'Poison' and user.item in ['Toxic Plate', 'Poison Barb']:
            other_buff *= 1.2
        if sk_type == 'Fairy' and user.item == 'Pixie Plate':
            other_buff *= 1.2
        if sk_type == 'Dragon' and user.item in ['Draco Plate', 'Dragon Fang']:
            other_buff *= 1.2
        if sk_type == 'Normal' and user.item == 'Silk Scarf':
            other_buff *= 1.2

        # berry buff
        if target.item in attr_berry and sk_type == attr_berry[target.item] and type_buff > 1:
            self.log.add(actor=target, event=target.item)
            target.use_item(add_log=False)
            other_buff *= 0.5

        if target.item == 'Chilan Berry' and sk_type == 'Normal':
            self.log.add(actor=target, event=target.item)
            target.use_item(add_log=False)
            other_buff *= 0.5

        # env buff

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

        if target.ability == 'Heatproof':
            if sk_type == 'Fire':
                other_buff *= 0.5
        if target.ability in ['Prism Armor', 'Filter', 'Solid Rock'] and type_buff > 1:
            other_buff *= 0.75

        if target.ability in ['Shadow Shield', 'Multiscale'] and target.maxHP == target.HP:
            other_buff *= 0.5

        target_sidecond = env.get_sidecond(target)
        if user.ability != 'Infiltrator' and sk_name != 'ConfusionHit':
            if target_sidecond['lightscreen'] and ctg == 'Special':
                other_buff *= 0.5
            if target_sidecond['reflect'] and ctg == 'Physical':
                other_buff *= 0.5
            if target_sidecond['auroraveil']:
                other_buff *= 0.5

        if target.vstatus['protect'] and 'is_z_move' in move:
            other_buff *= 0.25

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
