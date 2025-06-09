import sys
from PyQt5.QtWidgets import (QApplication, QMainWindow, QPushButton, QDialog,
                             QLabel, QLineEdit, QVBoxLayout, QHBoxLayout,
                             QMessageBox, QWidget)
from PyQt5.QtCore import Qt

class LoginDialog(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("用户登录")
        self.setMinimumWidth(300)

        # 创建用户名和密码输入框
        self.username_label = QLabel("用户名:")
        self.username_edit = QLineEdit()

        self.password_label = QLabel("密码:")
        self.password_edit = QLineEdit()
        self.password_edit.setEchoMode(QLineEdit.Password)  # 密码以圆点显示

        # 创建按钮
        self.ok_button = QPushButton("确定")
        self.cancel_button = QPushButton("取消")

        # 设置布局
        main_layout = QVBoxLayout()

        # 添加用户名和密码输入框
        user_layout = QHBoxLayout()
        user_layout.addWidget(self.username_label)
        user_layout.addWidget(self.username_edit)
        main_layout.addLayout(user_layout)

        pwd_layout = QHBoxLayout()
        pwd_layout.addWidget(self.password_label)
        pwd_layout.addWidget(self.password_edit)
        main_layout.addLayout(pwd_layout)

        # 添加按钮
        button_layout = QHBoxLayout()
        button_layout.addStretch()
        button_layout.addWidget(self.ok_button)
        button_layout.addWidget(self.cancel_button)
        main_layout.addLayout(button_layout)

        self.setLayout(main_layout)

        # 连接信号和槽
        self.ok_button.clicked.connect(self.accept)
        self.cancel_button.clicked.connect(self.reject)

    def get_user_info(self):
        """获取用户输入的用户名和密码"""
        return self.username_edit.text(), self.password_edit.text()
