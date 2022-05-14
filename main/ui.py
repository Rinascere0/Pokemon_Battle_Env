import sys
import time
import os

path = os.path.abspath(__file__) + '/../../resource/'
pkm_path = path + 'pkm/'

from PyQt5.QtGui import QFont, QPixmap, QMovie
from PyQt5.QtWidgets import QApplication, QWidget, QTextEdit, QLabel, QPushButton, QCheckBox
from PyQt5.QtCore import pyqtSignal

from threading import Thread

from game import Game


class UI(QWidget):
    add_signal = pyqtSignal(str)

    def __init__(self):
        super(UI, self).__init__()
        self.inited = False
        self.game = Game()
        self.game.start()

        player = self.game.get_ui_player()
        player.set_ui(self)
        self.init_ui()

        self.inited = True

    def setText(self):
        state = self.game.get_state(1)
        Round = state['round']
        self.round_label.setText('Round ' + str(Round))

        my_team = state['my_team']
        my_pkms = my_team['pkms']

        foe_team = state['foe_team']
        foe_pkms = foe_team['pkms']

        # show pivots
        pivot = my_pkms[my_team['pivot']]
        #     self.myPivot.setPixmap(QPixmap())

        foe_pivot = foe_pkms[foe_team['pivot']]
        self.foePivot.setPixmap(QPixmap(pkm_path + foe_pivot['name'].lower() + '.gif'))

        # show my mini teams
        for i, pkm in enumerate(my_pkms):
            name = pkm['name']
            print(name)
            self.pkms[i].setText(name + '\n' + str(pkm['hp']) + '/' + str(pkm['maxhp']))
            self.mypkm_mini[i].setPixmap(QPixmap(pkm_path + name.replace(' ', '-').lower() + '.gif'))
            self.mypkm_mini[i].setScaledContents(True)

        # show my moves
        pivot = my_team['pivot']
        # print(my_pkms[pivot]['moves'])
        for i, move in enumerate(my_pkms[pivot]['moves']):
            self.moves[i].setText(move['name'] + '\n' + str(move['pp']) + '/' + str(move['maxpp']))

        # show foe mini team
        for i, pkm in enumerate(foe_pkms):
            name = pkm['name']
            self.foepkm_mini[i].setPixmap(QPixmap(pkm_path + name.replace(' ', '-').lower() + '.gif'))
            self.foepkm_mini[i].setScaledContents(True)

    def init_ui(self):
        self.setFixedSize(1130, 720)
        self.move(300, 300)

        # field
        self.bg = QLabel(self)
        self.bg.setGeometry(0, 0, 600, 370)
        self.bg.setPixmap(QPixmap(path + 'bg.png'))
        self.bg.setScaledContents(True)

        self.log = QTextEdit(self)
        self.log.setReadOnly(True)
        self.log.setGeometry(580, 0, 550, 600)
        self.log.setFont(QFont("Consolas", 10, 30))
        with open('D:\PycharmProjects\Pokemon_Battle_Env\docs\demo.txt','r') as f:
            log=f.read()
        self.log.setText(log)

        self.myPivot = QLabel(self)
        self.myPivot.setGeometry(50, 130, 250, 250)
        self.myMovie = QMovie(path + 'charizard.png')
        self.myPivot.setMovie(self.myMovie)
        self.myMovie.jumpToFrame(0)

        self.foePivot = QLabel(self)
        self.foePivot.setGeometry(350, 0, 250, 250)

        # round info
        self.round_label = QLabel(self)
        self.round_label.setGeometry(85, 25, 120, 50)
        self.round_label.setStyleSheet("color:rgb(255,228,181,100)")
        self.round_label.setFont(QFont("Microsoft YaHei", 15, 75))

        self.left_margin = QLabel(self)
        self.left_margin.setStyleSheet("background-color:rgb(0,0,0,50)")
        self.left_margin.setGeometry(0, 0, 60, 370)

        self.right_margin = QLabel(self)
        self.right_margin.setStyleSheet("background-color:rgb(0,0,0,50)")
        self.right_margin.setGeometry(520, 0, 60, 370)

        self.mypkm_mini = [QLabel(self) for _ in range(6)]
        for i, label in enumerate(self.mypkm_mini):
            label.setGeometry(10, 60 + 50 * i, 45, 45)

        self.foepkm_mini = [QLabel(self) for _ in range(6)]
        for i, label in enumerate(self.foepkm_mini):
            label.setGeometry(530, 50 * i, 45, 45)

        # move button
        self.moves = [QPushButton(self) for _ in range(4)]
        for i, move in enumerate(self.moves):
            move.clicked.connect(self.send)
            move.setFont(QFont("Consolas", 11, 30))

        self.moves[0].setGeometry(50, 390, 200, 80)
        self.moves[1].setGeometry(320, 390, 200, 80)
        self.moves[2].setGeometry(50, 490, 200, 80)
        self.moves[3].setGeometry(320, 490, 200, 80)

        self.mega = QCheckBox('Mega', self)
        self.mega.setFont(QFont("Microsoft YaHei", 10, 30))
        self.mega.move(160, 585)

        self.z_move = QCheckBox('Z-Move', self)
        self.z_move.setFont(QFont("Microsoft YaHei", 10, 30))
        self.z_move.move(340, 585)

        self.label = QLabel('Switch:', self)
        self.label.setGeometry(20, 630, 100, 50)
        self.label.setFont(QFont("Microsoft YaHei", 14, 75))

        self.pkms = [QPushButton(self) for _ in range(6)]
        for i, pkm in enumerate(self.pkms):
            pkm.setFont(QFont("Consolas", 10, 30))
            pkm.setGeometry(120 + 170 * i, 630, 150, 60)

        self.add_signal.connect(self.add_log)
        self.show()

    def add_log(self):
        self.log.setText(self.log.toPlainText() + '132')

    def send(self):
        self.add_signal.emit('111')


def hout(ui):
    while (True):
        time.sleep(1)
        pass


if __name__ == '__main__':
    app = QApplication(sys.argv)
    ui = UI()
    thread = Thread(target=hout, args=(ui,))
    # thread.start()
    sys.exit(app.exec_())
