from main.client import run_client_test, run_client_1p, run_client_2p, run_client_online

valid_modes = ['1p', 'test', 'ol']
if __name__ == '__main__':
    game_mode = ''
    while game_mode not in valid_modes:
        game_mode = input('test: AI vs AI\n1p:   PVE\nol:   PVP Online\nGame Mode:')
    if game_mode == '2p':
        run_client_2p()
    elif game_mode == '1p':
        run_client_1p()
    elif game_mode == 'test':
        run_client_test()
    else:
        run_client_online()
