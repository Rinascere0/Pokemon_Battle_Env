import sys
import os
import re
import copy

from PyQt5 import QtWidgets
from PyQt5.QtNetwork import QTcpSocket

from lib.functions import move_to_key, pkm_to_key
from main.login_diag import LoginDialog
from main.team_selection import TeamSelectionDialog

path = getattr(sys, '_MEIPASS',  os.path.dirname(os.path.abspath(__file__)))
if 'MEI' not in path:
    path+='/..'
path+= '/resource/'
#path = os.path.dirname(os.path.abspath(__file__)) + '/../resource/'
print('path',path)
pkm_path = path + 'pkm/'
icon_path = path + 'icon/'

from PyQt5.QtGui import QFont, QPixmap, QPainter, QColor, QTextCursor, QCursor, QMovie, QIcon, QTextCharFormat
from PyQt5.QtWidgets import QApplication, QWidget, QTextEdit, QLabel, QPushButton, QCheckBox, QComboBox, QMessageBox, QDialog
from PyQt5.QtCore import pyqtSignal, QRect, Qt, QVariantAnimation, QEasingCurve, QSize, QTimer


# Lines from log.translate(event=='round') look like "\nRound 3" → split yields "Round 3"
_BATTLE_LOG_ROUND_LINE = re.compile(r"^(\s*)(Round \d+)(\s*)$", re.IGNORECASE)

_BATTLE_LOG_HR_HTML = (
    '<hr style="border:none;border-top:1px solid rgba(255,255,255,0.14);'
    'margin:10px 0 12px 0;height:0;"/>'
)


def _ui_font_family():
    f = QFont()
    fam = f.family()
    if fam and fam.lower() not in ('ms shell dlg 2', 'fixedsys'):
        return fam
    return "Segoe UI"


def _accent_font_stack_qss():
    """Display font for round badge / switch title — slightly more character than default UI."""
    return '"Bahnschrift", "Trebuchet MS", "Candara", "Segoe UI", sans-serif'


def _accent_font_pointsize(pt):
    f = QFont("Bahnschrift", pt)
    if not f.exactMatch():
        f = QFont("Trebuchet MS", pt)
    if not f.exactMatch():
        f = QFont("Segoe UI", pt)
    return f


def _pivot_gender_symbol(gender):
    if gender == "M":
        return "\u2642"
    if gender == "F":
        return "\u2640"
    return ""


def _pivot_field_caption(pkm):
    name = pkm.get("name") or ""
    sym = _pivot_gender_symbol(pkm.get("gender"))
    lv = pkm.get("lv")
    parts = [name]
    if sym:
        parts.append(sym)
    if lv is not None and lv != "":
        parts.append(f"Lv.{lv}")
    return " ".join(parts)


def _move_btn_text_color(rgb_csv):
    r, g, b = (int(x.strip()) for x in rgb_csv.split(","))
    lum = 0.2126 * r + 0.7152 * g + 0.0722 * b
    return "#0e1118" if lum > 155 else "#f4f6fc"


def _qss_move_idle():
    ff = _ui_font_family()
    return (
        "QPushButton {"
        f"font-family: 'Cascadia Mono', 'JetBrains Mono', Consolas, monospace;"
        f"font-size: 11pt;"
        "background-color: rgba(52, 56, 72, 0.92);"
        "color: rgba(230, 233, 245, 0.28);"
        "border: 1px solid rgba(255, 255, 255, 0.09);"
        "border-radius: 12px;"
        "padding: 10px 12px;"
        "}"
        "QPushButton:disabled {"
        "background-color: rgba(44, 47, 60, 0.85);"
        "color: rgba(230, 233, 245, 0.22);"
        "border: 1px solid rgba(255, 255, 255, 0.06);"
        "}"
    )


def _qss_move_typed(rgb_csv, alpha=195):
    fg = _move_btn_text_color(rgb_csv)
    return (
        "QPushButton {"
        f"font-family: 'Cascadia Mono', 'JetBrains Mono', Consolas, monospace;"
        f"font-size: 11pt;"
        f"font-weight: 600;"
        f"background-color: rgba({rgb_csv}, {alpha});"
        f"color: {fg};"
        "border: 1px solid rgba(0, 0, 0, 0.22);"
        "border-radius: 12px;"
        "padding: 10px 12px;"
        "}"
        "QPushButton:hover:enabled {"
        "border: 1px solid rgba(255, 255, 255, 0.42);"
        "}"
        "QPushButton:disabled {"
        "background-color: rgba(44, 47, 60, 0.88);"
        "color: rgba(230, 233, 245, 0.3);"
        "border: 1px solid rgba(255, 255, 255, 0.06);"
        "}"
    )


def _qss_switch_slot(hp_rgb_csv):
    return (
        "QPushButton {"
        f"font-family: 'Cascadia Mono', 'JetBrains Mono', Consolas, monospace;"
        f"font-size: 10pt;"
        "background-color: rgba(40, 43, 56, 0.96);"
        f"color: rgb({hp_rgb_csv});"
        "border: 1px solid rgba(255, 255, 255, 0.11);"
        "border-radius: 10px;"
        "padding: 7px 10px 7px 14px;"
        "text-align: left;"
        "}"
        "QPushButton:hover:enabled {"
        "background-color: rgba(52, 56, 72, 0.98);"
        "border: 1px solid rgba(120, 160, 255, 0.35);"
        "}"
        "QPushButton:disabled {"
        "background-color: rgba(34, 36, 46, 0.92);"
        "color: rgba(180, 186, 202, 0.45);"
        "border: 1px solid rgba(255, 255, 255, 0.05);"
        "}"
    )


def _hp_track_style_active():
    return (
        "QLabel {"
        "background-color: rgba(252, 252, 255, 0.94);"
        "border: 1px solid rgba(20, 24, 40, 0.22);"
        "border-radius: 5px;"
        "}"
    )


def _hp_pct_overlay_style():
    return (
        "QLabel {"
        "background-color: transparent;"
        "color: #0d101a;"
        "font-weight: 800;"
        "border: none;"
        "}"
    )


def _field_caption_style_active():
    return (
        "QLabel#FieldPkmCaption {"
        "color: #f4f6ff;"
        f"font-family: {_accent_font_stack_qss()};"
        "font-size: 9pt;"
        "font-weight: 600;"
        "background-color: rgba(10, 12, 22, 0.58);"
        "border: 1px solid rgba(255, 255, 255, 0.12);"
        "border-radius: 5px;"
        "padding: 2px 6px;"
        "}"
    )


def _field_caption_style_hidden():
    return (
        "QLabel#FieldPkmCaption {"
        "background: transparent;"
        "border: none;"
        "color: transparent;"
        "padding: 0px;"
        "}"
    )


def _apply_field_caption_label(label, text):
    if text and str(text).strip():
        label.setStyleSheet(_field_caption_style_active())
        label.setText(str(text).strip())
    else:
        label.setStyleSheet(_field_caption_style_hidden())
        label.setText("")


def _main_window_stylesheet():
    ff = _ui_font_family()
    return f"""
    QWidget#ClientRoot {{
        background-color: #1f2230;
    }}
    QTextEdit#BattleLog {{
        background-color: #161822;
        color: #d8dce8;
        border: 1px solid rgba(255, 255, 255, 0.08);
        border-radius: 10px;
        padding: 10px;
        font-family: "Cascadia Mono", "JetBrains Mono", Consolas, monospace;
        font-size: 10pt;
        selection-background-color: #3d4f7a;
    }}
    QLabel#FieldBackdrop {{
        border-radius: 12px;
        border: 1px solid rgba(255, 255, 255, 0.1);
    }}
    QLabel#RoundBadge {{
        color: #f2f5ff;
        font-family: {_accent_font_stack_qss()};
        font-size: 16pt;
        font-weight: 600;
        font-style: italic;
        letter-spacing: 0.03em;
        background-color: rgba(0, 0, 0, 0.35);
        border: 1px solid rgba(255, 255, 255, 0.14);
        border-radius: 10px;
        padding: 8px 14px;
    }}
    QLabel#SideVignette {{
        background-color: rgba(0, 0, 0, 0.42);
        border: none;
    }}
    QLabel#SwitchTitle {{
        color: rgba(236, 240, 255, 0.88);
        font-family: {_accent_font_stack_qss()};
        font-size: 13pt;
        font-weight: 600;
        letter-spacing: 0.22em;
    }}
    QLabel#PkmThumb {{
        background-color: rgba(0, 0, 0, 0.25);
        border: 1px solid rgba(255, 255, 255, 0.12);
        border-radius: 8px;
    }}
    QPushButton#ConnectBtn {{
        font-family: "{ff}";
        font-size: 10pt;
        font-weight: 600;
        color: #f0f4ff;
        background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
            stop:0 #4a6cf0, stop:1 #3558d6);
        border: 1px solid rgba(255, 255, 255, 0.22);
        border-radius: 9px;
        padding: 6px 14px;
    }}
    QPushButton#ConnectBtn:hover {{
        background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
            stop:0 #5a7aff, stop:1 #4568e8);
        border: 1px solid rgba(255, 255, 255, 0.35);
    }}
    QPushButton#ConnectBtn:pressed {{
        background: #2f4cb8;
    }}
    QPushButton#SurrenderBtn {{
        font-family: "{ff}";
        font-size: 10pt;
        font-weight: 600;
        color: #ffd0d0;
        background-color: rgba(180, 60, 70, 0.35);
        border: 1px solid rgba(255, 120, 130, 0.45);
        border-radius: 9px;
        padding: 6px 14px;
    }}
    QPushButton#SurrenderBtn:hover {{
        background-color: rgba(200, 70, 82, 0.5);
        border: 1px solid rgba(255, 150, 160, 0.55);
    }}
    QPushButton#SurrenderBtn:pressed {{
        background-color: rgba(160, 50, 60, 0.55);
    }}
    QPushButton#SurrenderBtn:disabled {{
        color: rgba(255, 200, 200, 0.35);
        background-color: rgba(80, 45, 50, 0.35);
        border: 1px solid rgba(255, 100, 110, 0.15);
    }}
    QPushButton#RematchBtn {{
        font-family: "{ff}";
        font-size: 10pt;
        font-weight: 600;
        color: #dff7ee;
        background-color: rgba(50, 140, 110, 0.4);
        border: 1px solid rgba(120, 220, 180, 0.45);
        border-radius: 9px;
        padding: 6px 14px;
    }}
    QPushButton#RematchBtn:hover:enabled {{
        background-color: rgba(60, 160, 125, 0.52);
        border: 1px solid rgba(150, 235, 200, 0.55);
    }}
    QPushButton#RematchBtn:pressed {{
        background-color: rgba(40, 110, 88, 0.55);
    }}
    QPushButton#RematchBtn:disabled {{
        color: rgba(200, 230, 215, 0.3);
        background-color: rgba(45, 65, 58, 0.35);
        border: 1px solid rgba(100, 160, 130, 0.12);
    }}
    QPushButton#ReplayBtn {{
        font-family: "{ff}";
        font-size: 10pt;
        font-weight: 600;
        color: #e8ecff;
        background-color: rgba(90, 110, 200, 0.38);
        border: 1px solid rgba(150, 170, 255, 0.42);
        border-radius: 9px;
        padding: 6px 14px;
    }}
    QPushButton#ReplayBtn:hover:enabled {{
        background-color: rgba(105, 128, 220, 0.5);
        border: 1px solid rgba(170, 190, 255, 0.55);
    }}
    QPushButton#ReplayBtn:pressed {{
        background-color: rgba(70, 88, 170, 0.52);
    }}
    QPushButton#ReplayBtn:disabled {{
        color: rgba(210, 220, 245, 0.3);
        background-color: rgba(45, 52, 80, 0.35);
        border: 1px solid rgba(100, 120, 180, 0.15);
    }}
    QCheckBox {{
        font-family: "{ff}";
        font-size: 10pt;
        color: rgba(230, 233, 245, 0.9);
        spacing: 8px;
    }}
    QCheckBox::indicator {{
        width: 18px;
        height: 18px;
        border-radius: 5px;
        border: 1px solid rgba(255, 255, 255, 0.22);
        background-color: rgba(40, 43, 56, 0.95);
    }}
    QCheckBox::indicator:checked {{
        background-color: #4a6cf0;
        border: 1px solid rgba(255, 255, 255, 0.35);
    }}
    QCheckBox::indicator:hover {{
        border: 1px solid rgba(120, 160, 255, 0.55);
    }}
    QCheckBox::indicator:disabled {{
        background-color: rgba(34, 36, 46, 0.8);
        border: 1px solid rgba(255, 255, 255, 0.08);
    }}
    QToolTip {{
        color: #1a1c26;
        background-color: #f2f4fa;
        border: 1px solid rgba(0, 0, 0, 0.12);
        border-radius: 6px;
        padding: 6px 8px;
        font-family: "{ff}";
        font-size: 9pt;
    }}
    """

from data.moves import Moves
from lib.const import *

remote = True
if remote:
    host='115.236.153.177'
    port= 47121
else:
    host='127.0.0.1'
    port= 12345

class Client_UI(QWidget):
    add_signal = pyqtSignal(dict)
    chg_pivot_signal = pyqtSignal(bool, str)

    def on_surrender_clicked(self):
        reply = QMessageBox.question(
            self,
            'Surrender',
            'Are you sure you want to surrender? The battle will end immediately and the log will record your surrender.',
            QMessageBox.Yes | QMessageBox.No,
            QMessageBox.No,
        )
        if reply != QMessageBox.Yes:
            return
        self.client.request_surrender()

    def on_rematch_clicked(self):
        self.rematch_button.setEnabled(False)
        self.replay_button.setEnabled(False)
        team_dlg = TeamSelectionDialog(self)
        if team_dlg.exec_() != QDialog.Accepted:
            self.rematch_button.setEnabled(True)
            if self._replay_snapshots:
                self.replay_button.setEnabled(True)
            return
        choice = team_dlg.get_choice()
        if choice is None:
            self.rematch_button.setEnabled(True)
            if self._replay_snapshots:
                self.replay_button.setEnabled(True)
            return
        self.client.set_pending_team_choice(choice)
        self.client.apply_team_choice_to_player(choice)
        if self.online:
            self.client.request_rematch_online()
        else:
            self.log.clear()
            self.flush_ui()
            self.client.restart_local_battle()

    def _cancel_replay(self):
        if getattr(self, '_replay_timer', None) is not None:
            self._replay_timer.stop()
            self._replay_timer.deleteLater()
            self._replay_timer = None
        self._replay_active = False
        rb = getattr(self, 'replay_button', None)
        if rb is not None:
            rb.setText('Replay')

    def _apply_replay_playback_lock(self):
        """During replay, force-disable all battle inputs (update() re-enables them by state)."""
        self.disable_buttons()
        self.surrender_button.setEnabled(False)
        self.rematch_button.setEnabled(False)
        self.replay_button.setEnabled(True)
        self.replay_button.setText('Stop')

    def _replay_user_stop(self):
        if getattr(self, '_replay_timer', None) is not None:
            self._replay_timer.stop()
            self._replay_timer.deleteLater()
            self._replay_timer = None
        self._replay_active = False
        self.replay_button.setText('Replay')
        self._rebuild_battle_log_from_snapshots()
        self.lock_ui_game_over()

    def _reset_battle_field_state(self):
        for move in self.moves:
            move.setText('')
            move.setEnabled(False)
            move.setStyleSheet(_qss_move_idle())

        for sw in self.pkm_switch:
            sw.setText('')
            sw.setEnabled(False)
            sw.setIcon(QIcon())
            sw.setStyleSheet(_qss_switch_slot("145,153,161"))

        for mini in self.mypkm_mini:
            mini.setPixmap(QPixmap())

        for mini in self.foepkm_mini:
            mini.setPixmap(QPixmap())

        self.z_move.setEnabled(False)
        self.mega.setEnabled(False)

        self.round_label.setText('')
        self.myPivot.setMovie(QMovie(''))
        self.foePivot.setMovie(QMovie(''))

        self.myPivotMaxHP.setText('')
        self.myPivotPct.setText('')
        _apply_field_caption_label(self.myPivotCaption, "")
        self.myPivot.setToolTip('')
        self.myPivotHP.setStyleSheet("background-color:rgb(0,0,0,0)")
        self.myPivotMaxHP.setStyleSheet("background-color:rgb(0,0,0,0)")
        self.myPivotPct.setStyleSheet("background-color: transparent; border: none;")

        self.foePivot.setToolTip('')
        self.foePivotMaxHP.setText('')
        self.foePivotPct.setText('')
        _apply_field_caption_label(self.foePivotCaption, "")
        self.foePivotHP.setStyleSheet("background-color:rgb(0,0,0,0)")
        self.foePivotMaxHP.setStyleSheet("background-color:rgb(0,0,0,0)")
        self.foePivotPct.setStyleSheet("background-color: transparent; border: none;")

        self._stop_hp_anim('my')
        self._stop_hp_anim('foe')
        self._prev_my_field_key = None
        self._prev_my_field_alive = False
        self._prev_foe_field_key = None
        self._prev_foe_field_alive = False
        self._my_ko_cleared = True
        self._foe_ko_cleared = True
        self._last_my_hp_field_key = None
        self._last_foe_hp_field_key = None
        self._my_hp_display_perc = 1.0
        self._foe_hp_display_perc = 1.0

    def on_replay_clicked(self):
        if self._replay_active:
            self._replay_user_stop()
            return
        if not self._replay_snapshots:
            return
        self._begin_replay()

    def _begin_replay(self):
        self._cancel_replay()
        if not self._replay_snapshots:
            return
        self._replay_active = True
        self.replay_button.setText('Stop')
        self.replay_button.setEnabled(True)
        self.rematch_button.setEnabled(False)
        self._reset_battle_field_state()
        self._replay_index = 0
        self.log.clear()
        self._battlelog_round_lines = 0
        self._replay_step()

    def _rebuild_battle_log_from_snapshots(self):
        self.log.clear()
        self._battlelog_round_lines = 0
        for snap in self._replay_snapshots:
            line = snap.get('log')
            if line:
                self._append_battle_log_line(line)
        self.log.moveCursor(QTextCursor.End)

    def _replay_step(self):
        if self._replay_index >= len(self._replay_snapshots):
            self._replay_finish()
            return
        snap = self._replay_snapshots[self._replay_index]
        self._replay_index += 1
        line = snap.get('log')
        if line:
            self._append_battle_log_line(line)
            self.log.moveCursor(QTextCursor.End)
        self.update(snap['state'], snap['action_required'])
        if self._replay_index < len(self._replay_snapshots):
            self._replay_timer = QTimer(self)
            self._replay_timer.setSingleShot(True)
            self._replay_timer.timeout.connect(self._replay_step)
            self._replay_timer.start(450)
        else:
            self._replay_finish()

    def _replay_finish(self):
        self._replay_active = False
        if getattr(self, '_replay_timer', None) is not None:
            self._replay_timer.stop()
            self._replay_timer.deleteLater()
            self._replay_timer = None
        self.replay_button.setText('Replay')
        self.lock_ui_game_over()

    def toggle_connection(self):
        if self.client.socket.state() != QTcpSocket.ConnectedState:
            dialog = LoginDialog(self)
            if dialog.exec_():
                username, password = dialog.get_user_info()
                if not username:
                    QMessageBox.warning(self, "警告", "用户名不能为空!")
                    return
            else:
                return
            team_dlg = TeamSelectionDialog(self)
            if team_dlg.exec_() != QDialog.Accepted:
                return
            choice = team_dlg.get_choice()
            if choice is None:
                return
            self.client.set_pending_team_choice(choice)
            self.client.connect_to_server(host, port, username, password)
            self.connect_button.setText("Disconnect")
        else:
            self.client.disconnect_from_server()
            self.connect_button.setText("Connect")


    def disable_buttons(self):
        for move in self.moves:
            move.setEnabled(False)

        for sw in self.pkm_switch:
            sw.setEnabled(False)

        self.z_move.setEnabled(False)
        self.mega.setEnabled(False)

    def lock_ui_game_over(self):
        """Disable all battle actions including Surrender (normal win, loss, or surrender)."""
        self.disable_buttons()
        self.surrender_button.setEnabled(False)
        self.rematch_button.setEnabled(True)
        self.replay_button.setEnabled(bool(self._replay_snapshots))

    def flush_ui(self):
        self._cancel_replay()
        self._replay_snapshots.clear()
        self._reset_battle_field_state()
        self.surrender_button.setEnabled(True)
        self.rematch_button.setEnabled(False)
        self.replay_button.setEnabled(False)

    def onDisconnect(self):
        self.flush_ui()
        self.connect_button.setText("Connect")

    def onConnect(self):
        self.flush_ui()

    def _shutdown_battle_environment(self):
        if getattr(self, '_shutdown_battle_environment_done', False):
            return
        self._shutdown_battle_environment_done = True
        c = self.client
        if c is None:
            return
        try:
            if c.socket.state() == QTcpSocket.ConnectedState:
                c.disconnect_from_server()
            g = c.game
            if g is not None:
                g.shutdown_and_join()
        except Exception:
            pass

    def closeEvent(self, event):
        self._shutdown_battle_environment()
        super().closeEvent(event)

    def change_movie(self, back, name):
        mv_name = name.replace(' ', '-').lower() + '.gif'
        if back:
            movie = self.myPivot.movie()
            file_name = pkm_path + 'back/' + mv_name
        else:
            movie = self.foePivot.movie()
            file_name = pkm_path + mv_name

        if file_name.split('/')[-1] != movie.fileName().split('/')[-1]:
            movie.setFileName(file_name)
            movie.stop()
            movie.start()

    def update_messages(self, message):
        if message[0] == '~':
            self.add_log(message[1:])
        else:
            # game message
            msg_grp = message.split('^')
            print('groups',len(msg_grp))
            if len(msg_grp) == 1:
                self.msg_buf += msg_grp[0]
            else:
                msg = self.msg_buf + msg_grp[0]
                self.add_log(eval(msg))
                for msg in msg_grp[1:-1]:
                    self.add_log(eval(msg))
                self.msg_buf = msg_grp[-1]
                # TO DELETE
                #  self.msg_buf += msg['val']
                #  if msg['end'] == 0:
                #       return
                #   msg= self.msg_buf
                #  self.msg_buf = ''

    def update_status(self, status):
        """更新状态显示"""
        self.log.append(f"[Status] {status}")

    def setBold(self,button,en):
        font = button.font()
        font.setBold(en)
        button.setFont(font)

    def __init__(self, client, uid=1, online=False):
        super(Client_UI, self).__init__()
        self.uid = uid
        self.online = online

        self.z_mask = [False for _ in range(4)]
        self.move_mask = [False for _ in range(4)]

        self.msg_buf = ''

        self._replay_snapshots = []
        self._replay_active = False
        self._replay_index = 0
        self._replay_timer = None

        self.action_required = False
        self.client = client
        self.client.set_ui(self)
        self.client.signals.new_message.connect(self.update_messages)
        self.client.signals.status_updated.connect(self.update_status)

        self.init_ui()

        if not self.online:
            while True:
                team_dlg = TeamSelectionDialog(self)
                if team_dlg.exec_() != QDialog.Accepted:
                    QMessageBox.information(self, '队伍', '请选择队伍后再进行对战（取消将重新打开本窗口）')
                    continue
                choice = team_dlg.get_choice()
                if choice is None:
                    continue
                self.client.apply_team_choice_to_player(choice)
                break

    def init_ui(self):
        self.setObjectName("ClientRoot")
        self.setFixedSize(1130, 720)
        self.move(300, 300)
        self.setWindowTitle('Pokémon Battle Env')
        self.setWindowIcon(QIcon(path+'avatar.png'))
        self.setStyleSheet(_main_window_stylesheet())

        self.connect_button = QPushButton(self)
        self.connect_button.setObjectName("ConnectBtn")
        self.connect_button.setText('Connect')
        self.connect_button.clicked.connect(self.toggle_connection)
        self.connect_button.setGeometry(10, 388, 100, 34)
        self.connect_button.setVisible(self.online)

        self.surrender_button = QPushButton(self)
        self.surrender_button.setObjectName("SurrenderBtn")
        self.surrender_button.setText('Forfeit')
        self.surrender_button.setGeometry(10, 430, 100, 34)
        self.surrender_button.clicked.connect(self.on_surrender_clicked)

        self.rematch_button = QPushButton(self)
        self.rematch_button.setObjectName("RematchBtn")
        self.rematch_button.setText('Rematch')
        self.rematch_button.setGeometry(10, 472, 100, 34)
        self.rematch_button.setEnabled(False)
        self.rematch_button.clicked.connect(self.on_rematch_clicked)

        self.replay_button = QPushButton(self)
        self.replay_button.setObjectName("ReplayBtn")
        self.replay_button.setText('Replay')
        self.replay_button.setGeometry(10, 514, 100, 34)
        self.replay_button.setEnabled(False)
        self.replay_button.clicked.connect(self.on_replay_clicked)

        # pkm_infos
        self.my_pkm_infos = [None for _ in range(6)]
        self.foe_pkm_infos = [None for _ in range(6)]

        # field
        self.bg = QLabel(self)
        self.bg.setObjectName("FieldBackdrop")
        self.bg.setGeometry(0, 0, 600, 370)
        self.bg.setPixmap(QPixmap(path + 'bg.png'))
        self.bg.setScaledContents(True)

        self.log = QTextEdit(self)
        self.log.setObjectName("BattleLog")
        self.log.setReadOnly(True)
        self.log.setGeometry(612, 12, 506, 576)
        self.log.setFont(QFont("Cascadia Mono", 10))
        if not self.log.font().exactMatch():
            self.log.setFont(QFont("Consolas", 10))
        self.log.setAcceptRichText(True)
        self._battlelog_round_lines = 0

        self.myPivot = QLabel(self)
        self.myPivot.setGeometry(100, 130, 250, 250)
        self.myPivot.setMovie(QMovie())

        self.myPivotCaption = QLabel(self)
        self.myPivotCaption.setObjectName("FieldPkmCaption")
        self.myPivotCaption.setGeometry(90, 160, 150, 18)
        self.myPivotCaption.setAlignment(Qt.AlignLeft | Qt.AlignVCenter)
        self.myPivotCaption.setFont(_accent_font_pointsize(9))
        _apply_field_caption_label(self.myPivotCaption, "")

        self.myPivotMaxHP = QLabel(self)
        self.myPivotMaxHP.setGeometry(90, 180, 150, 16)
        self.myPivotMaxHP.setFrameShape(QtWidgets.QFrame.NoFrame)
        self.myPivotMaxHP.setStyleSheet(
            "background-color: transparent; border: none; border-radius: 5px;")

        self.myPivotHP = QLabel(self)
        self.myPivotHP.setGeometry(90, 180, 150, 15)

        self.myPivotPct = QLabel(self)
        self.myPivotPct.setGeometry(90, 180, 150, 16)
        self.myPivotPct.setFont(QFont(_ui_font_family(), 8, QFont.Black))
        self.myPivotPct.setAlignment(Qt.AlignCenter)
        self.myPivotPct.setStyleSheet(_hp_pct_overlay_style())
        self.myPivotPct.setAttribute(Qt.WA_TransparentForMouseEvents)

        self.foePivot = QLabel(self)
        self.foePivot.setGeometry(370, 10, 250, 250)
        self.foePivot.setMovie(QMovie())

        self.foePivotCaption = QLabel(self)
        self.foePivotCaption.setObjectName("FieldPkmCaption")
        self.foePivotCaption.setGeometry(350, 40, 150, 18)
        self.foePivotCaption.setAlignment(Qt.AlignLeft | Qt.AlignVCenter)
        self.foePivotCaption.setFont(_accent_font_pointsize(9))
        _apply_field_caption_label(self.foePivotCaption, "")

        self.foePivotMaxHP = QLabel(self)
        self.foePivotMaxHP.setGeometry(350, 60, 150, 16)
        self.foePivotMaxHP.setFrameShape(QtWidgets.QFrame.NoFrame)
        self.foePivotMaxHP.setStyleSheet(
            "background-color: transparent; border: none; border-radius: 5px;")

        self.foePivotHP = QLabel(self)
        self.foePivotHP.setGeometry(350, 60, 150, 15)

        self.foePivotPct = QLabel(self)
        self.foePivotPct.setGeometry(350, 60, 150, 16)
        self.foePivotPct.setFont(QFont(_ui_font_family(), 8, QFont.Black))
        self.foePivotPct.setAlignment(Qt.AlignCenter)
        self.foePivotPct.setStyleSheet(_hp_pct_overlay_style())
        self.foePivotPct.setAttribute(Qt.WA_TransparentForMouseEvents)

        # round info
        self.round_label = QLabel(self)
        self.round_label.setObjectName("RoundBadge")
        self.round_label.setGeometry(72, 12, 200, 48)
        self.round_label.setAlignment(Qt.AlignCenter)

        self.left_margin = QLabel(self)
        self.left_margin.setObjectName("SideVignette")
        self.left_margin.setGeometry(0, 0, 60, 370)

        self.right_margin = QLabel(self)
        self.right_margin.setObjectName("SideVignette")
        self.right_margin.setGeometry(520, 0, 60, 370)

        self.mypkm_mini = [QLabel(self) for _ in range(6)]
        for i, label in enumerate(self.mypkm_mini):
            label.setObjectName("PkmThumb")
            label.setGeometry(10, 60 + 50 * i, 45, 45)

        self.foepkm_mini = [QLabel(self) for _ in range(6)]
        for i, label in enumerate(self.foepkm_mini):
            label.setObjectName("PkmThumb")
            label.setGeometry(530, 50 * i, 45, 45)

        # move button
        self.moves = [QPushButton(self) for _ in range(4)]
        for move in self.moves:
            move.setStyleSheet(_qss_move_idle())

        _move_x0 = 124
        _move_x1 = 392
        self.moves[0].setGeometry(_move_x0, 388, 208, 84)
        self.moves[1].setGeometry(_move_x1, 388, 208, 84)
        self.moves[2].setGeometry(_move_x0, 486, 208, 84)
        self.moves[3].setGeometry(_move_x1, 486, 208, 84)

        self.mega = QCheckBox('Mega', self)
        self.mega.move(238, 586)

        self.z_move = QCheckBox('Z-Move', self)
        self.z_move.move(378, 586)
        self.z_move.clicked.connect(self.set_zable_move)

        self.label = QLabel('SWITCH', self)
        self.label.setObjectName("SwitchTitle")
        self.label.setGeometry(18, 636, 96, 44)

        self.pkm_switch = [QPushButton(self) for _ in range(6)]
        for i, pkm in enumerate(self.pkm_switch):
            pkm.setGeometry(108 + 168 * i, 632, 156, 62)
            pkm.setIconSize(QSize(38, 38))

        # connect
        self.moves[0].clicked.connect(lambda: self.send_action(self.gen_action_type(), 0))
        self.moves[1].clicked.connect(lambda: self.send_action(self.gen_action_type(), 1))
        self.moves[2].clicked.connect(lambda: self.send_action(self.gen_action_type(), 2))
        self.moves[3].clicked.connect(lambda: self.send_action(self.gen_action_type(), 3))

        self.pkm_switch[0].clicked.connect(lambda: self.send_action(ActionType.Switch, 0))
        self.pkm_switch[1].clicked.connect(lambda: self.send_action(ActionType.Switch, 1))
        self.pkm_switch[2].clicked.connect(lambda: self.send_action(ActionType.Switch, 2))
        self.pkm_switch[3].clicked.connect(lambda: self.send_action(ActionType.Switch, 3))
        self.pkm_switch[4].clicked.connect(lambda: self.send_action(ActionType.Switch, 4))
        self.pkm_switch[5].clicked.connect(lambda: self.send_action(ActionType.Switch, 5))

        self.add_signal.connect(lambda x: self.add_log(x))
        self.chg_pivot_signal.connect(lambda x, y: self.change_movie(x, y))

        self._hp_anim_my = None
        self._hp_anim_foe = None
        self._prev_my_field_key = None
        self._prev_my_field_alive = False
        self._prev_foe_field_key = None
        self._prev_foe_field_alive = False
        self._my_ko_cleared = True
        self._foe_ko_cleared = True
        self._last_my_hp_field_key = None
        self._last_foe_hp_field_key = None
        self._my_hp_display_perc = 1.0
        self._foe_hp_display_perc = 1.0

        self.disable_buttons()
        self.show()

    def _hp_zone_rgb(self, hp_perc):
        if hp_perc >= 0.5:
            return 0, 255, 50
        if hp_perc >= 0.25:
            return 255, 255, 0
        return 255, 0, 0

    def _hp_apply_bar(self, side, max_HP_bar, HP_bar, hp_perc, r, g, b, update_pct_label=True):
        w = max(0.0, min(1.0, hp_perc)) * 150
        HP_bar.setStyleSheet(
            f"background-color:rgba({r},{g},{b},220); border-radius: 4px;"
            "border: 1px solid rgba(0,0,0,0.12);"
        )
        HP_bar.setGeometry(HP_bar.x(), HP_bar.y(), int(round(w)), 15)
        if not update_pct_label:
            return
        pct = self.myPivotPct if side == "my" else self.foePivotPct
        if hp_perc > 0:
            pct.setText(str(round(hp_perc * 100, 2)) + "%")
            pct.setStyleSheet(_hp_pct_overlay_style())
            pct.raise_()
        else:
            pct.setText("")

    def _stop_hp_anim(self, side, flush_label_pair=None):
        """Stops running HP animation. If flush_label_pair (max_bar, hp_bar) is given,
        syncs display perc from the animation's current frame and updates the % label —
        so each interrupted tween still gets a label 'finish' before the next one."""
        disp_attr = '_my_hp_display_perc' if side == 'my' else '_foe_hp_display_perc'
        anim_attr = '_hp_anim_my' if side == 'my' else '_hp_anim_foe'
        anim = getattr(self, anim_attr)
        if anim is not None:
            cv = anim.currentValue()
            if cv is not None:
                try:
                    setattr(self, disp_attr, max(0.0, min(1.0, float(cv))))
                except (TypeError, ValueError):
                    pass
            anim.stop()
            anim.deleteLater()
            setattr(self, anim_attr, None)
        if flush_label_pair is not None:
            max_hp_bar, hp_bar, side = flush_label_pair
            p = max(0.0, min(1.0, float(getattr(self, disp_attr))))
            r, g, b = self._hp_zone_rgb(p)
            self._hp_apply_bar(side, max_hp_bar, hp_bar, p, r, g, b, update_pct_label=True)

    def _finish_my_ko_hp_anim(self):
        self._stop_hp_anim('my')
        self._my_hp_display_perc = 0.0
        self.chg_pivot_signal.emit(True, 'none')
        self.myPivotMaxHP.setText('')
        self.myPivotPct.setText('')
        _apply_field_caption_label(self.myPivotCaption, "")
        self.myPivot.setToolTip('')
        self.myPivotHP.setStyleSheet("background-color:rgb(0,0,0,0)")
        self.myPivotMaxHP.setStyleSheet("background-color:rgb(0,0,0,0)")
        self.myPivotPct.setStyleSheet("background-color: transparent; border: none;")
        self._my_ko_cleared = True

    def _finish_foe_ko_hp_anim(self):
        self._stop_hp_anim('foe')
        self._foe_hp_display_perc = 0.0
        self.chg_pivot_signal.emit(False, 'none')
        self.foePivot.setToolTip('')
        self.foePivotMaxHP.setText('')
        self.foePivotPct.setText('')
        _apply_field_caption_label(self.foePivotCaption, "")
        self.foePivotHP.setStyleSheet("background-color:rgb(0,0,0,0)")
        self.foePivotMaxHP.setStyleSheet("background-color:rgb(0,0,0,0)")
        self.foePivotPct.setStyleSheet("background-color: transparent; border: none;")
        self._foe_ko_cleared = True

    def _update_pivot_hp_bar(self, side, max_HP_bar, HP_bar, target_perc, identity_changed,
                              zero_finish_callback=None):
        disp_attr = '_my_hp_display_perc' if side == 'my' else '_foe_hp_display_perc'
        target_perc = max(0.0, min(1.0, float(target_perc)))

        if identity_changed:
            self._stop_hp_anim(side)
            setattr(self, disp_attr, target_perc)
            r, g, b = self._hp_zone_rgb(target_perc)
            self._hp_apply_bar(side, max_HP_bar, HP_bar, target_perc, r, g, b, update_pct_label=True)
            return

        self._stop_hp_anim(side, (max_HP_bar, HP_bar, side))
        start_perc = getattr(self, disp_attr)
        if abs(start_perc - target_perc) < 1e-6:
            if zero_finish_callback is not None and target_perc <= 1e-9:
                zero_finish_callback()
            return

        r0, g0, b0 = self._hp_zone_rgb(start_perc)
        r1, g1, b1 = self._hp_zone_rgb(target_perc)
        span = target_perc - start_perc
        if abs(span) < 1e-9:
            setattr(self, disp_attr, target_perc)
            self._hp_apply_bar(side, max_HP_bar, HP_bar, target_perc, r1, g1, b1, update_pct_label=True)
            if zero_finish_callback is not None and target_perc <= 1e-9:
                zero_finish_callback()
            return

        anim_attr = '_hp_anim_my' if side == 'my' else '_hp_anim_foe'
        anim = QVariantAnimation(self)
        anim.setDuration(350)
        anim.setEasingCurve(QEasingCurve.OutCubic)
        anim.setStartValue(start_perc)
        anim.setEndValue(target_perc)

        def on_value(v):
            p = float(v)
            t = (p - start_perc) / span
            t = max(0.0, min(1.0, t))
            r = int(round(r0 + (r1 - r0) * t))
            g = int(round(g0 + (g1 - g0) * t))
            b = int(round(b0 + (b1 - b0) * t))
            self._hp_apply_bar(side, max_HP_bar, HP_bar, p, r, g, b, update_pct_label=False)
            setattr(self, disp_attr, p)

        def on_finished():
            setattr(self, anim_attr, None)
            setattr(self, disp_attr, target_perc)
            r, g, b = self._hp_zone_rgb(target_perc)
            self._hp_apply_bar(side, max_HP_bar, HP_bar, target_perc, r, g, b, update_pct_label=True)
            if zero_finish_callback is not None and target_perc <= 1e-9:
                zero_finish_callback()
            anim.deleteLater()

        anim.valueChanged.connect(on_value)
        anim.finished.connect(on_finished)
        anim.start()
        setattr(self, anim_attr, anim)

    def set_zable_move(self):
        if self.z_move.isChecked():
            for i, move in enumerate(self.moves):
                move.setEnabled(self.z_mask[i] & self.move_mask[i])
        else:
            for i, move in enumerate(self.moves):
                move.setEnabled(self.move_mask[i])

    def update(self, state, action_required=None):
        if action_required:
            self.action_required = action_required
        else:
            action_required = self.action_required

        Round = state['round']
        self.round_label.setText('Round ' + str(Round))

        def env_to_tip(env):
            env_tip = ""
            weather = env['weather']
            if weather['name']:
                env_tip += WeatherNames[weather['name']] + ' (' + str(weather['remain']) + ')\n'

            terrain = env['terrain']
            if terrain['name']:
                env_tip += WeatherNames[terrain['name']] + ' (' + str(terrain['remain']) + ')\n'

            pd_weathers = env['pseudo_weather']
            for pd_weather, round in pd_weathers.items():
                if round:
                    pd_name = WeatherNames[pd_weather] if pd_weather in WeatherNames else pd_weather
                    env_tip += pd_weather + ' (' + str(round) + ')\n'

            return env_tip[:-1]

        self.round_label.setToolTip(env_to_tip(state['env']))

        my_team = state['my_team']
        my_pkms = my_team['pkms']

        foe_team = state['foe_team']
        foe_pkms = foe_team['pkms']

        masks = my_team['masks']
        switch_mask = masks['switch']
        move_mask = masks['move']
        mega_mask = masks['mega']
        z_mask = masks['z']

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
        my_idx = my_team['pivot']
        my_field_key = (my_idx, pivot['name']) if my_idx != -1 else None
        my_alive_ok = bool(my_field_key and pivot['alive'])
        if my_field_key != self._prev_my_field_key:
            self._my_ko_cleared = False
        my_faint_edge = (
            my_field_key
            and not my_alive_ok
            and self._prev_my_field_alive
            and self._prev_my_field_key == my_field_key
        )
        anim_my_running = self._hp_anim_my is not None
        show_my_pivot = bool(
            my_field_key
            and (
                my_alive_ok
                or (not self._my_ko_cleared and (my_faint_edge or anim_my_running))
            )
        )
        my_hp_identity_changed = my_field_key != self._last_my_hp_field_key

        if show_my_pivot:
            if my_alive_ok:
                self.z_mask = z_mask
                self.move_mask = move_mask
            else:
                self.z_mask = [False for _ in range(4)]
                self.move_mask = [False for _ in range(4)]

            if pivot['vstatus']['substitute']:
                self.chg_pivot_signal.emit(True, 'substitute')
            else:
                self.chg_pivot_signal.emit(True, pivot['name'])

            self.myPivot.setToolTip(self.pkm_to_tip(pivot))
            _apply_field_caption_label(self.myPivotCaption, _pivot_field_caption(pivot))
            self.myPivotMaxHP.setStyleSheet(_hp_track_style_active())

            if my_alive_ok:
                self._update_pivot_hp_bar(
                    'my', self.myPivotMaxHP, self.myPivotHP, pivot['hp_perc'], my_hp_identity_changed
                )
            elif my_faint_edge:
                if self._my_hp_display_perc <= 1e-6:
                    self._finish_my_ko_hp_anim()
                else:
                    self._update_pivot_hp_bar(
                        'my', self.myPivotMaxHP, self.myPivotHP, 0.0, False,
                        zero_finish_callback=self._finish_my_ko_hp_anim,
                    )
        else:
            self._stop_hp_anim('my')
            self.z_mask = [False for _ in range(4)]
            self.chg_pivot_signal.emit(True, 'none')
            self.myPivotMaxHP.setText('')
            self.myPivotPct.setText('')
            _apply_field_caption_label(self.myPivotCaption, "")
            self.myPivot.setToolTip('')
            self.myPivotHP.setStyleSheet("background-color:rgb(0,0,0,0)")
            self.myPivotMaxHP.setStyleSheet("background-color:rgb(0,0,0,0)")
            self.myPivotPct.setStyleSheet("background-color: transparent; border: none;")

        self._last_my_hp_field_key = my_field_key
        self._prev_my_field_key = my_field_key
        self._prev_my_field_alive = my_alive_ok

        foe_pivot = foe_pkms[foe_team['pivot']]
        foe_idx = foe_team['pivot']
        foe_field_key = (foe_idx, foe_pivot['name']) if foe_idx != -1 else None
        foe_alive_ok = bool(foe_field_key and foe_pivot['alive'])
        if foe_field_key != self._prev_foe_field_key:
            self._foe_ko_cleared = False
        foe_faint_edge = (
            foe_field_key
            and not foe_alive_ok
            and self._prev_foe_field_alive
            and self._prev_foe_field_key == foe_field_key
        )
        anim_foe_running = self._hp_anim_foe is not None
        show_foe_pivot = bool(
            foe_field_key
            and (
                foe_alive_ok
                or (not self._foe_ko_cleared and (foe_faint_edge or anim_foe_running))
            )
        )
        foe_hp_identity_changed = foe_field_key != self._last_foe_hp_field_key

        if show_foe_pivot:
            if foe_pivot['vstatus']['substitute']:
                self.chg_pivot_signal.emit(False, 'substitute')
            else:
                self.chg_pivot_signal.emit(False, foe_pivot['name'])
            self.foePivot.setToolTip(self.pkm_to_tip(foe_pivot))
            _apply_field_caption_label(self.foePivotCaption, _pivot_field_caption(foe_pivot))
            self.foePivotMaxHP.setStyleSheet(_hp_track_style_active())

            if foe_alive_ok:
                self._update_pivot_hp_bar(
                    'foe', self.foePivotMaxHP, self.foePivotHP, foe_pivot['hp_perc'], foe_hp_identity_changed
                )
            elif foe_faint_edge:
                if self._foe_hp_display_perc <= 1e-6:
                    self._finish_foe_ko_hp_anim()
                else:
                    self._update_pivot_hp_bar(
                        'foe', self.foePivotMaxHP, self.foePivotHP, 0.0, False,
                        zero_finish_callback=self._finish_foe_ko_hp_anim,
                    )
        else:
            self._stop_hp_anim('foe')
            self.chg_pivot_signal.emit(False, 'none')
            self.foePivot.setToolTip('')
            self.foePivotMaxHP.setText('')
            self.foePivotPct.setText('')
            _apply_field_caption_label(self.foePivotCaption, "")
            self.foePivotHP.setStyleSheet("background-color:rgb(0,0,0,0)")
            self.foePivotMaxHP.setStyleSheet("background-color:rgb(0,0,0,0)")
            self.foePivotPct.setStyleSheet("background-color: transparent; border: none;")

        self._last_foe_hp_field_key = foe_field_key
        self._prev_foe_field_key = foe_field_key
        self._prev_foe_field_alive = foe_alive_ok

        game_over = state.get('loser') is not None

        my_pivot_alive = my_alive_ok
        foe_pivot_alive = foe_alive_ok

        # show my moves
        for i, move in enumerate(pivot['moves']):
            self.setBold(self.moves[i],False)
            if game_over or action_required in [Signal.Switch, Signal.Switch_in_turn] or not foe_pivot_alive:
                self.moves[i].setText('')
                self.moves[i].setEnabled(False)
                self.moves[i].setStyleSheet(_qss_move_idle())
            else:
                move_info = Moves[move_to_key(move['name'])]
                attr_key = move_info['type'].lower()
                self.moves[i].setText(move['name'] + '\n' + str(move['pp']) + '/' + str(move['maxpp']))
                self.moves[i].setToolTip(move_to_tip(move_info))
                self.moves[i].setStyleSheet(_qss_move_typed(Color[attr_key]))
                if action_required is not None:
                    self.moves[i].setEnabled(move_mask[i])

        self.z_move.setChecked(False)
        self.z_move.setEnabled(not game_over and any(z_mask) and my_pivot_alive)

        self.mega.setChecked(False)
        self.mega.setEnabled(not game_over and mega_mask and my_pivot_alive)

        for pkm_switch, pkm in zip(self.pkm_switch, my_pkms):
            pkm_switch.setEnabled(
                not game_over and (action_required is not None and (
                        switch_mask or action_required in [Signal.Switch, Signal.Switch_in_turn]) and pkm['alive']))
            pkm_switch.setToolTip(self.pkm_to_tip(pkm))
            hp_perc = pkm['hp'] / pkm['maxhp'] if 'hp' in pkm else pkm['hp_perc']

            if hp_perc > 0.5:
                hp_color = '83,121,28'  # green
            elif hp_perc > 0.25:
                hp_color = '164,161,31'  # yellow
            elif hp_perc > 0:
                hp_color = '255,0,0'
            else:
                hp_color = '145,153,161'
            pkm_switch.setStyleSheet(_qss_switch_slot(hp_color))
            pkm_switch.setIcon(QIcon(icon_path + pkm_to_key(pkm['name']) + '.png'))

        if my_pivot_alive and not game_over:
            self.pkm_switch[my_team['pivot']].setEnabled(False)

        if game_over:
            if not self._replay_active:
                self.lock_ui_game_over()
        else:
            if not self._replay_active:
                self.rematch_button.setEnabled(False)
                self.replay_button.setEnabled(False)

        # show my mini teams
        for i, pkm in enumerate(my_pkms):
            name = pkm['name']
            self.setBold(self.pkm_switch[i], False)
            self.pkm_switch[i].setText(name[:10] + '\n' + str(pkm['hp']) + '/' + str(pkm['maxhp']))
            pixmap = QPixmap(pkm_path + name.replace(' ', '-').lower() + '.gif')
            if not pkm['alive']:
                pixmap = self.get_faint_pkm_mini(pixmap)
            self.mypkm_mini[i].setPixmap(pixmap)
            self.mypkm_mini[i].setScaledContents(True)
            self.mypkm_mini[i].setToolTip(self.pkm_to_tip(pkm))

        # show foe mini team
        for i, pkm in enumerate(foe_pkms):
            name = pkm['name']
            pixmap = QPixmap(pkm_path + name.replace(' ', '-').lower() + '.gif')
            if not pkm['alive']:
                pixmap = self.get_faint_pkm_mini(pixmap)
            self.foepkm_mini[i].setPixmap(pixmap)
            self.foepkm_mini[i].setScaledContents(True)
            self.foepkm_mini[i].setToolTip(self.pkm_to_tip(pkm))

        if self._replay_active:
            self._apply_replay_playback_lock()

    # generate pkm info to display as tip
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

            vstatus = ""
            for key, turn in pkm['vstatus'].items():
                if turn:
                    vstatus += key + ','
            if vstatus:
                tip += 'VStatus: ' + vstatus[:-1] + '\n'


        else:
            if not pkm['alive']:
                tip += '(faint)\n'
            tip += gen_type_str()
            tip += gen_ability_str()
            tip += gen_item_str()
            tip += 'HP: ' + str(round(pkm['hp_perc'] * 100, 2)) + '%\n'
            for key in stat_lv:
                tip += gen_lv_str(key)
            tip += gen_move_str()
            if pkm['status']:
                tip += 'Status:' + pkm['status'] + '\n'
            vstatus = ""
            for key, turn in pkm['vstatus'].items():
                if turn:
                    vstatus += key + ','
            if vstatus:
                tip += 'VStatus: ' + vstatus[:-1] + '\n'

        return tip[:-1]

    # return the pixmap of faint pkm 
    def get_faint_pkm_mini(self, pixmap, opacity=75):
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

    # called by Log class, send log to gui display
    def send_log(self, msg):
        self.add_signal.emit(msg)

    def _append_battle_log_line(self, log):
        m = _BATTLE_LOG_ROUND_LINE.match(log)
        if not m:
            self.log.append(log)
            return
        n = int(m.group(2).split()[1])
        cursor = self.log.textCursor()
        cursor.movePosition(QTextCursor.End)
        plain_fmt = QTextCharFormat()
        divider_fmt = QTextCharFormat()
        divider_fmt.setForeground(QColor(80, 84, 102))
        bold_fmt = QTextCharFormat()
        bold_fmt.setFontWeight(QFont.Bold)
        if log.startswith('\n'):
            cursor.insertText('\n', plain_fmt)
        cursor.insertText('\n', plain_fmt)
        cursor.insertText('\u2500' * 56 + '\n', divider_fmt)
        cursor.insertText(f'Round {n}', bold_fmt)
        self.log.setTextCursor(cursor)

    # add log to gui textbox
    def add_log(self, msg):
        # differs msg and log
        if type(msg) is dict:
            with open('log.txt','a') as f:
                f.write(msg['log']+'\n')
            state, log, action_required = msg['state'],msg['log'], msg['action_required']
            self._replay_snapshots.append(copy.deepcopy({
                'state': state,
                'action_required': action_required,
                'log': log,
            }))
            self._append_battle_log_line(log)

            self.log.moveCursor(QTextCursor.End)
            self.update(state,action_required)
        else:
            self.log.append(f'Server: {msg}')
            self.log.moveCursor(QTextCursor.End)

    # generate action_type by mega and z check_box
    def gen_action_type(self):
        if self.mega.isChecked():
            return ActionType.Mega
        elif self.z_move.isChecked():
            return ActionType.Z_Move
        else:
            return ActionType.Common

    # send action to Client
    def send_action(self, action_type, item):
        if action_type==ActionType.Switch:
            self.setBold(self.pkm_switch[item],True)
        elif action_type in [ActionType.Common,ActionType.Z_Move]:
            self.setBold(self.moves[item],True)
        self.disable_buttons()
        self.action_required = None
        print('action',action_type,item)
        self.client.send_action(action_type, item)


def run():
    app = QApplication(sys.argv)


if __name__ == '__main__':
    run()
