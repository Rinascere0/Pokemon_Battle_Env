from main.client import run_client_test, run_client_1p, run_client_2p, run_client_online

valid_modes = {'0':'test','1':'1p', '2':'ol'}
if __name__ == '__main__':
    game_mode = -1
    while game_mode not in valid_modes:
        game_mode = input('0: AI vs AI\n1: PVE\n2: PVP Online\nSelect game Mode: ')
    game_mode = valid_modes[game_mode]
    if game_mode == '2p':
        run_client_2p()
    elif game_mode == '1p':
        run_client_1p()
    elif game_mode == 'test':
        run_client_test()
    else:
        run_client_online()
