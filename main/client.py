import random

from PyQt5.QtCore import QObject, pyqtSignal
from PyQt5.QtNetwork import QTcpSocket, QHostAddress, QAbstractSocket
from PyQt5.QtWidgets import QApplication
import sys

from main.client_ui import Client_UI
from main.game import Game

LOG, STATE = 0, 1


class ClientSignals(QObject):
    new_message = pyqtSignal(str)
    status_updated = pyqtSignal(str)

class Client(QObject):
    def __init__(self, uid):
        super().__init__()
        # plyaer id
        self.uid= uid
        self.inited = True
        self.ui = None

        # offline
        self.game = None
        self.team_wire_payload = 'RANDOM'

        # online
        self.socket = QTcpSocket(self)
        self.signals = ClientSignals()
        # key of client socket in server
        self.key_id = random.randint(1,10000)
        self.socket.readyRead.connect(self.read_data)
        self.socket.connected.connect(self.on_connected)
        self.socket.connected.connect(lambda: self.signals.status_updated.emit("Connected to server!"))
        self.socket.disconnected.connect(lambda: self.signals.status_updated.emit("Disconnected from server!"))
        self.socket.errorOccurred.connect(self.handle_error)

    def connect_to_server(self, host, port, username, password):
        self.username = username
        self.password = password
        self.socket.connectToHost(host, port)

    def on_connected(self):
        self.socket.setSocketOption(QAbstractSocket.ReceiveBufferSizeSocketOption, 65536)
        tw = getattr(self, 'team_wire_payload', None) or 'RANDOM'
        msg_key_id = f'${self.username}${self.password}|TEAM|{tw}'
        self.send_message(msg_key_id)


    def disconnect_from_server(self):
        self.socket.disconnectFromHost()

    def set_ui(self,ui):
        self.ui = ui
        self.socket.disconnected.connect(self.ui.onDisconnect)

    # send message to server
    def send_message(self, message):
        if self.socket.state() == QTcpSocket.ConnectedState:
            print(f'sent {message}')
            self.socket.write(message.encode('utf-8'))
            self.socket.flush()

    # receive message from server
    def read_data(self):
        while self.socket.bytesAvailable() > 0:
            print('read msg!')
            data = self.socket.readAll().data().decode('utf-8')
        #    self.signals.new_message.emit(f"Server: {data}")
            self.signals.new_message.emit(data)

    def handle_error(self, socket_error):
        self.signals.status_updated.emit(f"Error: {self.socket.errorString()}")

    # used in local mode
    def set_game(self,game):
        self.game = game

    def set_pending_team_choice(self, choice):
        if choice is None:
            self.team_wire_payload = 'RANDOM'
        else:
            self.team_wire_payload = choice.to_wire()

    def apply_team_choice_to_player(self, choice):
        if self.game is None or self.uid >= len(self.game.players):
            return
        pl = self.game.players[self.uid]
        if hasattr(pl, 'apply_team_choice'):
            pl.apply_team_choice(choice)

    def request_surrender(self):
        if self.game:
            self.game.request_surrender(self.uid)
        elif self.socket.state() == QTcpSocket.ConnectedState:
            self.send_message('__SURRENDER__')

    # used in local mode
    # receive message from server, flush ui state or add log(or both)
    def recv_msg(self,msg):
        if self.ui:
            # print(f'recv msg: {msg}')
            self.ui.send_log(msg)

    # send action to server, activated by ui signal
    def send_action(self,action_type,item):
        action = {'type':action_type,'item':item}
        # offline
        if self.game:
            self.game.send_action(self.uid,action)
        # online
        else:
            msg = action
            self.send_message(str(msg))


def run_client_test():
    game = Game(mode='test')
    game.start()
    # add client0
    client0 = Client(0)
    # add client1
    client1 = Client(1)
    game.set_client(client0)
    game.set_client(client1)

def run_client_1p():
    app = QApplication(sys.argv)
    game = Game(mode='1p')
    client0 = Client(0)
    client1 = Client(1)
    game.set_client(client0)
    game.set_client(client1)
    game.start()
    ui1 = Client_UI(client1, 1)
    game.ui_init(1)

    app.exec_()
    game.force_end()

def run_client_2p():
    app = QApplication(sys.argv)
    game = Game(mode='2p')
    client0 = Client(0)
    client1 = Client(1)
    game.set_client(client0)
    game.set_client(client1)
    game.start()
    ui0 = Client_UI(client0, 0)
    ui1 = Client_UI(client1, 1)
    game.ui_init(0)
    game.ui_init(1)

    app.exec_()
    game.force_end()

def run_client_online():
    app = QApplication(sys.argv)
    client = Client(0)
    ui = Client_UI(client,0,True)
    app.exec_()

if __name__ == '__main__':
    run_client_online()
