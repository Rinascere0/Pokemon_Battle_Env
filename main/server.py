import sys
import time

from PyQt5.QtWidgets import (QApplication, QMainWindow, QWidget, QVBoxLayout,
                             QTextEdit, QLineEdit, QPushButton, QLabel)
from PyQt5.QtNetwork import QTcpServer, QTcpSocket, QHostAddress
from PyQt5.QtCore import pyqtSignal, QObject, Qt

from main.game import Game

class ServerSignals(QObject):
    """定义服务器信号"""
    new_message = pyqtSignal(str)
    status_updated = pyqtSignal(str)


class Server(QTcpServer):
    """TCP服务器类"""

    def __init__(self, parent=None):
        super().__init__(parent)
        self.signals = ServerSignals()
        self.clients = []
        self.game = Game('online')
        self.game.set_server(self)
        self.game.start()
        print('server init')

    def incomingConnection(self, socketDescriptor):
        """处理新的客户端连接"""
        client_socket = QTcpSocket(self)
        client_socket.setSocketDescriptor(socketDescriptor)
        self.clients.append(client_socket)
        self.game.add_player()

        self.signals.status_updated.emit(f"新连接: {client_socket.peerAddress().toString()}:{client_socket.peerPort()}")

        client_socket.readyRead.connect(lambda: self.read_client(client_socket))
        client_socket.disconnected.connect(lambda: self.client_disconnected(client_socket))

    def read_client(self, socket):
        """读取客户端发送的数据"""
        while socket.bytesAvailable() > 0:
            data = socket.readAll().data().decode('utf-8')
            uid=self.clients.index(socket)
            print(uid, data)
            self.game.send_action(uid,eval(data))
            # DFX: display on server UI
            self.signals.new_message.emit(f"客户端: {data}")

    def client_disconnected(self, socket):
        """处理客户端断开连接"""
        self.signals.status_updated.emit(f"客户端断开: {socket.peerAddress().toString()}:{socket.peerPort()}")
        if socket in self.clients:
            self.game.remove_player(self.clients.index(socket))
            self.clients.remove(socket)
        socket.deleteLater()

    def send_message(self, message, uid=None):
        """向所有客户端发送消息"""
        target_clients = self.clients if uid is None else [self.clients[uid]]
        for client in target_clients:
            if client.state() == QTcpSocket.ConnectedState:
                client.write(message.encode('utf-8'))
                client.flush()
        # avoid two or more message in one time
        time.sleep(0.1)

class ServerWindow(QMainWindow):
    """服务器主窗口"""

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