from pokemon import Pokemon
from const import *


class BattleLog:
    def __init__(self):
        self.total_logs = []
        self.log = []

    def step(self):
        self.total_logs.append(self.log)
        self.log = []

    def reset(self, players):
        self.total_logs = []
        self.log = []
        self.log.append([None, 'The game between ' + players[0].name + ' and ' + players[1].name + ' started!'])
        for player in players:
            pkm_str = ""
            for pkm in player.pkms:
                pkm_str += pkm.name + '/'
            self.log.append([None, player.name + '\'s pokemons: ' + pkm_str[:-1]])

    def match_up(self):
        self.total_logs.append(self.log)
        self.step_print()

    def step_print(self):
        self.total_logs.append(self.log)
        for actor, event in self.log:
            if actor:
                if type(actor) is Pokemon:
                    print(actor.player.name + '\'s', actor.name, event)
                else:
                    print(actor.name, event)
            else:
                print(event)
        print()
        self.log = []

    def translate(self, raw_log):
        actor = raw_log['actor']
        event = raw_log['event']
        target = raw_log['target']
        val = raw_log['val']
        logtype = raw_log['logType']

        if type(actor) is Pokemon:
            actor = actor.player.name + '\'s', actor.name
        else:
            actor = actor.name

        if type(actor) is Pokemon:
            target = target.player.name + '\'s', target.name
        else:
            target = target.name

        # ability
        if logtype == logType.ability:
            log = '[' + actor + '\'s ' + event + ']'

        # common
        elif event == 'use':
            if 'Hidden Power' in val:
                val = 'Hidden Power'
            log = 'used ' + str(val) + '!'

        elif event == 'use_item':
            log = 'used ' + val + '!'

        if event == 'lost':
            log = 'lost ' + str(val) + '% of it\'s health!'

        elif event == 'sub_make':
            log = 'made a substitute!'

        elif event == 'sub_dmg':
            log = 'the substitute took damage instead!'

        elif event == 'heal':
            log = 'was healed ' + str(val) + '% of it\'s health!'

        elif event == 'sub_fade':
            log = 'substitute faded...'

        elif event == 'protect':
            log = 'protected itself!'

        elif event == 'protect_from':
            log = 'protected itself from attack!'

        elif event == 'change_type':
            log = '\'s type changed to ' + val + '!'

        elif event == 'lose':
            log = 'lost!'

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
            log = '\'s ' + str(val) + ' increased!'
        elif event == '+2':
            log = '\'s ' + str(val) + ' harshly increased!'
        elif event == '+3':
            log = '\'s ' + str(val) + ' dramatically increased!'
        elif event == '+6':
            log = '\'s ' + str(val) + ' is increased to maximum!'
        elif event == '+7':
            log = '\'s ' + str(val) + ' couldn\'t be higher!'

        elif event == '-0':
            log = '\'s ' + str(val) + ' couldn\'t be lowered!'
        elif event == '-1':
            log = '\'s ' + str(val) + ' decreased!'
        elif event == '-2':
            log = '\'s ' + str(val) + ' harshly decreased!'
        elif event == '-3':
            log = '\'s ' + str(val) + ' dramatically decreased!'
        elif event == '-7':
            log = '\'s ' + str(val) + ' couldn\'t be lower!'

        # item event
        elif event == 'rockyhelmet':
            log = 'was hurt by the Rocky Helmet!'

        elif event == 'balloon':
            log = 'is floating with Air Balloon!'

        elif event == '-balloon':
            log = '\'s Air Balloon popped!'

        elif event == 'leftovers':
            log = 'restored HP with leftovers.'

        # status event
        elif event == '+poison':
            log = 'was hurt by it\'s posion!'

        elif event == '+burn':
            log = 'was hurt by it\'s burn!'

        if event == 'confusion':
            output = actor + 'is confused!'

        elif event == '+flinch':
            log = 'flinched and could not move!'

        elif event == '+frz':
            log = 'is frozen solid!'

        elif event == '-frz':
            log = 'is out of frozen!'

        elif event == 'wake':
            log = actor, 'woke up!'

        elif event == 'taunt':
            log = 'was taunted!'

        elif event == '-taunt':
            log = '\'s taunt ended!'

        elif event == 'status':
            log = 'is ' + str(val) + '!'

        elif event == 'istatus':
            log = 'is already ' + str(val) + '!'

        # weather event
        elif event == '+mistyterrain':
            log = 'was protected by Misty Terrain!'

        elif event == '+grassyterrain':
            log = 'was healed by Grassy Terrain!'

        elif event == '+electricterrain':
            log = 'was protected by Electric Terrain!'

        elif event == '+psychicterrain':
            log = 'was protected by Psychic Terrain!'

        elif event == 'mistyterrain':
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
            log = 'The weirdness disappeared from the battlefield.!'

        elif event == 'sunnyday':
            log = "The sunlight turned harsh!"

        elif event == 'Raindance':
            log = "It started to rain!"

        elif event == 'hail':
            log = "It started to hail!"

        elif event == 'Sandstorm':
            log = "A sandstorm kicked up!"

        elif event == '-sunnyday':
            log = "The sunlight faded."

        elif event == '-Raindance':
            log = "The rain stopped."

        elif event == '-hail':
            log = "The hail stopped."

        elif event == '-Sandstorm':
            log = "The sandstorm subsided."

        # field event
        elif event == '+stealthrock':
            log = 'Pointed stone stuck into ' + actor.name + '\'s body.'
            actor = None

        elif event == 'stealthrock':
            log = 'Pointed stone floated on ' + actor.player.name + '\'s field.'
            actor = None

        elif event == 'toxicspikes':
            log = 'Toxic spikes were scattered on ' + actor.player.name + '\'s field.'
            actor = None

        elif event == '+toxicspikes':
            log = 'was influenced by toxic spikes!'

        elif event == '-toxicspikes':
            log = 'absorbed the toxic spikes!'

        elif event == 'spikes':
            log = 'Spikes were scattered on ' + actor.player.name + '\'s field.'
            actor = None

        elif event == '+spikes':
            log = 'was hurt by spikes!'

        elif event == 'clear':
            log = val + ' on ' + actor.name + '\'s field was cleared.'
            actor = None

        elif event in ['-auroraveil', '-craftyshield', '-lightscreen', '-luckychant', '-matblock', '-mist',
                       '-quickguard',
                       '-reflect', '-safeguard', '-tailwind', '-wideguard']:
            log = event + ' on ' + actor.name + '\'s field ended.'
            actor = None

        # no actor
        elif event == 'ct':
            log = 'A critical hit!'

        elif event == 'effect':
            log = 'It\'s super effective!'

        elif event == 'neffect':
            log = 'It\'s not very effective...'

        elif event == '0effect':
            log = 'It didn\'t effect ' + actor.name + '...'

        elif event == 'splash':
            log = 'But nothing happened...'

        elif event == 'fail':
            log = 'But it failed!'

        # skill
        elif event == 'knockoff':
            log = 'knocked off ' + val.name + '\'s ' + val.item + '!'

        elif event == 'trick':
            log = 'switched its item with ' + val.name + '!'

        elif event == 'obtain':
            log = 'obtained ' + val + '!'

        elif event == 'painsplit':
            log = 'splited the pain with ' + val.name + '!'

        elif event == '+leechseed':
            log = '\'s health was snapped by leech seed!'

        elif event == 'pred':
            log = 'predicted an attack!'

        elif event == 'solar':
            log = 'absorbed the light!'

        elif event == 'belly_fail_hp':
            log = 'does not have enough HP!'

        elif event == 'belly_fail_atk':
            log = '\'s Attack is already maximum!'

        # +ability
        elif event == '+moldbreak':
            log = 'is breaking the mold!'

        elif event == '+pressure':
            log = 'is exerting pressure!'

        elif event == '+anticipate':
            log = 'anticipated danger!'

        elif event == '+frisk':
            log = 'discovered the opponent\'s ' + val

        elif event == '+trace':
            log = 'traced the opponent\'s' + val

        elif event == '+raindish':
            log = 'was healed by Rain Dish!'

        elif event == '+dryskin':
            log = 'was healed by Dry Skin!'

        elif event == '-dryskin':
            log = 'was hurt by Dry Skin!'

        elif event == '+icebody':
            log = 'was healed by Ice Body!'

        elif event == '+hydration':
            log = val + ' was healed by Hydration!'

        elif event == '+ironbarbs':
            log = 'was hurt by ' + event + '!'

        elif event == '+roughskin':
            log = 'was hurt by ' + event + '!'

    def add(self, actor=None, event=None, target=None, val=0, type=logType.ability):
        self.log.append({'actor': actor, 'event': event, 'target': target, 'val': val, 'logType': type})
