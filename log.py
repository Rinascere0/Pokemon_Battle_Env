from pokemon import Pokemon


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

    def add(self, actor=None, event=None, val=0):
        log = None
        if event == 'confusion':
            log = 'is confused!'

        elif event == '+flinch':
            log = 'flinched and could not move!'

        elif event == 'wake':
            log = actor, 'woke up!'

        elif event == 'ct':
            log = 'A critical hit!'

        elif event == 'helmet':
            log = 'was hurt by the rocky helmet!'

        elif event == 'rough':
            log = 'was hurt by rough skin!'

        elif event == 'heal':
            log = 'was healed ' + str(val) + '% of it\'s health!'

        elif event == 'lost':
            log = 'lost ' + str(val) + '% of it\'s health!'

        elif event == 'sub_make':
            log = 'made a substitute!'

        elif event == 'sub_dmg':
            log = 'the substitute took damage instead!'

        elif event == 'sub_fade':
            log = 'substitute faded...'

        elif event == 'effect':
            log = 'It\'s super effective!'

        elif event == 'neffect':
            log = 'It\'s not very effective...'

        elif event == '0effect':
            log = 'It didn\'t effect ' + actor.name + '...'
            actor = None

        elif event == 'mold':
            log = 'is breaking the mold!'

        elif event == 'pressure':
            log = 'is exerting pressure!'

        elif event == 'intimidate':
            log = 'intimidated ' + val + '!'

        elif event == 'download':
            log = '\'s download activated!'

        elif event == 'soulheart':
            log = '\'s Soul-Heart activated!'

        elif event == 'beastboost':
            log = '\'s Beast Boost activated!'

        elif event == 'anticipate':
            log = 'anticipated danger!'

        elif event == 'frisk':
            log = 'discovered the opponent\'s ' + val

        elif event == 'trace':
            log = 'copied the opponent\'s' + val

        elif event == 'splash':
            log = 'But nothing happened...'

        elif event == 'knockoff':
            log = 'knocked off ' + val.name + '\'s ' + val.item + '!'

        elif event == 'obtain':
            log = 'obtained ' + val + '!'

        elif event == 'taunt':
            log = 'was taunted!'

        elif event == '-taunt':
            log = '\'s taunt ended!'

        elif event == 'protect':
            log = 'protected itself!'

        elif event == 'protect_from':
            log = 'protected itself from attack!'

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

        elif event == '+posion':
            log = 'was hurt by it\'s posion!'

        elif event == '+burn':
            log = 'was hurt by it\'s burn!'

        elif event in ['-auroraveil', '-craftyshield', '-lightscreen', '-luckychant', '-matblock', '-mist',
                       '-quickguard',
                       '-reflect', '-safeguard', '-tailwind', '-wideguard']:
            log = event + ' on ' + actor.player.name + '\'s field ended.'
            actor = None

        elif event == 'use':
            if 'Hidden Power' in val:
                val = 'Hidden Power'
            log = 'used ' + str(val) + '!'

        elif event == 'use_item':
            log = 'used ' + val + '!'

        elif event == 'fail':
            log = 'But it failed!'

        elif event == 'faint':
            log = 'fainted!'

        elif event == 'status':
            log = 'is ' + str(val) + '!'

        elif event == 'istatus':
            log = 'is already ' + str(val) + '!'

        elif event == 'avoid':
            log = 'avoided the attack!'

        elif event == 'belly_fail_hp':
            log = 'does not have enough HP!'

        elif event == 'belly_fail_atk':
            log = '\'s Attack is already maximum!'

        elif event == 'frz':
            log = 'is frozen solid!'

        elif event == 'unfrz':
            log = 'is out of frozen!'

        elif event == 'solar':
            log = 'absorbed the light!'

        elif event == 'withdraw':
            log = 'withdrew ' + str(val) + '!'

        elif event == 'switch':
            log = 'sent out ' + str(val) + '!'

        elif event == 'pred':
            log = 'predicted an attack!'

        elif event == 'speedboost':
            log = '\'s Speed Boost activated!'

        elif event == 'moody':
            log = '\'s Moody activated!'

        elif event == 'solarpower':
            log = 'lost it\'s health due to Solar Power!'

        elif event == '+leechseed':
            log = '\'s health was snapped by leech seed!'

        elif event == 'ooze':
            log = 'was hurt by liquid ooze!'

        elif event == 'balloon':
            log = 'is floating with Air Balloon!'

        elif event == '-balloon':
            log = '\'s Air Balloon popped!'

        elif event == 'Rocky Helmet':
            log = 'was hurt by Rocky Helmet!'

        elif event in ['Iron Barbs', 'Rough Skin']:
            log = 'was hurt by ' + event + '!'

        elif event == 'steadfast':
            log = '\'s Steadfast activated!'

        elif event == 'justified':
            log = '\'s Justified activated!'

        elif event == 'protean':
            log = '\'s Protean activated!'

        elif event == 'change_type':
            log = '\'s type changed to ' + val + '!' \
                                                 ''
        # elif event=='lockedmove':
        #     log='locked'

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

        elif event == 'leftovers':
            log = 'restored HP with leftovers.'

        elif event == 'lose':
            log = 'lost!'

        #  print(event)
        if log:
            self.log.append([actor, log])
