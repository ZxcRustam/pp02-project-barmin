# -*- coding: utf-8 -*-
import os
from PySide6.QtGui import QIcon
from PySide6.QtWidgets import QLabel, QLineEdit, QPushButton, QVBoxLayout, QWidget

from app.main_window import MainWindow
from config import ICON_PATH
from db.connection import Database
from db.users_repo import UsersRepo
from styles import (
    GUEST_BUTTON_STYLE,
    LOGIN_BUTTON_STYLE,
    LOGIN_INPUT_STYLE,
    LOGIN_LABEL_STYLE,
    LOGIN_WINDOW_STYLE,
)
from utils.messages import show_error, show_info, validate_login


class LoginWindow(QWidget):
    def __init__(self, db=None):
        super().__init__()
        self.db = db if db is not None else Database()
        self.users_repo = UsersRepo(self.db)

        self.setWindowTitle("Авторизация")
        self.resize(300, 200)
        if os.path.exists(ICON_PATH):
            self.setWindowIcon(QIcon(ICON_PATH))
        self.setStyleSheet(LOGIN_WINDOW_STYLE)

        self._setup_ui()

    def _setup_ui(self):
        layout = QVBoxLayout(self)
        layout.setSpacing(10)
        layout.setContentsMargins(20, 20, 20, 20)

        label = QLabel("Введите ваш логин:")
        label.setStyleSheet(LOGIN_LABEL_STYLE)
        layout.addWidget(label)

        self.login_input = QLineEdit()
        self.login_input.setPlaceholderText("Например: admin, manager1, client01")
        self.login_input.setStyleSheet(LOGIN_INPUT_STYLE)
        layout.addWidget(self.login_input)

        self.login_button = QPushButton("Войти")
        self.login_button.setStyleSheet(LOGIN_BUTTON_STYLE)
        self.login_button.clicked.connect(self.handle_login)
        layout.addWidget(self.login_button)

        self.guest_button = QPushButton("Войти как Гость")
        self.guest_button.setStyleSheet(GUEST_BUTTON_STYLE)
        self.guest_button.clicked.connect(self.handle_guest)
        layout.addWidget(self.guest_button)

    def handle_login(self):
        login_text, error = validate_login(self.login_input.text())
        if error:
            show_error(self, error)
            return

        user_info = self.users_repo.get_user_by_login(login_text)

        if user_info:
            u_id, r_id, l_name, f_name, m_name = user_info
            full_name_str = " ".join(p for p in (l_name, f_name, m_name) if p)

            show_info(self, f"Добро пожаловать, {full_name_str}!")

            self.main_window = MainWindow(
                role_id=r_id,
                full_name=full_name_str,
                user_id=u_id,
                db=self.db,
            )
            self.main_window.show()
            self.close()
        else:
            show_error(self, "Пользователь не найден")

    def handle_guest(self):
        self.main_window = MainWindow(
            role_id=None,
            full_name=None,
            user_id=None,
            db=self.db,
        )
        self.main_window.show()
        self.close()
