from main.client import run_client_test,run_client_1p,run_client_2p

game_mode = 'test'
if __name__ == '__main__':
    if game_mode=='2p':
        run_client_2p()
    elif game_mode=='1p':
        run_client_1p()
    else:
        run_client_test()
