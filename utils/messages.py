# -*- coding: utf-8 -*-
from PySide6.QtWidgets import QMessageBox


def validate_login(raw):
    login = raw.strip()
    if not login:
        return None, "Введите логин (пробелы не считаются)"
    if len(login) < 3:
        return None, "Логин должен содержать минимум 3 символа"
    return login, None


def show_error(parent, message, title="Ошибка"):
    QMessageBox.critical(parent, title, message)


def show_info(parent, message, title="Информация"):
    QMessageBox.information(parent, title, message)


def show_warning_confirm(parent, message, title="Предупреждение"):
    reply = QMessageBox.warning(
        parent,
        title,
        message,
        QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
    )
    return reply == QMessageBox.StandardButton.Yes
