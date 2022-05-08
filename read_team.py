import random
import re
from pokemon import Pokemon
import pickle


def read_set():
    with open('team/ou.txt', 'r') as f:
        s = f.read()
    info = '(?P<Name>[a-zA-Z\s\-]+)?((\s)\((?P<Gender>[MF])\))?((\s@ (?P<Item>[a-zA-Z\s]+))?)'
    ability = '\n(Ability:\s(?P<Ability>[a-zA-Z0-9 \-]+))'
    shiny = '(\nShiny:\s(?P<Shiny>[a-zA-Z]+))?'
    evs = '(\nEVs:\s((?P<HP>[0-9]+)\sHP)?(\s\/\s)?((?P<Atk>[0-9]+)\sAtk)?(\s\/\s)?((?P<Def>[0-9]+)\sDef)?(\s\/\s)?((?P<SpA>[0-9]+)\sSpA)?(\s\/\s)?((?P<SpD>[0-9]+)\sSpD)?(\s\/\s)?((?P<Spe>[0-9]+)\sSpe)?)?'
    ivs = '(\nIVs:\s((?P<iHP>[0-9]+)\sHP)?(\s\/\s)?((?P<iAtk>[0-9]+)\sAtk)?(\s\/\s)?((?P<iDef>[0-9]+)\sDef)?(\s\/\s)?((?P<iSpA>[0-9]+)\sSpA)?(\s\/\s)?((?P<iSpD>[0-9]+)\sSpD)?(\s\/\s)?((?P<iSpe>[0-9]+)\sSpe)?)?'
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

    with open('team/ou.pkl', 'wb') as f:
        pickle.dump(pkm_sets, f)

    with open('team/ou.py', 'w') as f:
        f.write('ou_sets=' + str(pkm_dicts))


def read_team(tid=6):
    if tid == 0:
        tid = random.choice(list(range(1,28)))
    with open('team/' + str(tid), 'r') as f:
        s = f.read()

    info = '(?P<Name>[a-zA-Z\s\-]+)?((\s)\((?P<Gender>[MF])\))?((\s@ (?P<Item>[a-zA-Z\s]+))?)'
    ability = '\n(Ability:\s(?P<Ability>[a-zA-Z0-9 \-]+))'
    shiny = '(\nShiny:\s(?P<Shiny>[a-zA-Z]+))?'
    evs = '(\nEVs:\s((?P<HP>[0-9]+)\sHP)?(\s\/\s)?((?P<Atk>[0-9]+)\sAtk)?(\s\/\s)?((?P<Def>[0-9]+)\sDef)?(\s\/\s)?((?P<SpA>[0-9]+)\sSpA)?(\s\/\s)?((?P<SpD>[0-9]+)\sSpD)?(\s\/\s)?((?P<Spe>[0-9]+)\sSpe)?)?'
    ivs = '(\nIVs:\s((?P<iHP>[0-9]+)\sHP)?(\s\/\s)?((?P<iAtk>[0-9]+)\sAtk)?(\s\/\s)?((?P<iDef>[0-9]+)\sDef)?(\s\/\s)?((?P<iSpA>[0-9]+)\sSpA)?(\s\/\s)?((?P<iSpD>[0-9]+)\sSpD)?(\s\/\s)?((?P<iSpe>[0-9]+)\sSpe)?)?'
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
     #   res['Name'] = (res['Name'].split('-Mega')[0]).split('-Ash')[0]
     #   if '-Mega-X' in res['Name']:
     #       res['Name'] = res['Name'].replace('-Mega-X', '')
     #   if '-Mega-X' in res['Name']:
     #       res['Name'] = res['Name'].replace('-Mega-Y', '')
     #   if '-Ash' in res['Name']:
     #       res['Name'] = res['Name'].replace('-Ash', '')
     #   if '-Mega' in res['Name']:
     #       res['Name'] = res['Name'].replace('-Mega', '')
        pkms.append(Pokemon(res))

    return pkms


if __name__ == '__main__':
    for i in range(28,35):
        print(i)
        read_team(i)
