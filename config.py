# -*- coding: utf-8 -*-
import os
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent
RESOURCES_DIR = BASE_DIR / "resources"

ICON_PATH = str(RESOURCES_DIR / "icon.ico")
LOGO_PATH = str(RESOURCES_DIR / "logo.png")
PLACEHOLDER_IMAGE = str(RESOURCES_DIR / "picture.png")

DB_CONFIG = {
    "dbname": "podcasts_db",
    "user": "postgres",
    "password": "123",
    "host": "127.0.0.1",
    "port": 5432,
}

ROLE_NAMES = {
    1: "Администратор",
    2: "Менеджер",
    3: "Покупатель",
    None: "Гость",
}

DISCOUNT_LIMIT = 15
DISCOUNT_COLOR = "#2E8B57"

WINDOW_TITLES = {
    0: "Мир подкастов — Каталог",
    1: "Мир подкастов — Карточка подкаста",
    2: "Мир подкастов — Заказы",
}
