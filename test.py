import numpy as np

from data.moves import Moves
from data.pokedex import pokedex
import random

# for move, i in Moves.items():
#    if 'self' in i and ('secondary' in i and i['secondary'] is not None or 'secondaries' in i):
#        print(move)

# print(Moves['endeavor'])

# for name,move in Moves.items():
#    if 'damage' in move:
#        print(name,move['damage'])

# for name,move in Moves.items():
#    if 'ohko' in move:
#       print(name,move['ohko'])

import math


def get_key(key):
    d={}
    for name, move in Moves.items():
        if  key in move:
            print(name,move[key])

def get_key2(key,key2):
    d={}
    for name, move in Moves.items():
        if  key in move and key2 in move and move[key] and move[key2]:
            print(name,move[key],move[key2])

def get_move(name):
    print(Moves[name])


def f():
    return 1, 2
get_key2('secondaries','volatileStatus')
