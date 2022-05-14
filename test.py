import time

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


def get_pic():
    last_stop = 'pikachuworld'

    for idx, (key, pkm) in enumerate(pokedex.items()):
        if key == last_stop:
            last_idx = idx
    for idx, (_, pkm) in enumerate(pokedex.items()):
        if idx <= last_idx:
            continue
        name = pkm['name'].lower()
        if 'gmax' in name:
            continue
        url = 'https://www.smogon.com/dex/media/sprites/xy/' + name + '.gif'
        print(url)
        path = 'D:/resource/' + name + '.gif'
        try:
            wget.download(url, path)  # 下载
        except:
            continue


get_pic()
