import sys
import threading
import time
import os

from lib.functions import move_to_key

path = os.path.abspath(__file__) + '/../../resource/'
pkm_path = path + 'pkm/'

from PyQt5.QtGui import QFont, QPixmap, QPainter, QColor, QTextCursor, QCursor
from PyQt5.QtWidgets import QApplication, QWidget, QTextEdit, QLabel, QPushButton, QCheckBox
from PyQt5.QtCore import pyqtSignal, QRect, Qt

from threading import Thread

from data.moves import Moves
from game import Game
from lib.const import *


class UI(QWidget):
    add_signal = pyqtSignal(str)

    def __init__(self):
        super(UI, self).__init__()
        self.inited = False
        self.game = Game()
        self.game.set_ui(self)
        self.game.start()

        self.player = self.game.get_ui_player()
        self.player.set_ui(self)
        self.init_ui()

        self.inited = True

    def setText(self, action_required):
        state = self.game.get_state(1)
        Round = state['round']
        self.round_label.setText('Round ' + str(Round))

        my_team = state['my_team']
        my_pkms = my_team['pkms']

        foe_team = state['foe_team']
        foe_pkms = foe_team['pkms']

        masks = my_team['masks']
        switch_mask = masks['switch']
        move_mask = masks['move']
        mega_mask = masks['mega']
        z_mask = masks['z']

        def set_HP_bar(HP_bar, HP_perc):
            if HP_perc >= 1 / 2:
                color = "background-color:rgb(0,255,50,150)"
            elif HP_perc >= 1 / 4:
                color = "background-color:rgb(255,255,0,150)"
            else:
                color = "background-color:rgb(255,0,0,150)"
            HP_bar.setStyleSheet(color)
            HP_bar.setGeometry(HP_bar.x(), HP_bar.y(), HP_perc * 150, 15)

        def move_to_tip(move):
            s = ''
            s += 'Type: ' + move['type'] + '\n'
            s += 'Category: ' + move['category'] + '\n'
            if move['category'] != 'Status':
                s += 'BasePower: ' + str(move['basePower']) + '\n'
            s += 'Accuracy: ' + str(move['accuracy']) + '\n'
            if 'desc' in move:
                s += 'Desc: ' + move['desc']
            return s

        # show pivots
        pivot = my_pkms[my_team['pivot']]
        my_pivot_exist = my_team['pivot'] != -1 and pivot['alive']
        if my_pivot_exist:
            self.myPivot.setPixmap(QPixmap(pkm_path + 'back/' + pivot['name'].replace(' ', '-').lower() + '.gif'))
            self.myPivot.setToolTip(self.pkm_to_tip(pivot))
            set_HP_bar(self.myPivotHP, pivot['hp_perc'])
            self.myPivotMaxHP.setStyleSheet("background-color:rgb(255,255,255,200)")
        else:
            self.myPivot.setPixmap(QPixmap())
            self.myPivotHP.setStyleSheet("background-color:rgb(0,0,0,0)")
            self.myPivotMaxHP.setStyleSheet("background-color:rgb(0,0,0,0)")

        foe_pivot = foe_pkms[foe_team['pivot']]
        foe_pivot_exist = foe_team['pivot'] != -1 and foe_pivot['alive']
        if foe_pivot_exist:
            self.foePivot.setPixmap(QPixmap(pkm_path + foe_pivot['name'].replace(' ', '-').lower() + '.gif'))
            self.foePivot.setToolTip(self.pkm_to_tip(foe_pivot))
            set_HP_bar(self.foePivotHP, foe_pivot['hp_perc'])
            self.foePivotMaxHP.setStyleSheet("background-color:rgb(255,255,255,200)")
        else:
            self.foePivot.setPixmap(QPixmap())
            self.foePivotHP.setStyleSheet("background-color:rgb(0,0,0,0)")
            self.foePivotMaxHP.setStyleSheet("background-color:rgb(0,0,0,0)")

        # show my moves
        for i, move in enumerate(pivot['moves']):
            if action_required in [Signal.Switch,Signal.Switch_in_turn]:
                self.moves[i].setText('')
                self.moves[i].setEnabled(False)
            else:
                self.moves[i].setText(move['name'] + '\n' + str(move['pp']) + '/' + str(move['maxpp']))
                self.moves[i].setToolTip(move_to_tip(Moves[move_to_key(move['name'])]))
                self.moves[i].setEnabled(move_mask[i])

        self.z_move.setChecked(False)
        self.z_move.setEnabled(z_mask.any() and my_pivot_exist)

        self.mega.setChecked(False)
        self.mega.setEnabled(mega_mask and my_pivot_exist)

        for pkm_switch, pkm in zip(self.pkm_switch, my_pkms):
            pkm_switch.setEnabled(switch_mask and pkm['alive'])
            pkm_switch.setToolTip(self.pkm_to_tip(pkm))

        if my_pivot_exist:
            self.pkm_switch[my_team['pivot']].setEnabled(False)

        # show my mini teams
        for i, pkm in enumerate(my_pkms):
            name = pkm['name']
            self.pkm_switch[i].setText(name + '\n' + str(pkm['hp']) + '/' + str(pkm['maxhp']))
            pixmap = QPixmap(pkm_path + name.replace(' ', '-').lower() + '.gif')
            if not pkm['alive']:
                pixmap = self.get_dead_pkm(pixmap)
            self.mypkm_mini[i].setPixmap(pixmap)
            self.mypkm_mini[i].setScaledContents(True)
            self.mypkm_mini[i].setToolTip(self.pkm_to_tip(pkm))

        # show foe mini team
        for i, pkm in enumerate(foe_pkms):
            name = pkm['name']
            pixmap = QPixmap(pkm_path + name.replace(' ', '-').lower() + '.gif')
            if not pkm['alive']:
                pixmap = self.get_dead_pkm(pixmap)
            self.foepkm_mini[i].setPixmap(pixmap)
            self.foepkm_mini[i].setScaledContents(True)
            self.foepkm_mini[i].setToolTip(self.pkm_to_tip(pkm))

    def init_ui(self):
        self.setFixedSize(1130, 720)
        self.move(300, 300)
        self.setWindowTitle('Pokémon Battle Env')

        # pkm_infos
        self.my_pkm_infos = [None for _ in range(6)]
        self.foe_pkm_infos = [None for _ in range(6)]

        # field
        self.bg = QLabel(self)
        self.bg.setGeometry(0, 0, 600, 370)
        self.bg.setPixmap(QPixmap(path + 'bg.png'))
        self.bg.setScaledContents(True)

        self.log = QTextEdit(self)
        self.log.setReadOnly(True)
        self.log.setGeometry(580, 0, 550, 600)
        self.log.setFont(QFont("Consolas", 10, 30))

        self.myPivot = QLabel(self)
        self.myPivot.setGeometry(100, 130, 250, 250)

        self.myPivotMaxHP = QLabel(self)
        self.myPivotMaxHP.setGeometry(90, 180, 150, 15)
        self.myPivotMaxHP.setStyleSheet("background-color:rgb(255,255,255,0)")

        self.myPivotHP = QLabel(self)
        self.myPivotHP.setGeometry(90, 180, 150, 15)

        self.foePivot = QLabel(self)
        self.foePivot.setGeometry(370, 10, 250, 250)

        self.foePivotMaxHP = QLabel(self)
        self.foePivotMaxHP.setGeometry(350, 60, 150, 15)
        self.foePivotMaxHP.setStyleSheet("background-color:rgb(255,255,255,0)")

        self.foePivotHP = QLabel(self)
        self.foePivotHP.setGeometry(350, 60, 150, 15)

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

        self.pkm_switch = [QPushButton(self) for _ in range(6)]
        for i, pkm in enumerate(self.pkm_switch):
            pkm.setFont(QFont("Consolas", 10, 30))
            pkm.setGeometry(120 + 170 * i, 630, 150, 60)

        # connect
        self.moves[0].clicked.connect(lambda: self.send(self.gen_action_type(), 0))
        self.moves[1].clicked.connect(lambda: self.send(self.gen_action_type(), 1))
        self.moves[2].clicked.connect(lambda: self.send(self.gen_action_type(), 2))
        self.moves[3].clicked.connect(lambda: self.send(self.gen_action_type(), 3))

        self.pkm_switch[0].clicked.connect(lambda: self.send(ActionType.Switch, 0))
        self.pkm_switch[1].clicked.connect(lambda: self.send(ActionType.Switch, 1))
        self.pkm_switch[2].clicked.connect(lambda: self.send(ActionType.Switch, 2))
        self.pkm_switch[3].clicked.connect(lambda: self.send(ActionType.Switch, 3))
        self.pkm_switch[4].clicked.connect(lambda: self.send(ActionType.Switch, 4))
        self.pkm_switch[5].clicked.connect(lambda: self.send(ActionType.Switch, 5))

        self.add_signal.connect(lambda x: self.add_log(x))
        self.show()

    def pkm_to_tip(self, pkm):
        tip = ""
        tip += pkm['name'] + '\n'
        stat_lv = pkm['stat_lv']

        def lv_to_str(lv):
            if lv > 0:
                return '(+' + str(lv) + ')'
            elif lv < 0:
                return '(' + str(lv) + ')'
            else:
                return ""

        def gen_lv_str(key):
            if stat_lv[key]:
                return upper_stat[key] + ': ' + lv_to_str(stat_lv[key]) + '\n'
            else:
                return ""

        def gen_stat_str(key):
            if key in ['accuracy', 'evasion', 'ct']:
                return gen_lv_str(key)
            else:
                return upper_stat[key] + ': ' + str(pkm[key]) + lv_to_str(stat_lv[key]) + '\n'

        def gen_type_str():
            s = "Type:"
            for type in pkm['type']:
                if type:
                    s += ' ' + type + ','
                else:
                    s += ' ' + 'None' + ','
            return s[:-1] + "\n"

        def gen_move_str():
            s = ""
            for move in pkm['moves']:
                name = move['name']
                if name == 'unrevealed':
                    continue
                s += '- ' + name + ' ' + str(move['pp']) + '/' + str(move['maxpp']) + '\n'

            return s

        def gen_ability_str():
            if pkm['ability'] == 'unrevealed':
                return ""
            elif pkm['ability']:
                return 'Ability: ' + pkm['ability'] + '\n'
            else:
                return 'Ability: None\n'

        def gen_item_str():
            if pkm['item'] == 'unrevealed':
                return ""
            elif pkm['item']:
                return 'Item: ' + pkm['item'] + '\n'
            else:
                return 'Item: None\n'

        # my_pkm
        if 'hp' in pkm:
            if not pkm['alive']:
                tip += '(faint)\n'
            tip += gen_type_str()
            tip += gen_ability_str()
            tip += gen_item_str()
            tip += 'HP: ' + str(pkm['hp']) + '/' + str(pkm['maxhp']) + '\n'

            for key in pkm['stat_lv']:
                tip += gen_stat_str(key)
            tip += gen_move_str()
            if pkm['status']:
                tip += 'Status: ' + pkm['status'] + '\n'
            if pkm['vstatus']:
                tip += 'VStatus: '
                for key, turn in pkm['vstatus'].items():
                    tip += key + ','
                tip = tip[:-1] + '\n'

        else:
            if not pkm['alive']:
                tip += '(faint)\n'
            tip += gen_type_str()
            tip += gen_ability_str()
            tip += gen_item_str()
            tip += 'HP: ' + str(pkm['hp_perc'] * 100) + '%\n'
            for key in stat_lv:
                tip += gen_lv_str(key)
            tip += gen_move_str()
            if pkm['status']:
                tip += 'Status:' + pkm['status'] + '\n'
            if pkm['vstatus']:
                tip += 'VStatus: '
                for key, turn in pkm['vstatus'].items():
                    tip += key + ','
                tip = tip[:-1] + '\n'

        return tip[:-1]

    def get_dead_pkm(self, pixmap, opacity=75):
        pMap = pixmap
        temp = QPixmap(pMap.size())
        temp.fill(Qt.transparent)
        p = QPainter(temp)
        p.setCompositionMode(QPainter.CompositionMode_Source);
        p.drawPixmap(0, 0, pMap)
        p.setCompositionMode(QPainter.CompositionMode_DestinationIn)
        p.fillRect(temp.rect(), QColor(0, 0, 0, opacity))  # 根据QColor中第四个参数设置透明度，0～255
        p.end()
        pMap = temp  # 获得有透明度的图片
        return pMap

    def add_log(self, x):
        self.log.setText(self.log.toPlainText() + x + '\n')
        self.log.moveCursor(QTextCursor.End)

    def send(self, action_type, item):
        self.player.set_action(action_type, item)

    def send_log(self, log):
        self.add_signal.emit(log)

    def gen_action_type(self):
        if self.mega.isChecked():
            return ActionType.Mega
        elif self.z_move.isChecked():
            return ActionType.Z_Move
        else:
            return ActionType.Common


if __name__ == '__main__':
    app = QApplication(sys.argv)
    ui = UI()
    app.exec_()
    ui.game.force_end()
