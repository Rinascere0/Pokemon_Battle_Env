import requests
from data.pokedex import pokedex

path = 'D:/PythonProjects/Pokemon_Battle_Env/resource/icon/'

url = 'https://www.smogon.com/dex/media/sprites/xyicons/'

fail = []
for name in pokedex:
    urlname = pokedex[name]['name'].lower().replace(' ', '-').replace('_', '-').replace('\’', '')

    try:
        full = url + urlname + '.png'
        print(full)
        r = requests.get(full)
        with open(path + name + '.png', 'wb') as f:
            f.write(r.content)
        print(name)
    except:
        fail.append(name)

print(fail)
