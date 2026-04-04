import random
import re
from main.pokemon import Pokemon
import pickle
import os
import sys

#path = os.path.abspath(__file__)
path = getattr(sys, '_MEIPASS',  os.path.dirname(os.path.abspath(__file__)))
if 'MEI' not in path:
    path += '/..'


class TeamParseError(Exception):
    """Showdown team sheet could not be parsed."""
    pass


_TEAM_SHEET_REGEX = None


def _team_regex():
    global _TEAM_SHEET_REGEX
    if _TEAM_SHEET_REGEX is None:
        info = r'(?P<Name>[a-zA-Z\s\-]+)?((\s)\((?P<Gender>[MF])\))?((\s@ (?P<Item>[a-zA-Z\s]+))?)'
        ability = r'\n(Ability:\s(?P<Ability>[a-zA-Z0-9 \-]+))'
        shiny = r'(\nShiny:\s(?P<Shiny>[a-zA-Z]+))?'
        evs = r'(\nEVs:\s((?P<hp>[0-9]+)\sHP)?(\s\/\s)?((?P<atk>[0-9]+)\sAtk)?(\s\/\s)?((?P<def>[0-9]+)\sDef)?(\s\/\s)?((?P<spa>[0-9]+)\sSpA)?(\s\/\s)?((?P<spd>[0-9]+)\sSpD)?(\s\/\s)?((?P<spe>[0-9]+)\sSpe)?)?'
        ivs = r'(\nIVs:\s((?P<ihp>[0-9]+)\sHP)?(\s\/\s)?((?P<iatk>[0-9]+)\sAtk)?(\s\/\s)?((?P<idef>[0-9]+)\sDef)?(\s\/\s)?((?P<ispa>[0-9]+)\sSpA)?(\s\/\s)?((?P<ispd>[0-9]+)\sSpD)?(\s\/\s)?((?P<ispe>[0-9]+)\sSpe)?)?'
        nature = r'(\n(?P<Nature>[a-zA-Z]+)\sNature)?'
        move1 = r'(\n\-\s(?P<Move1>[a-zA-Z0-9 \-\[\]\']+))'
        move2 = r'(\n\-\s(?P<Move2>[a-zA-Z0-9 \-\[\]\']+))?'
        move3 = r'(\n\-\s(?P<Move3>[a-zA-Z0-9 \-\[\]\']+))?'
        move4 = r'(\n\-\s(?P<Move4>[a-zA-Z0-9 \-\[\]\']+))?'
        _TEAM_SHEET_REGEX = info + ability + shiny + evs + nature + ivs + move1 + move2 + move3 + move4
    return _TEAM_SHEET_REGEX


def validate_team_legality(pkms):
    """
    Return True if the team is allowed to battle.
    Placeholder: always accepts; implement tier/rules checks later.
    """
    return True


def list_preset_team_ids():
    """Numeric preset team files under team/ (e.g. 1, 2, …)."""
    team_dir = os.path.join(path, 'team')
    if not os.path.isdir(team_dir):
        return []
    ids = []
    for name in os.listdir(team_dir):
        if name.isdigit():
            ids.append(int(name))
    return sorted(ids)


def parse_team_sheet(text):
    """
    Parse Showdown-style team text into a list of Pokemon.
    Raises TeamParseError on failure.
    """
    if not text or not str(text).strip():
        raise TeamParseError('队伍文本为空')
    total = _team_regex()
    pkms = []
    for pm in text.split('\n\n'):
        if not pm.strip():
            continue
        m = re.search(total, pm)
        if not m:
            raise TeamParseError(f'无法解析队伍片段:\n{pm[:200]}…' if len(pm) > 200 else f'无法解析队伍片段:\n{pm}')
        res = m.groupdict()
        if res.get('Lv') is None:
            res['Lv'] = 100
        try:
            pkms.append(Pokemon(res))
        except Exception as e:
            raise TeamParseError(f'构建宝可梦失败: {e}') from e
    if len(pkms) != 6:
        raise TeamParseError(f'需要恰好 6 只宝可梦，当前为 {len(pkms)} 只')
    if not validate_team_legality(pkms):
        raise TeamParseError('队伍未通过合法性检查')
    return pkms


def read_team_by_id(tid):
    """Load preset team file team/<tid> (no random)."""
    tid = int(tid)
    team_file = os.path.join(path, 'team', str(tid))
    if not os.path.isfile(team_file):
        raise TeamParseError(f'预置队伍文件不存在: {tid}')
    with open(team_file, 'r', encoding='utf-8', errors='replace') as f:
        s = f.read()
    return parse_team_sheet(s)
def read_set():
    with open(path+'/team/ou.txt', 'r') as f:
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

    with open(path+'/team/ou.pkl', 'wb') as f:
        pickle.dump(pkm_sets, f)

    with open(path+'/team/ou.py', 'w') as f:
        f.write('ou_sets=' + str(pkm_dicts))


def read_team(tid=0):
    """Load preset team by id; tid==0 picks a random numeric preset from team/."""
    ids = list_preset_team_ids()
    if not ids:
        raise TeamParseError('team 目录下没有数字命名的预置队伍文件')
    if tid == 0:
        tid = random.choice(ids)
    else:
        tid = int(tid)
    print(path)
    print(tid)
    team_file = os.path.join(path, 'team', str(tid))
    with open(team_file, 'r', encoding='utf-8', errors='replace') as f:
        s = f.read()
    return parse_team_sheet(s)


if __name__ == '__main__':
    for i in range(28, 35):
        print(i)
        read_team(i)
