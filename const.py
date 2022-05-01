import numpy as np

names = ['Satoshi', 'BJK']


class Signal:
    Wait, Move, Switch, End = range(4)


memories = {'Bug Memory': 'Bug', 'Dark Memory': 'Dark', 'Dragon Memory': 'Dragon', 'Electric Memory': 'Electric',
            'Fairy Memory': 'Fairy', 'Fighting Memory': 'Fighting', 'Fire Memory': 'Fire', 'Flying Memory': 'Flying',
            'Ghost Memory': 'Ghost', 'Grass Memory': 'Grass', 'Ground Memory': 'Ground', 'Ice Memory': 'Ice',
            'Poison Memory': 'Poison', 'Psychic Memory': 'Psychic', 'Rock Memory': 'Rock', 'Steel Memory': 'Steel',
            'Water Memory': 'Water'}

plates = {'Pixie Plate': 'Fairy', 'Draco Plate': 'Dragon', 'Dread Plate': "Dark", 'Earth Plate': 'Ground',
          'Fist Plate': 'Fighting',
          'Flame Plate': 'Fire', 'Icicle Plate': 'Ice', 'Insect Plate': 'Bug', 'Iron Plate': 'Steel',
          'Meadow Plate': 'Grass',
          'Mind Plate': 'Psychic', 'Sky Plate': 'Flying', 'Splash Plate': 'Water', 'Spooky Plate': 'Ghost',
          'Stone Plate': 'Rock', 'Toxic Plate': 'Poison', 'Zap Plate': 'Electric'}


class Weather:
    Harsh, Rain, Sandstorm, Hail = range(4)


class State:
    Poison, Toxic, Paralyse, Burn, Frozen, Sleep, Confuse, Infatuation, Nightmare, Drowsy, Encore, Torment, HealBlock, \
    Identified, Disable, Block, Embargo, Taunt, Telekinesis, Curse, Perish, Leech, Bound, SmackDown, ThroatChop, Tarshot, \
    Octolock, = range(27)


class Status:
    Burn, Sleep, Toxic, Poison, Paralyse, Frozen = range(6)


full_status = {
    'brn': 'burned',
    'slp': 'asleep',
    'tox': 'toxic',
    'psn': 'posioned',
    'par': 'paralysed',
    'frz': 'frozen'
}

full_stat = {
    'atk': 'Attack',
    'def': 'Defence',
    'spa': 'Special Attack',
    'spd': 'Special Defence',
    'spe': 'Speed'
}

sound_move = ['Boomburst ', 'Bug Buzz ', 'Chatter ', 'Clanging Scales ', 'Clangorous Soul ', 'Clangorous Soulblaze ',
              'Confide ', 'Disarming Voice ', 'Echoed Voice ', 'Eerie Spell ', 'Grass Whistle ', 'Growl ', 'Heal Bell ',
              'Howl ', 'Hyper Voice ', 'Metal Sound ', 'Noble Roar ', 'Overdrive ', 'Parting Shot ', 'Perish Song ',
              'Relic Song ', 'Roar ', 'Round ', 'Screech ', 'Shadow Panic ', 'Sing ', 'Snarl ', 'Snore ',
              'Sparkling Aria ', 'Supersonic ', 'Uproar ']

pulse_move = ['Aura Sphere', 'Dark Pulse', 'Water Pulse', 'Origin Pulse', 'Dragon Pulse', 'Heal Pulse']

recoil_move = ['Brave Bird', 'Double Edge', 'Flare Blitz', 'Head Charge', 'Head Smash', 'High Jump Kick', 'Jump Kick',
               'Submission', 'Take Down', 'Wild Charge']

biting_move = ['Bite', 'Crunch', 'Fire Fang', 'Thunder Fang', 'Ice Fang', 'Fishious Rend', 'Hyper Fang', 'Jaw Lock',
               'Poison Fang', 'Psychic Fangs']

ct_move = ['Slash', 'Cross Poison', 'Night Slash', 'Psycho Cut', 'Shadow Claw', 'Crabhammer', 'Cross Chop',
           'Stone Edge', 'Spacial Rend', 'Attack Order', 'Aeroblast', 'Blaze Kick', 'Drill Run', 'Sky Attack',
           'Razor Leaf', 'Poison Tail', 'Karate Chop', 'Razor Wind', 'Snipe Shot', 'Air Cutter']
evolved = []

no_gender = []


class Stat:
    HP, Atk, Def, SAtk, SDef, Spe = range(6)


Nature = {'Adamant': ('Atk', 'SpA'),
          'Bold': ('Def', 'Atk'),
          'Brave': ('Atk', 'Spe'),
          'Calm': ('SpD', 'SpA'),
          'Careful': ('SpD', 'SpA'),
          'Gentle': ('SpD', 'Def'),
          'Hasty': ('Spe', 'Def'),
          'Impish': ('Def', 'SpA'),
          'Jolly': ('Spe', 'SpA'),
          'Lax': ('Def', 'SpD'),
          'Lonely': ('Atk', 'Def'),
          'Mild': ('SpA', 'Def'),
          'Modest': ('SpA', 'Atk'),
          'Naive': ('Spe', 'SpD'),
          'Naughty': ('Atk', 'SpD'),
          'Quiet': ('SpA', 'Spe'),
          'Rash': ('SpA', 'SpD'),
          'Relaxed': ('Def', 'Spe'),
          'Sassy': ('SpD', 'Spe'),
          'Timid': ('Spe', 'Atk')}


class Ctg:
    Physical, Special, Status = range(3)


trans_ctg = {
    'Physical': Ctg.Physical,
    'Special': Ctg.Special,
    'Status': Ctg.Status
}


class Attr:
    NoAttr, Water, Fire, Grass, Electric, Ice, Poison, Bug, Fighting, Steel, Rock, Ghost, Psychic, Dark, Ground, Flying, Dragon, Fairy, Normal = range(
        19)


Attr_dict = {'NoAttr': 0,
             "Water": 1, "Fire": 2, "Grass": 3, "Electric": 4, "Ice": 5, "Poison": 6, "Bug": 7, "Fighting": 8,
             "Steel": 9, "Rock": 10, "Ghost": 11, "Psychic": 12, "Dark": 13, "Ground": 14, "Flying": 15, "Dragon": 16,
             "Fairy": 17, "Normal": 18}

Attr_Mat = np.array([[1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, ],
                     [1, 0.5, 2, 0.5, 1, 1, 1, 1, 1, 1, 2, 1, 1, 1, 2, 1, 0.5, 1, 1, ],
                     [1, 0.5, 0.5, 2, 1, 2, 1, 2, 1, 2, 0.5, 1, 1, 1, 1, 1, 0.5, 1, 1, ],
                     [1, 2, 0.5, 0.5, 1, 1, 0.5, 0.5, 1, 0.5, 2, 1, 1, 1, 2, 0.5, 0.5, 1, 1, ],
                     [1, 2, 1, 0.5, 0.5, 1, 1, 1, 1, 1, 1, 1, 1, 1, 0, 2, 0.5, 1, 1, ],
                     [1, 0.5, 0.5, 2, 1, 0.5, 1, 1, 1, 0.5, 1, 1, 1, 1, 2, 2, 2, 1, 1, ],
                     [1, 1, 1, 2, 1, 1, 0.5, 1, 1, 0, 0.5, 0.5, 1, 1, 0.5, 1, 1, 2, 1, ],
                     [1, 1, 0.5, 2, 1, 1, 0.5, 1, 0.5, 0.5, 1, 0.5, 2, 2, 1, 0.5, 1, 0.5, 1, ],
                     [1, 1, 1, 1, 1, 2, 0.5, 0.5, 1, 2, 2, 0, 0.5, 2, 1, 0.5, 1, 0.5, 2, ],
                     [1, 0.5, 0.5, 1, 0.5, 2, 1, 1, 1, 0.5, 2, 1, 1, 1, 1, 1, 1, 2, 1, ],
                     [1, 1, 2, 1, 1, 2, 1, 2, 0.5, 0.5, 1, 1, 1, 1, 0.5, 2, 1, 1, 1, ],
                     [1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 2, 2, 0.5, 1, 1, 1, 1, 0, ],
                     [1, 1, 1, 1, 1, 1, 2, 1, 2, 0.5, 1, 1, 0.5, 0, 1, 1, 1, 1, 1, ],
                     [1, 1, 1, 1, 1, 1, 1, 1, 0.5, 1, 1, 2, 2, 0.5, 1, 1, 1, 0.5, 1, ],
                     [1, 1, 2, 0.5, 2, 1, 2, 0.5, 1, 2, 2, 1, 1, 1, 1, 0, 1, 1, 1, ],
                     [1, 1, 1, 2, 0.5, 1, 1, 2, 2, 0.5, 0.5, 1, 1, 1, 1, 1, 1, 1, 1, ],
                     [1, 1, 1, 1, 1, 1, 1, 1, 1, 0.5, 1, 1, 1, 1, 1, 1, 2, 0, 1, ],
                     [1, 1, 0.5, 1, 1, 1, 0.5, 1, 2, 0.5, 1, 1, 1, 2, 1, 1, 2, 1, 1, ],
                     [1, 1, 1, 1, 1, 1, 1, 1, 1, 0.5, 0.5, 0, 1, 1, 1, 1, 1, 1, 1, ]])
