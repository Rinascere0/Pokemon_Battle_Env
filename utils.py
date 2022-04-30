from pokemon import Pokemon
from functions import *
from data.moves import Moves

from read_team import *
from player import Player
from env import Env

from log import BattleLog

Hit, Miss, NoEffect = 0, 1, 2


class Utils:
    def __init__(self, log):
        self.log = log

    def step_turn(self, env, players, move_names):
        pkms = [players[0].get_pivot(), players[1].get_pivot()]
        pkms[0].prep(env)
        pkms[1].prep(env)
        moves = [Moves[move_names[0]], Moves[move_names[1]]]
        prior = np.zeros(2)
        if pkms[0].Spe > pkms[1].Spe:
            prior[0] += 0.1
        elif pkms[0].Spe < pkms[1].Spe:
            prior[1] += 0.1
        else:
            prior[random.randint(0, 1)] += 0.1

        # switch

        if env.pseudo_weather['trickroom'] > 0:
            prior = 1 - prior

        if type(move_names[0]) is int:
            prior[0] += 10
        else:
            prior[0] += moves[0]['priority']

        if type(move_names[1]) is int:
            prior[1] += 10
        else:
            prior[1] += moves[1]['priority']

        if prior[0] > prior[1]:
            first = 0
        else:
            first = 1

        # move first
        if type(moves[first]) is int:
            if moves[1 - first]['name'] != 'Pursuit':
                players[first].switch(moves[first])
            else:
                self.use_move(user=pkms[1 - first], target=pkms[first], move=moves[1 - first], env=env, last=True)
                if pkms[first].turn:
                    players[first].switch(moves[first])
                    pkms[1 - first].turn = False
                return
        else:
            self.use_move(user=pkms[first], target=pkms[1 - first], move=moves[first], env=env, last=False)

        # move last
        if pkms[1 - first].turn:
            if type(moves[1 - first]) is int:
                players[1 - first].switch(moves[1 - first])
            else:
                self.use_move(user=pkms[1 - first], target=pkms[first], move=moves[1 - first], env=env, last=True)

        # end turn

        done = False
        to_switch = []
        for pid, player in enumerate(players):
            if player.lose():
                self.log.add(player, 'lose')
                done = True
            elif not player.get_pivot().alive:
                to_switch.append(player)
            else:
                player.get_pivot().end_turn()

        return done, to_switch

    def step_turn_pkm(self, env, pkms, move_names):
        pkms[0].prep(env)
        pkms[1].prep(env)
        moves = [Moves[move_names[0]], Moves[move_names[1]]]
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

        self.use_move(user=pkms[first], target=pkms[1 - first], move=moves[first], env=env, last=False)
        self.use_move(user=pkms[1 - first], target=pkms[first], move=moves[1 - first], env=env, last=True)

        self.log.step_print()

    def use_move(self, user: Pokemon, target: Pokemon, move, env, last):
        if user.vstatus['flinch']:
            self.log.add(user, '+flinch')
            return
        if user.status is 'slp':
            if user.status_turn == 0:
                self.log.add(user, 'sleep')
                user.status_turn -= 1
                return
            else:
                self.log.add(user, 'wake')
        if user.status is 'frz':
            if random.uniform(0, 1) <= 0.2:
                self.log.add(user, 'unfrz')
            else:
                self.log.add(user, 'frz')
                return

        self.log.add(user, 'use', move['name'])
        if move['name'] == 'Splash':
            self.log.add(event='splash')

        if 'charge' in move['flags']:
            if user.charge is None:
                user.charge = move['name']
                if move['name'] in ['Solar Beam', 'Solar Blade']:
                    self.log.add(user, 'solar')
                    if env.weather is 'sunnyday':
                        user.charge = None
                if user.charge is not None:
                    return
            else:
                user.charge = None

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
        for _ in range(count):
            useful = self.check_useful(user, target, move)
            if useful == Hit:
                if self_destruct == 'ifHit':
                    user.damage(0, 100)
                self.effect_move(user, target, move, env, last)
            elif useful == Miss:
                self.log.add(target, 'avoid')
                user.multi_count = 0
            else:
                self.log.add(actor=target, event='0effect')
                user.set_lock()

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
                if type(count) is list:
                    count = np.random.choice([2, 3, 4, 5], p=[1 / 3, 1 / 3, 1 / 6, 1 / 6])

            for _ in range(count):
                dmg = self.calc_dmg(user, target, move, env, last)
                target.damage(val=dmg, perc=False, in_turn=True)

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
                            sec_target.add_status(effect['status'])
                        if 'volatileStatus' in effect:
                            sec_target.add_vstate(effect['volatileStatus'])
                        if 'boosts' in effect:
                            for stat, lv in effect['boosts'].items():
                                sec_target.boost(stat, lv)
                        if move['name'] == 'Tri Attack':
                            status = random.randint(0, 2)
                            if status == 0:
                                sec_target.add_status('par')
                            elif status == 1:
                                sec_target.add_status('brn')
                            else:
                                sec_target.add_status('frz')

            # drain move
            if 'drain' in move:
                heal = int(move['drain'][0] / move['drain'][1] * dmg)
                if target.ability == 'Liquid Ooze':
                    if user.item == 'Big Root':
                        heal = int(heal * 1.3)
                    user.damage(heal)
                else:
                    user.heal(heal)

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

            # same round move
            if move['name'] in ['Triple Axel', 'Triple Kick']:
                user.multi_count += 1

        else:
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
                target.add_status(status)

            if 'volatileStatus' in move:
                vstatus = move['volatileStatus']
                if 'condition' in move:
                    cond = move['condition']
                else:
                    cond = None
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
                env.set_weather(weather, user.item)

            if 'pseudoWeather' in move:
                pd_weather = move['pseudoWeather']
                env.set_pd_weather(pd_weather)

            if 'terrain' in move:
                terrain = move['terrain']
                env.set_terrain(terrain, user.item)

            if 'sideCondition' in move:
                sidecond = move['sideCondition']
                target.add_sidecond(sidecond)

            if move['name'] == 'Belly Drum':
                if user.HP > user.maxHP / 2:
                    if user.stat_lv['atk'] == 6:
                        self.log.add(user, 'belly_fail_atk')
                    else:
                        user.damage(0, perc=1 / 2)
                        user.boost('atk', 6)
                else:
                    self.log.add(user, 'belly_fail_hp')
        if target.ability in ['Iron Barbs', 'Rough Skin']:
            user.damage(0, perc=1 / 8)
            self.log.add()

        if target.item == 'Rocky Helmet':
            user.damage(0, prec=1 / 6)

    def check_useful(self, user, target, move):
        sk_type = move['type']
        sk_name = move['name']
        sk_ctg = move['category']
        sk_flag = move['flags']
        acc = move['accuracy']
        acc_buff = 1
        # 特性修正

        if user.ability in ['Moldbreaker', 'Teravolt', 'Turboblaze']:
            self.log.add(user, 'mold')
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

        if sk_type == Attr.Water:
            if target.ability == 'Water Absorb':
                target.heal(1 / 4, perc=Hit)
                return NoEffect
        if target.ability == 'Dry Skin':
            target.heal(1 / 4, perc=Hit)
            return NoEffect
        if target.ability == 'Storm Drain':
            target.Satk_lv += 1
            return NoEffect

        if sk_type == Attr.Fire:
            if target.ability == 'Flash Fire':
                target.flash_fire = Hit
                return NoEffect

        if sk_type == Attr.Electric:
            if target.ability == 'Lightning Rod':
                target.Satk_lv += 1
                return NoEffect
            if target.ability == 'Motor Drive':
                target.Spe_lv += 1
                return NoEffect
            if target.ability == 'Volt Absorb':
                target.heal(1 / 4, perc=Hit)
                return NoEffect

        if sk_type == Attr.Grass:
            if target.ability == 'Sap Sipper':
                target.Atk_lv += 1
                return NoEffect

        if sk_type == Attr.Ground:
            if target.ability == 'Levitate':
                return NoEffect

        if target.ability == 'Bulletproof' and 'bullet' in sk_flag:
            return NoEffect

        if target.ability == 'Soundproof' and 'sound' in sk_flag:
            return NoEffect

        type_buff = 1
        for attr in target.attr:
            type_buff *= get_attr_fac(sk_type, attr)
        if type_buff == 0:
            if not (user.ability == 'Scrappy' and sk_type == 'Normal' and 'Ghost' in target.attr):
                return NoEffect
        if target.ability == 'Wonder Guard' and type_buff <= 1:
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

        if 'ohko' in move:
            return target.HP

        if sk_name == 'Stored Power':
            for key, boost in user.stat_lv.items():
                if boost > 0:
                    power += boost * 20

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
        if user.ability == 'sniper':
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

        # 相克补正
        type_buff = 1
        for attr in target.attr:
            type_buff *= get_attr_fac(sk_type, attr)

        if sk_name == 'Flying Press':
            for attr in target.attr:
                type_buff *= get_attr_fac(Attr.Flying, attr)

        if sk_name == 'Freeze Dry' and target.attr:
            # should be effective
            type_buff *= 4

        if type_buff > 1:
            self.log.add(event='effect')
        if type_buff < 1:
            self.log.add(event='neffect')

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

        if sk_type == Attr.Fire and user.item == 'Flame Plate':
            other_buff = 1.2
        if sk_type == Attr.Grass and user.item == 'Meadow Plate':
            other_buff = 1.2
        if sk_type == Attr.Water and user.item == 'Splash Plate':
            other_buff = 1.2
        if sk_type == Attr.Ground and user.item == 'Earth Plate':
            other_buff = 1.2
        if sk_type == Attr.Bug and user.item == 'Insect Plate':
            other_buff = 1.2
        if sk_type == Attr.Ice and user.item == 'Icicle Plate':
            other_buff = 1.2
        if sk_type == Attr.Steel and user.item == 'Iron Plate':
            other_buff = 1.2
        if sk_type == Attr.Fighting and user.item == 'Fist Plate':
            other_buff = 1.2
        if sk_type == Attr.Psychic and user.item == 'Mind Plate':
            other_buff = 1.2
        if sk_type == Attr.Flying and user.item == 'Sky Plate':
            other_buff = 1.2
        if sk_type == Attr.Dark and user.item == 'Dread Plate':
            other_buff = 1.2
        if sk_type == Attr.Ghost and user.item == 'Spooky Plate':
            other_buff = 1.2
        if sk_type == Attr.Rock and user.item == 'Stone Plate':
            other_buff = 1.2
        if sk_type == Attr.Electric and user.item == 'Zap Plate':
            other_buff = 1.2
        if sk_type == Attr.Poison and user.item == 'Toxic Plate':
            other_buff = 1.2
        if sk_type == Attr.Fairy and user.item == 'Pixie Plate':
            other_buff = 1.2
        if sk_type == Attr.Dragon and user.item == 'Draco Plate':
            other_buff = 1.2

        # ability buff
        if user.ability == 'Aerilate' and attr == Attr.Normal:
            attr = Attr.Flying
            other_buff *= 1.3

        if user.ability == 'Galvanize' and attr == Attr.Normal:
            attr = Attr.Electric
            other_buff *= 1.3

        if user.ability == 'Refrigerate' and attr == Attr.Normal:
            attr = Attr.Ice
            other_buff *= 1.3

        if user.ability == 'Pixilate' and attr == Attr.Normal:
            attr = Attr.Fairy
            other_buff *= 1.3

        if user.ability == 'Liquid Voice':
            if sk_name in sound_move:
                attr = Attr.Water

        if user.ability == 'Normalize':
            attr = Attr.Normal
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

        if user.ability == 'Blaze' and user.HP <= user.maxHP / 3 and sk_type == Attr.Fire:
            other_buff *= 1.5

        if user.ability == 'Overgrow' and user.HP <= user.maxHP / 3 and sk_type == Attr.Grass:
            other_buff *= 1.5

        if user.ability == 'Torrent' and user.HP <= user.maxHP / 3 and sk_type == Attr.Water:
            other_buff *= 1.5

        if user.ability == 'Swarm' and user.HP <= user.maxHP / 3 and sk_type == Attr.Bug:
            other_buff *= 1.5

        if 'Dark Aura' in [user.ability, target.ability] and attr == Attr.Dark:
            other_buff *= 1.3

        if 'Fairy Aura' in [user.ability, target.ability] and attr == Attr.Fairy:
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
            if sk_type in [Attr.Rock, Attr.Steel, Attr.Ground]:
                other_buff *= 1.3

        if user.ability == 'Strong Jaw' and sk_name in biting_move:
            other_buff *= 1.5

        if user.ability == 'Technician' and power <= 60:
            other_buff *= 1.5

        if user.ability == 'Tinted Lens' and type_buff < 1:
            other_buff *= 2

        if user.ability == 'Tough Claws' and 'contact' in flag:
            other_buff *= 1.3

        if user.ability == 'Water Bubble' and sk_type == Attr.Water:
            other_buff *= 2

        # Defence Buff
        if target.ability == 'Fluffy':
            if sk_type == Attr.Fire:
                other_buff *= 2
            if 'contact' in flag:
                other_buff *= 0.5

        if target.ability == 'Thick Fat':
            if sk_type in [Attr.Ice, Attr.Fire]:
                other_buff *= 0.5

        if target.ability == 'Water Bubble' and sk_type == Attr.Fire:
            other_buff *= 0.5

        if target.ability == 'Dry Skin':
            if sk_type == Attr.Fire:
                other_buff *= 1.25

        if target.ability in ['Prism Armor', 'Filter', 'Solid Rock'] and type_buff > 1:
            other_buff *= 0.75

        if target.ability in ['Shadow Shield', 'Multiscale'] and target.maxHP == target.HP:
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

    utils.step_turn_pkm(env=env, pkms=[pkms1[2], pkms2[5]], move_names=['stealthrock', 'shadowball'])
