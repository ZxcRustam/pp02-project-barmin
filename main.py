# -*- coding: utf-8 -*-
import sys
from pathlib import Path

# Добавляем корень проекта в sys.path для корректных импортов
sys.path.insert(0, str(Path(__file__).resolve().parent))

from PySide6.QtWidgets import QApplication
from app.login_window import LoginWindow


def main():
    app = QApplication(sys.argv)
    auth_window = LoginWindow()
    auth_window.show()
    sys.exit(app.exec())


if __name__ == "__main__":
    main()
