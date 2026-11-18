# -*- coding: utf-8 -*-
from PySide6.QtWidgets import (
    QComboBox, QDialog, QHBoxLayout, QLabel,
    QMessageBox, QPushButton, QVBoxLayout, QWidget
)
from PySide6.QtCore import Qt
from styles import BUTTON_STYLE, COMBO_STYLE, PAGE_TITLE_STYLE
from utils.image_loader import load_cover


class ProductPage(QWidget):
    def __init__(self, orders_repo=None):
        super().__init__()
        self.orders_repo = orders_repo
        self._setup_ui()

    def _setup_ui(self):
        product_layout = QVBoxLayout(self)
        product_layout.setContentsMargins(15, 15, 15, 15)
        lbl_prod = QLabel("Карточка подкаста")
        lbl_prod.setStyleSheet(PAGE_TITLE_STYLE)
        product_layout.addWidget(lbl_prod)
        product_layout.addStretch()


class ProductCard(QDialog):
    def __init__(self, product_id, parent=None):
        super().__init__(parent)
        self.product_id = product_id
        self.db = getattr(parent, "db", None)

        self.setWindowTitle("Карточка товара")
        self.resize(400, 420)
        self.setStyleSheet("QDialog { background-color: #FFFFFF; font-family: Calibri; }")
        self.setup_ui()

    def setup_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(20, 20, 20, 20)
        layout.setSpacing(12)

        # Задание 2.1: QLabel для изображения (заглушка picture.png 150x150)
        self.image_label = QLabel()
        pixmap = load_cover(None)
        if not pixmap.isNull():
            pixmap = pixmap.scaled(
                150, 150,
                Qt.AspectRatioMode.KeepAspectRatio,
                Qt.TransformationMode.SmoothTransformation
            )
        self.image_label.setPixmap(pixmap)
        self.image_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(self.image_label)

        # Задание 2.1: QLabel для наименования товара
        self.name_label = QLabel(f"Товар ID {self.product_id}")
        self.name_label.setStyleSheet("font-size: 16px; font-weight: bold; color: #1A237E;")
        self.name_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(self.name_label)

        # Описание / этап разработки
        self.desc_label = QLabel("Описание подкаста (данные из БД добавляются в РТ 17)")
        self.desc_label.setWordWrap(True)
        self.desc_label.setStyleSheet("font-size: 13px; color: #546E7A;")
        self.desc_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(self.desc_label)

        # Задание 3.1: QComboBox для выбора варианта (список из БД заполняется в РТ 17)
        variant_label = QLabel("Выберите вариант:")
        variant_label.setStyleSheet("font-size: 13px; font-weight: bold; color: #2C3E50;")
        layout.addWidget(variant_label)

        self.variant_combo = QComboBox()
        self.variant_combo.setStyleSheet(COMBO_STYLE)
        self.variant_combo.addItems(["Выпуск 1", "Выпуск 2", "Выпуск 3"])
        layout.addWidget(self.variant_combo)

        layout.addStretch()

        # Кнопки «Добавить» и «Закрыть»
        buttons_layout = QHBoxLayout()
        self.add_button = QPushButton("Добавить")
        self.add_button.setStyleSheet(BUTTON_STYLE)
        self.add_button.clicked.connect(self.add_selected_to_cart)
        buttons_layout.addWidget(self.add_button)

        close_btn = QPushButton("Закрыть")
        close_btn.setStyleSheet(BUTTON_STYLE)
        close_btn.clicked.connect(self.accept)
        buttons_layout.addWidget(close_btn)

        layout.addLayout(buttons_layout)

    def add_selected_to_cart(self):
        # Временный обработчик до реализации корзины в РТ 19
        QMessageBox.information(self, "Информация", "Корзина будет подключена в РТ 19")
