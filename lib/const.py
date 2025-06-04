import numpy as np

names = ['Satoshi', 'BJK']


class SwitchType:
    Common, In_turn, End_turn = range(3)


class Signal:
    Wait, Move, Switch, End, Switch_in_turn = range(5)


class ActionType:
    Common, Mega, Z_Move, Switch, Pass = range(5)


Color = {'normal': '145,153,161',
         'flying': '142,168,222',
         'fire': '254,156,84',
         'psychic': '249,113,120',
         'water': '79,144,213',
         'bug': '145,192,46',
         'electric': '244,210,60',
         'rock': '197,183,139',
         'grass': '98,187,90',
         'ghost': '82,105,172',
         'ice': '115,206,191',
         'dragon': '10,109,194',
         'fighting': '205,64,106',
         'dark': '90,83,101',
         'poison': '169,106,200',
         'steel': '90,141,161',
         'ground': '216,120,68',
         'fairy': '235,143,230',
         '???': '68,104,94'
         }

WeatherNames = {
    'psychicterrain': 'Psychic Terrain',
    'electricterrain': 'Electric Terrain',
    'mistyterrain': 'Misty Terrain',
    'grassyterrain': 'Grassy Terrain',
    'sunnyday': 'Harsh',
    'RainDance': 'Rain',
    'hail': 'Hail',
    'Sandstorm': 'Sandstorm',
    'trickroom': 'Trick Room',
    'magicroom': 'Magic Room',
    'wonderroom': 'Wonder Room'
}

Z_MOVES = {
    'Normal': 'Breakneck Blitz',
    'Fighting': 'All-Out Pummeling',
    'Flying': 'Supersonic Skystrike',
    'Poison': 'Acid Downpour',
    'Rock': 'Continental Crush',
    'Ground': 'Tectonic Rage',
    'Bug': 'Savage Spin-Out',
    'Ghost': 'Never-Ending Nightmare',
    'Steel': 'Corkscrew Crash',
    'Fire': 'Inferno Overdrive',
    'Water': 'Hydro Vortex',
    'Grass': 'Bloom Doom',
    'Electric': 'Gigavolt Havoc',
    'Ice': 'Subzero Slammer',
    'Psychic': 'Shattered Psyche',
    'Dragon': 'Devastating Drake',
    'Dark': 'Black Hole Eclipse',
    'Fairy': 'Twinkle Tackle'
}
protect_moves = ['Protect', 'Detect', 'Spike Shield', 'King\'s Shield', 'Baneful Bunker', 'Endure']
vstatus_turn = ['taunt', 'encore', 'flinch', 'followme', 'roost', 'protect', 'disable', 'magiccoat', 'confusion',
                'partiallytrapped', 'lockon', 'embargo', 'healblock', 'spikyshield',
                'kingsshield', 'banefulbunker', 'endure']

z_crystals = {'Buginium Z': 'Bug', 'Darkinium Z': 'Dark', 'Dragonium Z': 'Dragon', 'Electrium Z': 'Electric',
              'Fairium Z': 'Fairy', 'Fightinium Z': 'Fighting', 'Firium Z': 'Fire', 'Flyinium Z': 'Flying',
              'Ghostium Z': 'Ghost', 'Grassium Z': 'Grass', 'Groundium Z': 'Ground', 'Icium Z': 'Ice',
              'Normalium Z': 'Normal', 'Poisonium Z': 'Poison', 'Psychium Z': 'Psychic', 'Rockium Z': 'Rock',
              'Steelium Z': 'Steel', 'Waterium Z': 'Water'}

mega_stones = {'Abomasite': 'Abomasnow', 'Absolite': 'Absol', 'Aerodactylite': 'Aerodactyl', 'Aggronite': 'Aggron',
               'Alakazite': 'Alakazam', 'Altarianite': 'Altaria', 'Ampharosite': 'Ampharos', 'Audinite': 'Audino',
               'Banettite': 'Banette', 'Beedrillite': 'Beedrill', 'Blastoisinite': 'Blastoise',
               'Blazikenite': 'Blaziken', 'Cameruptite': 'Camerupt', 'Charizardite X': 'Charizard',
               'Charizardite Y': 'Charizard', 'Diancite': 'Diancie',
               'Galladite': 'Gallade', 'Garchompite': 'Garchomp', 'Gardevoirite': 'Gardevoir', 'Gengarite': 'Gengar',
               'Glalitite': 'Glalie', 'Gyaradosite': 'Gyarados', 'Heracronite': 'Heracross',
               'Houndoominite': 'Houndoom', 'Kangaskhanite': 'Kangaskhan', 'Latiasite': 'Latias', 'Latiosite': 'Latios',
               'Lopunnite': 'Lopunny', 'Lucarionite': 'Lucario', 'Manectite': 'Manectric', 'Mawilite': 'Mawile',
               'Medichamite': 'Medicham', 'Metagrossite': 'Metagross', 'Mewtwonite X': 'Mewtwo',
               'Mewtwonite Y': 'Mewtwo', 'Pidgeotite': 'Pidgeot', 'Pinsirite': 'Pinsir', 'Sablenite': 'Sableye',
               'Salamencite': 'Salamence', 'Sceptilite': 'Sceptile',
               'Scizorite': 'Scizor', 'Sharpedonite': 'Sharpedo', 'Slowbronite': 'Slowbro', 'Steelixite': 'Steelix',
               'Swampertite': 'Swampert', 'Tyranitarite': 'Tyranitar', 'Venusaurite': 'Venusaur'}

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
    'tox': 'badly poisoned',
    'psn': 'poisoned',
    'par': 'paralysed',
    'frz': 'frozen'
}

full_stat = {
    'atk': 'Atk',
    'def': 'Def',
    'spa': 'Sp. Atk',
    'spd': 'Sp. Def',
    'spe': 'Spe',
    'evasion': 'Evasion',
    'accuracy': 'Accuracy',
    'ct': 'Crit. Rate'
}

upper_stat = {
    'atk': 'Atk',
    'def': 'Def',
    'spa': 'SpA',
    'spd': 'SpD',
    'spe': 'Spe',
    'evasion': 'Eva',
    'accuracy': 'Acc',
    'ct': 'Crit'

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


class Stat:
    HP, Atk, Def, SAtk, SDef, Spe = range(6)


class logType:
    common, env, ability = range(3)


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


hp_berry = {
    'Figy Berry',
    'Wiki Berry',
    'Mago Berry',
    'Aguav Berry',
    'Iapapa Berry'
}
stat_berry = {
    'Liechi Berry': 'atk',
    'Ganlon Berry': 'def',
    'Salac Berry': 'spe',
    'Petaya Berry': 'spa',
    'Apicot Berry': 'spd'
}

attr_berry = {
    'Occa Berry': 'Fire',
    'Passho Berry': 'Water',
    'Wacan Berry': 'Electric',
    'Rindo Berry': 'Grass',
    'Yache Berry': 'Ice',
    'Chople Berry': 'Fighting',
    'Kebia Berry': 'Poison',
    'Shuca Berry': 'Ground',
    'Coba Berry': 'Fighting',
    'Payapa Berry': 'Psychic',
    'Tanga Berry': 'Bug',
    'Charti Berry': 'Rock',
    'Kasib Berry': 'Ghost',
    'Haban Berry': 'Dragon',
    'Colbur Berry': 'Dark',
    'Babiri Berry': 'Steel',
    'Chilan Berry': 'Normal'
}

nature_gift = {'Cheri Berry': {'attr': 'Fire', 'pow': 80}, 'Chesto Berry': {'attr': 'Water', 'pow': 80},
               'Pecha Berry': {'attr': 'Electric', 'pow': 80}, 'Rawst Berry': {'attr': 'Grass', 'pow': 80},
               'Aspear Berry': {'attr': 'Ice', 'pow': 80}, 'Leppa Berry': {'attr': 'Fighting', 'pow': 80},
               'Oran Berry': {'attr': 'Poison', 'pow': 80}, 'Persim Berry': {'attr': 'Ground', 'pow': 80},
               'Lum Berry': {'attr': 'Flying', 'pow': 80}, 'Sitrus Berry': {'attr': 'Psychic', 'pow': 80},
               'Figy Berry': {'attr': 'Bug', 'pow': 80}, 'Wiki Berry': {'attr': 'Rock', 'pow': 80},
               'Mago Berry': {'attr': 'Ghost', 'pow': 80}, 'Aguav Berry': {'attr': 'Dragon', 'pow': 80},
               'Iapapa Berry': {'attr': 'Dark', 'pow': 80}, 'Razz Berry': {'attr': 'Steel', 'pow': 80},
               'Bluk Berry': {'attr': 'Fire', 'pow': 90}, 'Nanab Berry': {'attr': 'Water', 'pow': 90},
               'Wepear Berry': {'attr': 'Electric', 'pow': 90}, 'Pinap Berry': {'attr': 'Grass', 'pow': 90},
               'Pomeg Berry': {'attr': 'Ice', 'pow': 90}, 'Kelpsy Berry': {'attr': 'Fighting', 'pow': 90},
               'Qualot Berry': {'attr': 'Poison', 'pow': 90}, 'Hondew Berry': {'attr': 'Ground', 'pow': 90},
               'Grepa Berry': {'attr': 'Flying', 'pow': 90}, 'Tamato Berry': {'attr': 'Psychic', 'pow': 90},
               'Cornn Berry': {'attr': 'Bug', 'pow': 90}, 'Magost Berry': {'attr': 'Rock', 'pow': 90},
               'Rabuta Berry': {'attr': 'Ghost', 'pow': 90}, 'Nomel Berry': {'attr': 'Dragon', 'pow': 90},
               'Spelon Berry': {'attr': 'Dark', 'pow': 90}, 'Pamtre Berry': {'attr': 'Steel', 'pow': 90},
               'Watmel Berry': {'attr': 'Fire', 'pow': 100}, 'Durin Berry': {'attr': 'Water', 'pow': 100},
               'Belue Berry': {'attr': 'Electric', 'pow': 100}, 'Occa Berry': {'attr': 'Fire', 'pow': 80},
               'Passho Berry': {'attr': 'Water', 'pow': 80}, 'Wacan Berry': {'attr': 'Electric', 'pow': 80},
               'Rindo Berry': {'attr': 'Grass', 'pow': 80}, 'Yache Berry': {'attr': 'Ice', 'pow': 80},
               'Chople Berry': {'attr': 'Fighting', 'pow': 80}, 'Kebia Berry': {'attr': 'Poison', 'pow': 80},
               'Shuca Berry': {'attr': 'Ground', 'pow': 80}, 'Coba Berry': {'attr': 'Flying', 'pow': 80},
               'Payapa Berry': {'attr': 'Psychic', 'pow': 80}, 'Tanga Berry': {'attr': 'Bug', 'pow': 80},
               'Charti Berry': {'attr': 'Rock', 'pow': 80}, 'Kasib Berry': {'attr': 'Ghost', 'pow': 80},
               'Haban Berry': {'attr': 'Dragon', 'pow': 80}, 'Colbur Berry': {'attr': 'Dark', 'pow': 80},
               'Babiri Berry': {'attr': 'Steel', 'pow': 80}, 'Chilan Berry': {'attr': 'Normal', 'pow': 80},
               'Liechi Berry': {'attr': 'Grass', 'pow': 100}, 'Ganlon Berry': {'attr': 'Ice', 'pow': 100},
               'Salac Berry': {'attr': 'Fighting', 'pow': 100}, 'Petaya Berry': {'attr': 'Poison', 'pow': 100},
               'Apicot Berry': {'attr': 'Ground', 'pow': 100}, 'Lansat Berry': {'attr': 'Flying', 'pow': 100},
               'Starf Berry': {'attr': 'Psychic', 'pow': 100}, 'Enigma Berry': {'attr': 'Bug', 'pow': 100},
               'Micle Berry': {'attr': 'Rock', 'pow': 100}, 'Custap Berry': {'attr': 'Ghost', 'pow': 100},
               'Jaboca Berry': {'attr': 'Dragon', 'pow': 100}, 'Rowap Berry': {'attr': 'Dark', 'pow': 100},
               'Roseli Berry': {'attr': 'Fairy', 'pow': 80}, 'Kee Berry': {'attr': 'Fairy', 'pow': 100},
               'Maranga Berry': {'attr': 'Dark', 'pow': 100}}

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
