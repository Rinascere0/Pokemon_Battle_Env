from data.moves import Moves


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

        self.slot_condition = [{'healingwish': 0, 'wish': {'turn': 0, 'val': None}, 'lunardance': 0, 'heal': 0},
                               {'healingwish': 0, 'wish': {'turn': 0, 'val': None}, 'lunardance': 0, 'heal': 0}]

        self.weather = None
        self.weather_turn = 0
        # {'hail': 0, 'RainDance': 0, 'Sandstorm': 0, 'sunnyday': 0}

        self.pseudo_weather = {'fairylock': 0, 'gravity': 0, 'iondeluge': 0, 'magicroom': 0, 'mudsport': 0,
                               'trickroom': 0, 'watersport': 0, 'wonderroom': 0}

        self.terrain = None
        self.terrain_turn = 0
        # {'electricterrain': 0, 'grassyterrain': 0, 'mistyterrain': 0, 'psychicterrain': 0}
        self.uproar = False

    def set_weather(self, weather, item, log):
        if weather == 'hail' and item == 'Icy Rock' or weather == 'sunnyday' and item == 'Heat Rock' or weather == 'Sandstorm' and item == 'Smooth Rock' or weather == 'RainDance' and item == 'Damp Rock':
            turn = 8
        else:
            turn = 5
        if self.weather == weather:
            pass
        else:
            self.weather = weather
            self.weather_turn = turn
            log.add(event=weather)

    def set_terrain(self, terrain, item, log):
        if item == 'Terrain Extender':
            turn = 8
        else:
            turn = 5
        if self.terrain == terrain:
            pass
        else:
            self.terrain = terrain
            self.terrain_turn = turn
            log.add(event=terrain)

    def get_sidecond(self, pkm):
        return self.side_condition[pkm.player.pid]

    def get_slotcond(self, pkm):
        return self.slot_condition[pkm.player.pid]

    def add_slotcond(self, slotcond, pkm):
        pid = pkm.player.pid
        if slotcond == 'wish':
            self.slot_condition[pid]['wish'] = {'turn': 2, 'val': pkm.maxHP / 2}
        else:
            self.slot_condition[pid][slotcond] = 1

    def add_sidecond(self, sidecond, pkm, cond, log):
        my_sidecond = self.get_sidecond(pkm)
        if sidecond == 'toxicspikes' and my_sidecond[sidecond] > 1 \
                or sidecond == 'spikes' and my_sidecond[sidecond] > 2 \
                or 'spikes' not in sidecond and my_sidecond[sidecond] > 0:
            log.add(event='fail')
            return
        if sidecond == 'auroraveil' and self.weather['hail'] == 0:
            log.add(event='fail')
            return

        turn = 1
        if cond:
            turn = cond['duration']
            if sidecond in ['lightscreen', 'reflect', 'auroraveil'] and self.item == 'Light Clay':
                turn = 8
        else:
            if my_sidecond[sidecond]:
                log.add(event='fail')
                return
        my_sidecond[sidecond] += turn
        log.add(actor=pkm.player, event=sidecond)

    def step_pseudo_weather(self, log):
        for pd in self.pseudo_weather:
            if self.pseudo_weather[pd] > 0:
                self.pseudo_weather[pd] -= 1
                if self.pseudo_weather[pd] == 0:
                    log.add(event='-' + pd)

    def step(self, players, log):
        for player in players:
            pid = player.pid
            sidecond = self.side_condition[pid]
            for cond in ['auroraveil', 'craftyshield', 'lightscreen', 'luckychant', 'matblock', 'mist', 'quickguard',
                         'reflect', 'safeguard', 'tailwind', 'wideguard']:
                if sidecond[cond] > 0:
                    sidecond[cond] -= 1
                    if sidecond[cond] == 0:
                        log.add(actor=player, event='-' + cond)

            wish = self.slot_condition[pid]['wish']
            if wish['turn'] > 0:
                wish['turn'] -= 1
                if wish['turn'] == 0:
                    log.add(actor=wish['val'], event='+wish')
                    player.get_pivot().heal(wish['val'])
                    wish['turn'] = 0

        if self.weather_turn > 0:
            self.weather_turn -= 1
            if self.weather_turn == 0:
                log.add(event='-' + self.weather)
                self.weather = None
            else:
                log.add(event='=' + self.weather)

        if self.terrain_turn > 0:
            self.terrain_turn -= 1
            if self.terrain_turn == 0:
                log.add(event='-' + self.terrain)
                self.terrain = None

        self.step_pseudo_weather(log)

    def set_pseudo_weather(self, pseudo_weather, log):
        if self.pseudo_weather[pseudo_weather]:
            if 'room' in pseudo_weather:
                log.add(event='-' + pseudo_weather)
                self.pseudo_weather[pseudo_weather] = 0
            else:
                log.add(event='fail')
                return
        log.add(event=pseudo_weather)
        if pseudo_weather in ['fairylock', 'iondeluge']:
            self.pseudo_weather[pseudo_weather] = 1
        else:
            self.pseudo_weather[pseudo_weather] = 5

    def clear_field(self, player, type, log):
        pid = player.pid
        if type == 'spike':
            sideconds = ['stealthrock', 'toxicspikes', 'spikes', 'stickyweb']
        if type == 'wall':
            sideconds = ['reflect', 'lightscreen', 'auroraveil', 'safeguard', 'mist']
        for sidecond in sideconds:
            if self.side_condition[pid][sidecond] > 0:
                log.add(actor=player, event='clear', val=Moves[sidecond]['name'])
                self.side_condition[pid][sidecond] = 0
