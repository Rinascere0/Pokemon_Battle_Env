import sys
import time
from threading import Thread

from PyQt5.QtWidgets import (QApplication, QMainWindow, QWidget, QVBoxLayout,
                             QTextEdit, QLineEdit, QPushButton, QLabel)
from PyQt5.QtNetwork import QTcpServer, QTcpSocket, QHostAddress
from PyQt5.QtCore import pyqtSignal, QObject, Qt

from main.game import Game

WAIT,START,END=0,1,2
DISCONNECT, READY = 0,1
class ServerSignals(QObject):
    new_message = pyqtSignal(str)
    status_updated = pyqtSignal(str)


class Server(QTcpServer):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.signals = ServerSignals()
        self.clients = []
        # {game_id:game}
        self.games = {}
        # {game_id:[socket0,socket1]}
        self.game_clients = {}
        self.game_status = []
        self.game_waiting = None
        # {client_key:{'game_id':,'uid':,'status':}
        self.game_players = {}
        print('server init')
        self.game_id = 0

    def create_game(self):
        self.game_id +=1
        game_id = self.game_id
        game = Game(self.game_id,'online')
        game.set_server(self)
        game.start()
        self.games[game_id] = game
        self.game_clients[game_id]=[]
        return game

    def remove_game(self,game_id):
        del self.games[game_id]
        del self.game_clients[game_id]
        print('remove game:',game_id)

    def gen_client_key(self,socket):
        client_key = socket.peerAddress().toString() + str(socket.peerPort())
        return client_key

    def remove_player_timeout(self,client_key):
        # get game_id and uid
        client_info = self.game_players[client_key]
        game_id,uid=client_info['game_id'],client_info['uid']
        print('remove!!')
        # wait 300s to re-connect if game start
        if self.games[game_id].get_status() == START:
            print('remove!!!!')
            print(self.game_players[client_key]['status'])
            while self.game_players[client_key]['status'] == DISCONNECT:
                time.sleep(1)
                print(client_key,' disconnect')

        # if client status DISCONNECT, delete client
        if self.game_players[client_key]['status'] == DISCONNECT:
            # remove player from game
            self.games[game_id].remove_player(uid)
            # delete client player info
            del(self.game_players[client_key])

    # if a player disconnect after a game start, wait 300s until deletion
    # else, just remove player
    def remove_player(self, socket):
        # set client status DISCONNECT
        client_key = self.gen_client_key(socket)
        self.game_players[client_key]['status'] = DISCONNECT
        print('start remove')
        thread = Thread(target=self.remove_player_timeout, args=(client_key,))
        thread.start()


    def incomingConnection(self, socketDescriptor):
        client_socket = QTcpSocket(self)
        client_socket.setSocketDescriptor(socketDescriptor)
        self.clients.append(client_socket)
        if not self.game_waiting:
            game = self.create_game()
            self.game_waiting = game
        else:
            game = self.game_waiting
            self.game_waiting = None
        uid = game.add_player()
        # check if exist client key
        client_key = self.gen_client_key(client_socket)
        print('new connect client_key',client_key)
        if client_key in self.game_players:
            print(client_key,'reconnect!!')
            self.game_players[client_key]['status'] = READY
        else:
            self.game_players[client_key]={
                'uid':uid,
                'game_id':game.game_id,
                'status':READY
            }
            self.game_clients[game.game_id].insert(uid, client_socket)

        self.signals.status_updated.emit(f"New Connection: {client_socket.peerAddress().toString()}:{client_socket.peerPort()}")

        client_socket.readyRead.connect(lambda: self.read_client(client_socket))
        client_socket.disconnected.connect(lambda: self.client_disconnected(client_socket))

    def client_disconnected(self, socket):
        self.signals.status_updated.emit(f"Client Disconnectd: {socket.peerAddress().toString()}:{socket.peerPort()}")
        self.remove_player(socket)
        self.clients.remove(socket)
        socket.deleteLater()

    def read_client(self, socket):
        while socket.bytesAvailable() > 0:
            data = socket.readAll().data().decode('utf-8')
            # find game_id & uid according to socket key
            client_key = self.gen_client_key(socket)
            uid=self.game_players[client_key]['uid']
            game_id = self.game_players[client_key]['game_id']
            # send action to game
            self.games[game_id].send_action(uid,eval(data))
            # DFX: display on server UI
            self.signals.new_message.emit(f"Client: {data}")

    def send_message(self, message, game_id=0, uid=None):
        # if uid is None, send to all clients of Game game_id
        # else only send to client uid
        print('send message game_id',game_id,'uid',uid)
        target_clients = self.game_clients[game_id] if uid is None else [self.game_clients[game_id][uid]]
        for client in target_clients:
            if client.state() == QTcpSocket.ConnectedState:
                client.write(message.encode('utf-8'))
                client.flush()
        # avoid two or more message in one time
        time.sleep(0.1)

class ServerWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("TCP服务器")
        self.resize(600, 400)

        self.central_widget = QWidget()
        self.setCentralWidget(self.central_widget)
        self.layout = QVBoxLayout(self.central_widget)

        # 状态标签
        self.status_label = QLabel("服务器未启动")
        self.layout.addWidget(self.status_label)

        # 消息显示区域
        self.message_display = QTextEdit()
        self.message_display.setReadOnly(True)
        self.layout.addWidget(self.message_display)

        # 输入区域
        self.message_input = QLineEdit()
        self.message_input.setPlaceholderText("输入消息...")
        self.message_input.returnPressed.connect(self.send_message)
        self.layout.addWidget(self.message_input)

        # 发送按钮
        self.send_button = QPushButton("发送")
        self.send_button.clicked.connect(self.send_message)
        self.layout.addWidget(self.send_button)

        # 启动服务器按钮
        self.start_button = QPushButton("启动服务器")
        self.start_button.clicked.connect(self.start_server)
        self.layout.addWidget(self.start_button)

        # 服务器实例
        self.server = Server()
        self.server.signals.new_message.connect(self.update_messages)
        self.server.signals.status_updated.connect(self.update_status)

        self.port = 12333  # 默认端口

    def start_server(self):
        """启动服务器"""
        if not self.server.isListening():
            if self.server.listen(QHostAddress.Any, self.port):
                self.status_label.setText(f"服务器在端口 {self.port} 上监听")
                self.start_button.setText("停止服务器")
            else:
                self.status_label.setText(f"无法启动服务器: {self.server.errorString()}")
        else:
            self.server.close()
            self.status_label.setText("服务器已停止")
            self.start_button.setText("启动服务器")

    def send_message(self):
        """发送消息"""
        message = self.message_input.text().strip()
        if message and self.server.isListening():
            self.server.send_message(message)
            self.message_display.append(f"服务器: {message}")
            self.message_input.clear()

    def update_messages(self, message):
        """更新消息显示"""
        self.message_display.append(message)


    def update_status(self, status):
        """更新状态显示"""
        self.message_display.append(f"[状态] {status}")


if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = ServerWindow()
    window.show()
    sys.exit(app.exec_())