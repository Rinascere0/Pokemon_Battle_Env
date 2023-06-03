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

        self.slot_condition = [{'healingwish': 0, 'Wish': None, 'lunardance': 0, 'heal': 0},
                               {'healingwish': 0, 'Wish': None, 'lunardance': 0, 'heal': 0}]
        # real weather
        self.real_weather = None
        # effect weather (None if air lock)
        self.weather = None
        self.weather_turn = 0
        # {'hail': 0, 'RainDance': 0, 'Sandstorm': 0, 'sunnyday': 0}

        self.pseudo_weather = {'fairylock': 0, 'gravity': 0, 'iondeluge': 0, 'magicroom': 0, 'mudsport': 0,
                               'trickroom': 0, 'watersport': 0, 'wonderroom': 0}

        self.terrain = None
        self.terrain_turn = 0
        # {'electricterrain': 0, 'grassyterrain': 0, 'mistyterrain': 0, 'psychicterrain': 0}
        self.uproar = False
        self.air_lock = False

    def set_weather(self, weather, item, log):
        if weather == 'hail' and item == 'Icy Rock' or weather == 'sunnyday' and item == 'Heat Rock' or weather == 'Sandstorm' and item == 'Smooth Rock' or weather == 'RainDance' and item == 'Damp Rock':
            turn = 8
        else:
            turn = 5
        if self.real_weather == weather:
            return False
        else:
            self.real_weather = weather
            self.weather_turn = turn
            log.add(event=weather)
        if not self.air_lock:
            self.weather = weather

        return True

    def set_terrain(self, terrain, item, log):
        if item == 'Terrain Extender':
            turn = 8
        else:
            turn = 5
        if self.terrain == terrain:
            return False
        else:
            self.terrain = terrain
            self.terrain_turn = turn
            log.add(event=terrain)
        return True

    def get_sidecond(self, pkm):
        return self.side_condition[pkm.player.pid]

    def get_slotcond(self, pkm):
        return self.slot_condition[pkm.player.pid]

    def add_slotcond(self, slotcond, pkm):
        mySlotcond = self.get_slotcond(pkm)
        if mySlotcond[slotcond]:
            return False
        if slotcond == 'Wish':
            mySlotcond['Wish'] = {'turn': 2, 'val': pkm.maxHP / 2}
        else:
            mySlotcond[slotcond] = 1
        return True

    def add_sidecond(self, sidecond, pkm, cond, log):
        my_sidecond = self.get_sidecond(pkm)
        if sidecond == 'toxicspikes' and my_sidecond[sidecond] > 1 \
                or sidecond == 'spikes' and my_sidecond[sidecond] > 2 \
                or 'spikes' not in sidecond and my_sidecond[sidecond] > 0:
            return False
        if sidecond == 'auroraveil' and self.weather != 'hail':
            return False

        turn = 1
        if cond:
            turn = cond['duration']
            if sidecond in ['lightscreen', 'reflect', 'auroraveil'] and pkm.item == 'Light Clay':
                turn = 8

        my_sidecond[sidecond] += turn
        log.add(actor=pkm.player, event=sidecond)
        return True

    def step_pseudo_weather(self, log):
        for pd in self.pseudo_weather:
            if self.pseudo_weather[pd] > 0:
                self.pseudo_weather[pd] -= 1
                if self.pseudo_weather[pd] == 0:
                    log.add(event='-' + pd)

    def set_air_lock(self, flag):
        self.air_lock += flag
        if self.air_lock > 0:
            self.weather = None
        else:
            self.weather = self.real_weather

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

            slotcond = self.slot_condition[pid]
            if slotcond['Wish']:
                slotcond['Wish']['turn'] -= 1
                if slotcond['Wish']['turn'] == 0:
                    log.add(actor=player.get_pivot(), event='+wish')
                    player.get_pivot().heal(slotcond['Wish']['val'])
                    slotcond['Wish'] = None

        if self.weather_turn > 0:
            self.weather_turn -= 1
            if self.weather_turn == 0:
                log.add(event='-' + self.real_weather)
                self.weather = None
            else:
                log.add(event='=' + self.real_weather)

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
        else:
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
