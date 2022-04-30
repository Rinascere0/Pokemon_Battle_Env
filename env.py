class Env:
    def __init__(self):
        self.reset()
        pass

    def reset(self):
        self.side_condition = []
        # player1 side
        self.side_condition.append({'auroraveil': 0, 'craftyshield': 0, 'lightscreen': 0,
                                    'luckychant': 0, 'matblock': 0,
                                    'mist': 0, 'quickguard': 0, 'reflect': 0, 'safeguard': 0,
                                    'spikes': 0, 'stealthrock': 0,
                                    'stickyweb': 0, 'tailwind': 0, 'toxicspikes': 0,
                                    'wideguard': 0})
        # player2 side
        self.side_condition.append({'auroraveil': 0, 'craftyshield': 0, 'lightscreen': 0,
                                    'luckychant': 0, 'matblock': 0,
                                    'mist': 0, 'quickguard': 0, 'reflect': 0, 'safeguard': 0,
                                    'spikes': 0, 'stealthrock': 0,
                                    'stickyweb': 0, 'tailwind': 0, 'toxicspikes': 0,
                                    'wideguard': 0})

        self.weather = None
        self.weather_turn = 0
        # {'hail': 0, 'RainDance': 0, 'Sandstorm': 0, 'sunnyday': 0}

        self.pseudo_weather = {'fairylock': 0, 'gravity': 0, 'iondeluge': 0, 'magicroom': 0, 'mudsport': 0,
                               'trickroom': 0, 'watersport': 0, 'wonderroom': 0}

        self.terrain = None
        self.terrain_turn = 0
        # {'electricterrain': 0, 'grassyterrain': 0, 'mistyterrain': 0, 'psychicterrain': 0}

    def set_weather(self, weather, item):
        if weather == 'hail' and item == 'Icy Rock' or weather == 'sunnyday' and item == 'Heat Rock' or weather == 'Sandstorm' and item == 'Smooth Rock' or weather == 'RainDance' and item == 'Damp Rock':
            turn = 8
        else:
            turn = 5
        if self.weather == weather:
            pass
        else:
            self.weather = weather
            self.weather_turn = turn

    def set_terrain(self, terrain, item):
        if item == 'Terrain Extender':
            turn = 8
        else:
            turn = 5
        if self.terrain == terrain:
            pass
        else:
            self.terrain = terrain
            self.terrain_turn = turn

    def set_pseudo_weather(self, pd_weather):
        self.pseudo_weather[pd_weather] = 5
