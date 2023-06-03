import time
from io import StringIO

import numpy as np
from lib.functions import pkm_to_key

from data.moves import Moves
from data.pokedex import pokedex


def get_nkey(key):
    for name, move in Moves.items():
        if key not in move:
            print(name)


def get_key(key):
    for name, move in Moves.items():
        if key in move and move['category'] != 'Status':
            print(name, move[key])


def get_key2(key, key2):
    d = {}
    for name, move in Moves.items():
        if key in move and key2 in move and move[key] and move[key2]:
            print(name, move[key], move[key2])


def get_key3(key, key2):
    d = {}
    for name, move in Moves.items():
        if key in move and move[key]:
            if key2 in move[key]:
                print(name, move[key][key2])


def get_move(name):
    print(Moves[name])

    # get_key2('volatileStatus', 'condition')
    # get_key('volatileStatus')
    # get_key('self')
    # get_nkey('flags')
    # get_move('spiritshackle')


#import wget
import requests
from PIL import Image


# from StringIO import StringIO

def get_pic():
    headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 6.1; WOW64; rv:23.0) Gecko/20100101 Firefox/23.0'}
    fail = []
    last = pokedex['victini']['num']
    for idx, (_, pkm) in enumerate(pokedex.items()):
        if pkm['num'] <= 494:
            continue
        name = pkm['name'].replace(' ', '-').lower()
        if 'gmax' in name:
            continue
        url = 'https://play.pokemonshowdown.com/sprites/ani-back/' + name + '.gif'
        try:
            response = requests.get(url, headers=headers)
            print(url)
            path = 'D:/resource/back/' + name + '.gif'
            with open(path, 'wb') as f:
                f.write(response.content)
        except:
            print('fail:', name)
            fail.append(name)
    #   try:
    #       wget.download(url, path)  # 下载
    #   except Exception as e:
    #       print(repr(e))
    #

    return fail


import re

def gen_moveset():
    with open('docs/moveset.txt', 'r') as f:
        moveset_str = f.read()
        # regex patterns
        perc_regex = '[0-9]+\.[0-9]+\%'
        ability_regex = '[a-zA-Z\-\s]+\s'
        ev_regex = '[0-9]+'
        spread_regex = '(?P<nature>[a-zA-Z]+)\:'
        single_move_regex = '[a-zA-Z\-\s\[\]\']+'
        for key in ['hp', 'atk', 'def', 'spa', 'spd', 'spe']:
            spread_regex += '(?P<' + key + '>' + ev_regex + ')\/'
        pkm_set_strs = moveset_str.split(
            ' +----------------------------------------+ \n +----------------------------------------+')

        movesets = {}
        for pkm_set_str in pkm_set_strs:
            pkm_strs = pkm_set_str.split('+----------------------------------------+')
            # name
            pkm_name = pkm_to_key(pkm_strs[0].replace('|', '').replace('\n', ''))
            # ability
            pkm_ability = pkm_strs[2].replace('|', '').replace('Abilities', '').strip()
            pkm_ability = re.search(ability_regex, pkm_ability).group().strip()
            # item
            pkm_item = pkm_strs[3].replace('|', '').replace('Items', '').strip()
            pkm_item = re.search(ability_regex, pkm_item).group().strip()
            # spread
            pkm_spread = pkm_strs[4].replace('|', '').replace('Spreads', '').strip()
            pkm_spread = re.search(spread_regex[:-2], pkm_spread).groupdict()
            pkm_nature = pkm_spread['nature']
            pkm_spread.pop('nature')
            for key in pkm_spread:
                pkm_spread[key]=int(pkm_spread[key])
            # move
            pkm_move = pkm_strs[5].replace('|', '').replace('Moves', '').strip()
            move_count = pkm_move.count('\n')
            pkm_move = pkm_move.replace('\n', '')
            move_regex = ''
            for i in range(move_count):
                move_regex += '(?P<move' + str(i) + '>' + single_move_regex + ')\s(?P<perc' + str(
                    i) + '>' + perc_regex + ')'
            pkm_move = re.search(move_regex, pkm_move).groupdict()
            for key in pkm_move:
                pkm_move[key] = pkm_move[key].strip()
            for i in range(move_count):
                pkm_move['perc'+str(i)]=round(float(pkm_move['perc'+str(i)][:-1])/100,2)
            # total info

            moves={}
            for i in range(move_count):
                move_name=pkm_move['move'+str(i)]
                moves[move_name]=pkm_move['perc'+str(i)]
            pkm_info = {'name': pkm_name, 'ability': pkm_ability, 'item': pkm_item, 'nature':pkm_nature,'spread': pkm_spread,
                        'moves': moves}



            movesets[pkm_name] = pkm_info
        print('moveset=',movesets)


print(get_move('spikyshield'))