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


def validate_login(raw):
    login = raw.strip()
    if not login:
        return None, "Введите логин (пробелы не считаются)"
    if len(login) < 3:
        return None, "Логин должен содержать минимум 3 символа"
    return login, None


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

    def check_login(self):
        # Проверка длины и пустого поля через validate_login
        login, error = validate_login(self.login_input.text())
        if error:
            QMessageBox.critical(self, "Ошибка", error)
            return

        # Получаем курсор (поддерживает оба варианта названия подключения в Database)
        conn = getattr(self.db, "conn", None) or getattr(self.db, "connection", None)
        cursor = conn.cursor() if conn else self.db.cursor

        cursor.execute(
            "SELECT user_id, role_id, last_name, first_name, middle_name "
            "FROM users WHERE login = %s", (login,)
        )
        result = cursor.fetchone()
        if conn:
            cursor.close()

        # Error для неверного логина
        if not result:
            QMessageBox.critical(self, "Ошибка", "Пользователь не найден")
            return

        user_id, role_id, last_name, first_name, middle_name = result
        full_name = " ".join(
            part for part in (last_name, first_name, middle_name) if part
        )

        self.user_id = user_id
        self.role_id = role_id
        self.full_name = full_name

        # Information для успешного входа
        QMessageBox.information(self, "Информация", f"Добро пожаловать, {full_name}!")

        self.accept()
        from main import MainWindow
        self.main_window = MainWindow(
            user_id=user_id,
            role_id=role_id,
            full_name=full_name
        )
        self.main_window.show()

    def login_as_guest(self):
        self.accept()
        from main import MainWindow
        self.main_window = MainWindow(user_id=None, role_id=None, full_name="Гость")
        self.main_window.show()
