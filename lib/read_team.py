import random
import re
from main.pokemon import Pokemon
import pickle
import os

path = os.path.abspath(__file__)


def read_set():
    with open(path+'/../../team/ou.txt', 'r') as f:
        s = f.read()
    info = '(?P<Name>[a-zA-Z\s\-]+)?((\s)\((?P<Gender>[MF])\))?((\s@ (?P<Item>[a-zA-Z\s]+))?)'
    ability = '\n(Ability:\s(?P<Ability>[a-zA-Z0-9 \-]+))'
    shiny = '(\nShiny:\s(?P<Shiny>[a-zA-Z]+))?'
    evs = '(\nEVs:\s((?P<hp>[0-9]+)\sHP)?(\s\/\s)?((?P<atk>[0-9]+)\sAtk)?(\s\/\s)?((?P<def>[0-9]+)\sDef)?(\s\/\s)?((?P<spa>[0-9]+)\sSpA)?(\s\/\s)?((?P<spd>[0-9]+)\sSpD)?(\s\/\s)?((?P<spe>[0-9]+)\sSpe)?)?'
    ivs = '(\nIVs:\s((?P<ihp>[0-9]+)\sHP)?(\s\/\s)?((?P<iatk>[0-9]+)\sAtk)?(\s\/\s)?((?P<idef>[0-9]+)\sDef)?(\s\/\s)?((?P<ispa>[0-9]+)\sSpA)?(\s\/\s)?((?P<ispd>[0-9]+)\sSpD)?(\s\/\s)?((?P<ispe>[0-9]+)\sSpe)?)?'
    nature = '(\n(?P<Nature>[a-zA-Z]+)\sNature)?'
    move1 = '(\n\-\s(?P<Move1>[a-zA-Z0-9 \-\[\]]+))'
    move2 = '(\n\-\s(?P<Move2>[a-zA-Z0-9 \-\[\]]+))?'
    move3 = '(\n\-\s(?P<Move3>[a-zA-Z0-9 \-\[\]]+))?'
    move4 = '(\n\-\s(?P<Move4>[a-zA-Z0-9 \-\[\]]+))?'
    total = info + ability + shiny + evs + ivs + nature + move1 + move2 + move3 + move4
    pms = s.split('\n\n')

    pkm_sets = {}
    pkm_dicts = {}
    for pm in pms[:-1]:
        res = re.search(total, pm).groupdict()
        if 'Lv' not in res:
            res['Lv'] = 100
        pkm = Pokemon(res)
        name = pkm.name
        if name in pkm_sets:
            pkm_sets[name].append(pkm)
            pkm_dicts[name].append(res)
        else:
            pkm_sets[name] = [pkm]
            pkm_dicts[name] = [res]

    with open(path+'/../../team/ou.pkl', 'wb') as f:
        pickle.dump(pkm_sets, f)

    with open(path+'/../../team/ou.py', 'w') as f:
        f.write('ou_sets=' + str(pkm_dicts))


def read_team(tid=0):
    if tid == 0:
        tid = random.choice(list(range(1, 28)))
    with open(path+'/../../team/' + str(tid), 'r') as f:
        s = f.read()

    print(tid)
    info = '(?P<Name>[a-zA-Z\s\-]+)?((\s)\((?P<Gender>[MF])\))?((\s@ (?P<Item>[a-zA-Z\s]+))?)'
    ability = '\n(Ability:\s(?P<Ability>[a-zA-Z0-9 \-]+))'
    shiny = '(\nShiny:\s(?P<Shiny>[a-zA-Z]+))?'
    evs = '(\nEVs:\s((?P<hp>[0-9]+)\sHP)?(\s\/\s)?((?P<atk>[0-9]+)\sAtk)?(\s\/\s)?((?P<def>[0-9]+)\sDef)?(\s\/\s)?((?P<spa>[0-9]+)\sSpA)?(\s\/\s)?((?P<spd>[0-9]+)\sSpD)?(\s\/\s)?((?P<spe>[0-9]+)\sSpe)?)?'
    ivs = '(\nIVs:\s((?P<ihp>[0-9]+)\sHP)?(\s\/\s)?((?P<iatk>[0-9]+)\sAtk)?(\s\/\s)?((?P<idef>[0-9]+)\sDef)?(\s\/\s)?((?P<ispa>[0-9]+)\sSpA)?(\s\/\s)?((?P<ispd>[0-9]+)\sSpD)?(\s\/\s)?((?P<ispe>[0-9]+)\sSpe)?)?'
    nature = '(\n(?P<Nature>[a-zA-Z]+)\sNature)?'
    move1 = '(\n\-\s(?P<Move1>[a-zA-Z0-9 \-\[\]\']+))'
    move2 = '(\n\-\s(?P<Move2>[a-zA-Z0-9 \-\[\]\']+))?'
    move3 = '(\n\-\s(?P<Move3>[a-zA-Z0-9 \-\[\]\']+))?'
    move4 = '(\n\-\s(?P<Move4>[a-zA-Z0-9 \-\[\]\']+))?'
    total = info + ability + shiny + evs + nature + ivs + move1 + move2 + move3 + move4
    pms = s.split('\n\n')
    pkms = []
    for pm in pms:
        #   print(pm)
        res = re.search(total, pm).groupdict()
        if 'Lv' not in res:
            res['Lv'] = 100
        pkms.append(Pokemon(res))
    return pkms


if __name__ == '__main__':
    for i in range(28, 35):
        print(i)
        read_team(i)
