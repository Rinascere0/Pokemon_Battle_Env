from main.client import run_client_test, run_client_1p, run_client_online, run_client_replay

valid_modes = {'0': 'test', '1': '1p', '2': 'ol', '3': 'replay'}
if __name__ == '__main__':
    game_mode = -1
    while game_mode not in valid_modes:
        game_mode = input(
            '0: AI vs AI\n'
            '1: PVE\n'
            '2: PVP Online\n'
            '3: Replay (playback only)\n'
            'Select game Mode: '
        )
    game_mode = valid_modes[game_mode]
    if game_mode == 'replay':
        run_client_replay()
    elif game_mode == 'ol':
        run_client_online()
    elif game_mode == '1p':
        run_client_1p()
    elif game_mode == 'test':
        run_client_test()
