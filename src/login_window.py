from PySide6.QtWidgets import (QDialog, QLineEdit, QPushButton,
                               QVBoxLayout, QLabel, QMessageBox)

# Фирменный стиль для кнопок
BUTTON_STYLE = """
    QPushButton {
        background-color: #70B2AF;
        color: white;
        font-family: Calibri;
        font-size: 13px;
        font-weight: bold;
        border: none;
        border-radius: 4px;
        padding: 6px 12px;
    }
    QPushButton:hover {
        background-color: #5B9A97;
    }
"""


class LoginWindow(QDialog):
    def __init__(self, db):
        super().__init__()
        self.db = db
        self.user_id = None
        self.role_id = None
        self.full_name = None

        self.setWindowTitle("Авторизация")
        self.resize(300, 220)
        self.setup_ui()

    # ЗАДАНИЯ 2.1 и 3.1: Поле ввода логина и кнопка «Войти»
    def setup_ui(self):
        self.setStyleSheet("""
            QDialog {
                background-color: #FFFFFF;
                font-family: Calibri;
            }
            QLabel {
                color: #333333;
            }
            QLineEdit {
                border: 1px solid #B0BEC5;
                border-radius: 4px;
                padding: 4px;
            }
        """)

        layout = QVBoxLayout()
        layout.addWidget(QLabel("Логин:"))

        self.login_input = QLineEdit()
        self.login_input.setPlaceholderText("Введите логин")
        layout.addWidget(self.login_input)

        self.login_button = QPushButton("Войти")
        self.login_button.setStyleSheet(BUTTON_STYLE)
        self.login_button.clicked.connect(self.check_login)
        layout.addWidget(self.login_button)

        self.guest_button = QPushButton("Войти как гость")
        self.guest_button.setStyleSheet(BUTTON_STYLE)
        self.guest_button.clicked.connect(self.login_as_guest)
        layout.addWidget(self.guest_button)

        self.setLayout(layout)

    # ЗАДАНИЯ 4.1 и 5.1: Проверка логина в БД и передача user_id, role_id
    def check_login(self):
        login = self.login_input.text().strip()

        if not login:
            QMessageBox.warning(self, "Ошибка", "Введите логин")
            return

        user = self.db.get_user_by_login(login)

        if user:
            user_id, role_id = user[0], user[1]
            self.user_id = user_id
            self.role_id = role_id
            self.full_name = " ".join(p for p in user[2:5] if p)

            self.accept()
            from main import MainWindow
            self.main_window = MainWindow(
                role_id=role_id,
                full_name=self.full_name,
                user_id=user_id
            )
            self.main_window.show()
        else:
            QMessageBox.warning(self, "Ошибка", "Пользователь не найден")

    def login_as_guest(self):
        self.accept()
        from main import MainWindow
        self.main_window = MainWindow(role_id=None, full_name="Гость", user_id=None)
        self.main_window.show()
