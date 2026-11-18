# -*- coding: utf-8 -*-
from config import DISCOUNT_COLOR

APP_STYLE = """
    QMainWindow {
        background-color: #FFFFFF;
        font-family: Calibri;
    }
"""

LOGIN_WINDOW_STYLE = """
    QWidget {
        background-color: #FAFAFA;
        font-family: Calibri;
    }
"""

LOGIN_LABEL_STYLE = "font-size: 13px; color: #2C3E50;"

LOGIN_INPUT_STYLE = """
    QLineEdit {
        font-size: 13px;
        padding: 6px;
        border: 1px solid #B0BEC5;
        border-radius: 4px;
        background-color: #FFFFFF;
        color: #000000;
    }
"""

LOGIN_BUTTON_STYLE = """
    QPushButton {
        background-color: #70B2AF;
        color: #FFFFFF;
        font-family: Calibri;
        font-size: 13px;
        font-weight: bold;
        border: 1px solid #5B9A97;
        border-radius: 4px;
        padding: 8px;
    }
    QPushButton:hover {
        background-color: #5B9A97;
    }
"""

GUEST_BUTTON_STYLE = """
    QPushButton {
        background-color: #90A4AE;
        color: #FFFFFF;
        font-family: Calibri;
        font-size: 13px;
        font-weight: bold;
        border: 1px solid #78909C;
        border-radius: 4px;
        padding: 8px;
    }
    QPushButton:hover {
        background-color: #78909C;
    }
"""

BUTTON_STYLE = """
    QPushButton {
        background-color: #70B2AF;
        color: white;
        font-family: Calibri;
        font-size: 13px;
        font-weight: bold;
        border: 1px solid #5B9A97;
        border-radius: 4px;
        padding: 6px 14px;
        min-height: 20px;
    }
    QPushButton:hover {
        background-color: #5B9A97;
    }
"""

COMBO_STYLE = """
    QComboBox, QLineEdit {
        font-family: Calibri;
        font-size: 13px;
        padding: 4px;
        border: 1px solid #B0BEC5;
        border-radius: 4px;
        background-color: #FFFFFF;
        min-width: 140px;
    }
"""

HEADER_STYLE = "background-color: #D2F6E7;"
HEADER_LOGO_FALLBACK_STYLE = "font-weight: bold; font-size: 18px; color: #00796B;"
HEADER_USER_STYLE = "font-weight: bold; font-size: 14px; color: #2C3E50; background: transparent;"

SCROLL_AREA_STYLE = "QScrollArea { border: none; background-color: #FFFFFF; }"
SCROLL_CONTENT_STYLE = "background-color: #FFFFFF;"

PAGE_TITLE_STYLE = "font-size: 16px; font-weight: bold;"

CARD_TITLE_STYLE = "font-weight: bold; font-size: 14px; color: #1A237E;"
CARD_OLD_PRICE_STYLE = "color: red;"

CARD_LOW_STOCK_STYLE = """
    QWidget { border: 1px solid #B0BEC5; border-radius: 8px; background-color: #ff8080; padding: 5px; }
    QLabel { border: none; background: transparent; color: #000000; }
"""
CARD_LOW_STOCK_PRICE_STYLE = "font-size: 16px; font-weight: bold; color: #1A237E;"

CARD_DISCOUNT_STYLE = """
    QWidget { border: 1px solid #CFD8DC; border-radius: 8px; background-color: #FFFFFF; padding: 5px; }
    QLabel { border: none; background: transparent; }
"""
CARD_DISCOUNT_PRICE_STYLE = f"color: {DISCOUNT_COLOR}; font-weight: bold; font-size: 16px;"

CARD_DEFAULT_STYLE = """
    QWidget { border: 1px solid #CFD8DC; border-radius: 8px; background-color: #FAFAFA; padding: 5px; }
    QLabel { border: none; background: transparent; }
"""
CARD_DEFAULT_PRICE_STYLE = "font-size: 16px; font-weight: bold; color: #2E7D32;"
