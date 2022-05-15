from main.pokemon import Pokemon
from lib.const import *
import time
import os


class BattleLog:
    def __init__(self, game, save_log=False):
        self.total_logs = []
        self.log = []
        self.total_log_texts = []
        self.log_text = []
        self.save_log = save_log
        self.loser = None
        self.game = game

    def step(self):
        self.total_logs.append(self.log)
        self.log = []

    def reset(self, players):
        self.total_log_texts = []
        self.log_text = []
        self.total_logs = []
        self.log = []
        self.loser = None

        if self.save_log:
            if not os.path.exists('../log'):
                os.mkdir('../log')
            self.log_file = 'log/' + str(time.asctime()).replace(':', '-') + '.txt'

        self.log_text.append('The game between ' + players[0].name + ' and ' + players[1].name + ' started!')
        for player in players:
            pkm_str = ""
            for pkm in player.pkms:
                pkm_str += pkm.name + '/'
            self.log_text.append(player.name + '\'s pokemons: ' + pkm_str[:-1])

        for log in self.log_text:
            self.game.send_log(log)

        self.step_print()

    def step_print(self):
        self.total_logs.append(self.log)
        self.total_log_texts.append(self.log_text)
        if self.save_log:
            with open(self.log_file, 'a') as f:
                for log in self.log_text:
                    if log:
                        f.write(log + '\n')
                    if log and 'lost!' in log:
                        break
                f.write('\n')
        else:
            for log in self.log_text:
                if log:
                    print(log)
                if log and 'lost!' in log:
                    break
            print()

        self.log = []
        self.log_text = []

    def translate(self, raw_log):
        actor = raw_log['actor']
        event = raw_log['event']
        target = raw_log['target']
        val = raw_log['val']
        logtype = raw_log['logType']

        def trans(actor, event, target, val, logtype):
            log = None

            if actor:
                if type(actor) is Pokemon:
                    actor = actor.player.name + ' \'s ' + actor.name + ' '
                else:
                    actor = actor.name + ' '

            if target:
                if type(target) is Pokemon:
                    target = target.player.name + ' \'s ' + target.name
                else:
                    target = target.name

            # ability
            if logtype == logType.ability:
                log = '[' + actor + '\'s ' + event + ']'
                raw_log['actor'].ability_revealed = True

            if log:
                return log

            # common
            if event == 'mega':
                log = 'evolved into ' + val + '!'

            if event == 'use':
                if 'Hidden Power' in val:
                    val = 'Hidden Power'
                log = 'used ' + str(val) + '!'

            elif event == 'zmove':
                log = 'was surrounded by Z-Power!'

            elif event == 'use_item':
                log = 'used ' + val + '!'

            elif event == 'lost':
                log = 'lost ' + str(val) + '% of it\'s health!'

            elif event == 'substitute':
                log = 'made a substitute!'

            elif event == '+substitute':
                log = '\'s substitute took damage instead!'

            elif event == 'heal':
                log = 'was healed ' + str(val) + '% of it\'s health!'

            elif event == '0heal':
                log = '\'s HP is already full!'

            elif event == 'burnitem':
                log = '\'s ' + val + ' was burned!'

            elif event == '-substitute':
                log = '\'s substitute faded...'

            elif event == 'protect':
                log = 'protected itself!'

            elif event == '+protect':
                log = 'protected itself from attack!'

            elif event == 'change_type':
                log = '\'s type changed to ' + val + '!'

            elif event == 'add_type':
                log = '\'s type was added ' + val + '!'

            elif event == 'add_type':
                log = 'was removed ' + val + ' types!'

            elif event == 'lose':
                log = 'lost!'
                if not self.loser:
                    self.loser = actor[:-1]

            elif event == 'withdraw':
                log = 'withdrew ' + str(val) + '!'

            elif event == 'switch':
                log = 'sent out ' + str(val) + '!'

            elif event == 'faint':
                log = 'fainted!'

            elif event == 'avoid':
                log = 'avoided the attack!'

            # stat_lv
            elif event == '+1':
                log = '\'s ' + str(val) + ' rose!'
            elif event == '+2':
                log = '\'s ' + str(val) + ' rose rapidly!'
            elif event == '+3':
                log = '\'s ' + str(val) + ' rose drastically!'
            elif event == '+6':
                log = '\'s ' + str(val) + ' rose to maximum!'
            elif event == '+7':
                log = '\'s ' + str(val) + ' won\'t go any higher!'

            elif event == '-0':
                log = '\'s ' + str(val) + ' couldn\'t be lowered!'
            elif event == '-1':
                log = '\'s ' + str(val) + ' fell!'
            elif event == '-2':
                log = '\'s ' + str(val) + ' fell harshly!'
            elif event == '-3':
                log = '\'s ' + str(val) + ' fell severely!'
            elif event == '-7':
                log = '\'s ' + str(val) + ' won\'t go any lower!'

            # item event
            elif event == 'rockyhelmet':
                log = 'was hurt by Rocky Helmet!'

            elif event == 'balloon':
                log = 'is floating with Air Balloon!'

            elif event == '-balloon':
                log = '\'s Air Balloon popped!'

            elif event == 'leftovers':
                log = 'restored HP with Leftovers.'

            elif event == '+blacksludge':
                log = 'restored HP with Black Sludge.'

            elif event == '-blacksludge':
                log = 'lost HP with Black Sludge!'

            elif event == 'ejectbutton':
                log = 'switched out using its Eject Button!'

            elif event == 'toxicorb':
                log = '\'s Toxic Orb activated!'

            elif event == 'flameorb':
                log = '\'s Flame Orb activated!'

            elif event == 'shellbell':
                log = 'restored a little HP using its Shell Bell!'

            # status event
            elif event == '+psn':
                log = 'was hurt by it\'s posion!'

            elif event == '+brn':
                log = 'was hurt by it\'s burn!'

            elif event == '+slp':
                log = 'is fast asleep.'

            elif event == '+par':
                log = 'is paralysed and could not move!'

            elif event == 'confusion':
                log = 'is confused!'

            elif event == '+nightmare':
                log = 'was tortured by nightmare!'

            elif event == '+flinch':
                log = 'flinched and could not move!'

            elif event == 'magiccoat':
                log = 'shrouded itself with Magic Coat!'

            elif event == '+magiccoat':
                log = 'bounced the ' + val + ' back!'

            elif event == '+frz':
                log = 'is frozen solid!'

            elif event == '-frz':
                log = 'is out of frozen!'

            elif event == '-slp':
                log = 'woke up!'

            elif event == 'taunt':
                log = 'was taunted!'

            elif event == '-taunt':
                log = '\'s taunt ended!'

            elif event == '+taunt':
                log = 'can\'t use ' + val + ' after the Taunt!'

            elif event == '++taunt':
                log = 'is already taunted!'

            elif event == 'partiallytrapped':
                log = 'is trapped by ' + val + '!'

            elif event == '+partiallytrapped':
                log = 'was hurt by ' + val + '!'

            elif event == '-partiallytrapped':
                log = 'is no longer trapped!'

            elif event == 'status':
                log = 'was ' + str(val) + '!'
                if val == 'paralysed':
                    log += ' It may be unable to move!'

            elif event == '++status':
                log = 'is already ' + str(val) + '!'

            elif event == '-status':
                log = val + ' was cured!'

            elif event == '-vstatus':
                log = val + ' was cured!'

            elif event == '++substitute':
                log = 'already has a substitute!'

            elif event == '--substitute':
                log = 'doesn\'t have enough HP to make a substitute...'

            # weather event
            elif event == '+mistyterrain':
                log = 'was protected by Misty Terrain!'

            elif event == '+grassyterrain':
                log = 'was healed by Grassy Terrain!'

            elif event == '+electricterrain':
                log = 'was protected by Electric Terrain!'

            elif event == '+psychicterrain':
                log = 'was protected by Psychic Terrain!'

            elif event == '+hail':
                log = "was buffeted by hail!"

            elif event == '+Sandstorm':
                log = "was buffeted by sandstorm!"

            if log:
                return actor + log

            if event == 'healbell':
                log = 'A bell chimed.'

            if event == 'aromatherapy':
                log = 'A soothing aroma wafted through the area!'

            if event == 'haze':
                log = 'All the stat changes on field were removed.'

            if event == 'mistyterrain':
                log = 'Mist swirled around the battlefield!'

            elif event == 'grassyterrain':
                log = 'Grass grew to cover the battlefield!'

            elif event == 'electricterrain':
                log = 'An electric current ran across the battlefield!'

            elif event == 'psychicterrain':
                log = 'The battlefield got weird!'

            elif event == '-mistyterrain':
                log = 'The mist disappeared from the battlefield.'

            elif event == '-grassyterrain':
                log = 'The grass disappeared from the battlefield.'

            elif event == '-electricterrain':
                log = 'The electric disappeared from the battlefield.'

            elif event == '-psychicterrain':
                log = 'The weirdness disappeared from the battlefield.'

            elif event == 'sunnyday':
                log = "The sunlight turned harsh!"

            elif event == 'RainDance':
                log = "It started to rain!"

            elif event == 'hail':
                log = "It started to hail!"

            elif event == 'Sandstorm':
                log = "A sandstorm kicked up!"

            elif event == '=RainDance':
                log = 'Rain continues to fall.'

            elif event == '=Sandstorm':
                log = 'The sandstorm is raging.'

            elif event == '=sunnyday':
                log = 'The sunlight is strong.'

            elif event == '=hail':
                log = 'The hail is crashing down.'

            elif event == '-sunnyday':
                log = "The sunlight faded."

            elif event == '-RainDance':
                log = "The rain stopped."

            elif event == '-hail':
                log = "The hail stopped."

            elif event == '-Sandstorm':
                log = "The sandstorm subsided."

            elif event == 'trickroom':
                log = 'It twisted the dimensions!'

            elif event == '-trickroom':
                log = 'The twisted dimensions returned to normal!'

            elif event == 'magicroom':
                log = 'It created a bizarre area in which Pokémon\'s held items lose their effects!'

            elif event == '-magicroom':
                log = 'Magic Room wore off, and held items\' effects returned to normal!'

            elif event == 'wonderroom':
                log = 'It created a bizarre area in which Defense and Sp. Def stats are swapped!'

            elif event == '-wonderroom':
                log = 'Wonder Room wore off, and Defense and Sp. Def stats returned to normal!'

            elif event == 'fairylock':
                log = 'No one will be able to run away during the next turn!'

            elif event == 'iondeluge':
                log = 'A deluge of ions showers the battlefield!'

            elif event == 'gravity':
                log = 'Gravity intensified!'

            elif event == 'mudsport':
                log = 'Electricity\'s power was weakened!'

            elif event == 'watersport':
                log = 'Fire\'s power was weakened!'

            # field event
            elif event == '+stealthrock':
                log = 'Pointed stone stuck into ' + actor + '\'s body.'
                actor = None

            elif event == 'stealthrock':
                log = 'Pointed stone floated on ' + actor + '\'s field.'
                actor = None

            elif event == 'toxicspikes':
                log = 'Toxic Spikes were scattered on ' + actor + '\'s field.'
                actor = None

            elif event == 'spikes':
                log = 'Spikes were scattered on ' + actor + '\'s field.'
                actor = None

            elif event == 'clear':
                log = val + ' on ' + actor + '\'s field was cleared.'

            elif event in ['-auroraveil', '-craftyshield', '-lightscreen', '-luckychant', '-matblock', '-mist',
                           '-quickguard',
                           '-reflect', '-safeguard', '-tailwind', '-wideguard']:
                log = event + ' on ' + actor + '\'s team ended.'

            elif event == 'tailwind':
                log = 'The Tailwind blew from behind ' + actor + '\'s team!'

            elif event == 'auroraveil':
                log = 'Aurora Veil made ' + actor + '\'s team stronger against physical and special moves!'

            elif event == 'safeguard':
                log = actor + '\'s steam cloaked itself in a mystical veil!'

            elif event == 'wideguard':
                log = 'Wide Guard protected ' + actor + '\'s team!'

            elif event == 'mist':
                log = actor + '\'s team became shrouded in mist!'

            elif event == 'lightscreen':
                log = 'Light Screen made' + actor + '\'s team stronger against special moves!'

            elif event == 'reflect':
                log = 'Reflect made' + actor + '\'s team stronger against physical moves!'

            elif event == 'luckychant':
                log = 'Lucky Chant shielded ' + actor + '\'s team from critical hits!'

            elif event in ['quickguard', 'matblock', 'craftyshield']:
                log = actor + '\'s team was protected by ' + event + '!'

            elif event in ['--auroraveil', '--craftyshield', '--lightscreen', '--reflect']:
                log = event + ' on ' + actor + '\'s field was destoryed!'

            if log:
                return log

            elif event == '+toxicspikes':
                log = 'was influenced by Toxic Spikes!'

            elif event == '-toxicspikes':
                log = 'absorbed the Toxic Spikes!'

            elif event == '+spikes':
                log = 'was hurt by Spikes!'

            if log:
                return actor + log

            # no actor
            elif event == 'ct':
                log = 'A critical hit!'

            elif event == 'effect':
                log = 'It\'s super effective!'

            elif event == 'neffect':
                log = 'It\'s not very effective...'

            elif event == '0effect':
                log = 'It didn\'t effect ' + actor + '...'

            elif event == 'splash':
                log = 'But nothing happened...'

            elif event == 'fail':
                log = 'But it failed!'

            elif event == 'round':
                log = '\nRound ' + str(val) + '\n'

            # attr berry
            elif event in attr_berry:
                log = 'The ' + event + ' weakened the damage to ' + actor + '!'

            elif event == 'healingwish':
                log = 'A healing wish came true for ' + actor + '!'

            elif event == 'wish':
                log = 'A wish came true for ' + actor + '!'

            elif event == 'lunardance':
                log = actor + 'became cloaked in mystical moonlight!'
            if log:
                return log

            # skill

            elif event == 'transform':
                log = 'transformed into ' + target + '!'

            elif event == 'self_transform':
                log = 'transformed into ' + val + '!'

            elif event == 'knockoff':
                log = 'knocked off ' + target + '\'s ' + val + '!'

            elif event == 'trick':
                log = 'switched its item with ' + target + '!'

            elif event == 'obtain':
                log = 'obtained ' + val + '!'

            elif event == 'painsplit':
                log = 'split the pain with ' + target + '!'

            elif event == 'leechseed':
                log = 'was seeded!'

            elif event == '+leechseed':
                log = '\'s health was sapped by leech seed!'

            elif event == '++leechseed':
                log = 'is already seeded!'

            elif event == 'predict':
                log = 'predicted an attack!'

            elif event == 'solar':
                log = 'absorbed the light!'

            elif event == 'belly_fail_hp':
                log = 'does not have enough HP!'

            elif event == 'belly_fail_atk':
                log = '\'s Attack is already maximum!'

            elif event == 'drop':
                log = 'dropped to the ground!'

            elif event == 'recoil':
                log = 'was hurt by the recoil!'

            # +ability
            elif event == '-forceswitch':
                log = 'cannot be forced to switch!'

            elif event == '+moldbreaker':
                log = 'is breaking the mold!'

            elif event == '+pressure':
                log = 'is exerting pressure!'

            elif event == '+unnerve':
                log = 'makes the pokemons on field to nervous to eat berries!'

            elif event == '+anticipate':
                log = 'anticipated danger!'

            elif event == '+frisk':
                log = 'discovered the opponent\'s ' + val + '!'

            elif event == '+trace':
                log = 'traced the opponent\'s ' + val + '!'

            elif event == '+raindish':
                log = 'was healed by Rain Dish!'

            elif event == '+dryskin':
                log = 'was healed by Dry Skin!'

            elif event == '-dryskin':
                log = 'was hurt by Dry Skin!'

            elif event == '+icebody':
                log = 'was healed by Ice Body!'

            elif event == '+ironbarbs':
                log = 'was hurt by Iron Barbs!'

            elif event == '+roughskin':
                log = 'was hurt by Rough Skin!'

            elif event == '+illusion':
                log = '\'s illusion disappeard!'

            elif event == '+whiteherb':
                log = 'prevented the ability decrease!'

            if log:
                return actor + log

        log = trans(actor, event, target, val, logtype)
        if event in ['lost', 'heal', 'use_item']:
            log = '(' + log + ')'
        return log

    def add(self, actor=None, event=None, target=None, val=0, type=logType.common):
        log = {'actor': actor, 'event': event, 'target': target, 'val': val, 'logType': type}
        self.log.append(log)
        self.log_text.append(self.translate(log))
        self.game.send_log(self.translate(log))
