import time
from io import StringIO

import numpy as np

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


import wget
import requests
from PIL import Image


# from StringIO import StringIO

def get_pic():
    headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 6.1; WOW64; rv:23.0) Gecko/20100101 Firefox/23.0'}
    fail = []
    last=pokedex['victini']['num']
    for idx, (_, pkm) in enumerate(pokedex.items()):
        if pkm['num']<=494:
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


#print(get_pic())
print(get_move('synthesis'))