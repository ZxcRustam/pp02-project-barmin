# -*- coding: utf-8 -*-
import psycopg2
from PySide6.QtWidgets import (
    QComboBox, QDialog, QHBoxLayout, QLabel,
    QMessageBox, QPushButton, QSpinBox, QVBoxLayout, QWidget
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

        # Получаем объект Database из родителя (CatalogPage или MainWindow)
        self.db = getattr(parent, "db", None)
        if self.db is None and parent is not None:
            repo = getattr(parent, "products_repo", None)
            self.db = getattr(repo, "db", None)


        self.setWindowTitle("Карточка товара")
        self.resize(420, 480)
        self.setStyleSheet("QDialog { background-color: #FFFFFF; font-family: Calibri; }")
        self.setup_ui()
        self.load_product(product_id)

    def setup_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(20, 20, 20, 20)
        layout.setSpacing(10)

        # Изображение товара
        self.image_label = QLabel()
        self.image_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(self.image_label)

        # Наименование
        self.name_label = QLabel(f"Товар ID {self.product_id}")
        self.name_label.setWordWrap(True)
        self.name_label.setStyleSheet("font-size: 17px; font-weight: bold; color: #1A237E;")
        self.name_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(self.name_label)

        # Цена и остаток
        self.price_label = QLabel("Цена: 0.00 ₽")
        self.price_label.setStyleSheet("font-size: 16px; font-weight: bold; color: #2E7D32;")
        self.price_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(self.price_label)

        # Описание
        self.description_label = QLabel("")
        self.description_label.setWordWrap(True)
        self.description_label.setStyleSheet("font-size: 13px; color: #546E7A;")
        self.description_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(self.description_label)

        # Выбор варианта
        variant_label = QLabel("Выберите вариант:")
        variant_label.setStyleSheet("font-size: 13px; font-weight: bold; color: #2C3E50;")
        layout.addWidget(variant_label)

        self.variant_combo = QComboBox()
        self.variant_combo.setStyleSheet(COMBO_STYLE)
        self.variant_combo.addItems(["Выпуск 1", "Выпуск 2", "Выпуск 3"])
        layout.addWidget(self.variant_combo)

        # Выбор количества (QSpinBox)
        qty_layout = QHBoxLayout()
        qty_label = QLabel("Количество:")
        qty_label.setStyleSheet("font-size: 13px; font-weight: bold; color: #2C3E50;")
        qty_layout.addWidget(qty_label)

        self.quantity_spin = QSpinBox()
        self.quantity_spin.setMinimum(1)
        self.quantity_spin.setStyleSheet("padding: 4px; font-size: 13px;")
        qty_layout.addWidget(self.quantity_spin)
        qty_layout.addStretch()
        layout.addLayout(qty_layout)

        layout.addStretch()

        # Кнопки
        buttons_layout = QHBoxLayout()
        self.add_button = QPushButton("Добавить в корзину")
        self.add_button.setStyleSheet(BUTTON_STYLE)
        self.add_button.clicked.connect(self.add_selected_to_cart)
        buttons_layout.addWidget(self.add_button)

        close_btn = QPushButton("Закрыть")
        close_btn.setStyleSheet(BUTTON_STYLE)
        close_btn.clicked.connect(self.accept)
        buttons_layout.addWidget(close_btn)

        layout.addLayout(buttons_layout)

    def load_product(self, product_id):
        if self.db is None:
            QMessageBox.critical(self, "Ошибка", "Нет подключения к базе данных")
            return

        conn = self.db.get_connection()
        if conn is None:
            QMessageBox.critical(self, "Ошибка", "Не удалось получить соединение с БД")
            return

        try:
            cursor = conn.cursor()
            cursor.execute("""
                SELECT p.name, p.price, p.description, p.image_path,
                       COALESCE(SUM(si.quantity), 0) AS total_quantity
                FROM products p
                LEFT JOIN stock_items si ON p.product_id = si.product_id
                WHERE p.product_id = %s
                GROUP BY p.product_id
            """, (product_id,))
            product = cursor.fetchone()
            cursor.close()

            if product is None:
                QMessageBox.critical(self, "Ошибка", "Товар не найден")
                return

            name, price, description, image_path, total_quantity = product

            self.name_label.setText(str(name))
            self.price_label.setText(f"Цена: {float(price):.2f} ₽ (Остаток: {int(total_quantity)})")
            self.description_label.setText(str(description) if description else "Описание отсутствует")

            # Если image_path пустой -> load_cover(None) вернет picture.png
            pixmap = load_cover(image_path if image_path else None)
            if not pixmap.isNull():
                pixmap = pixmap.scaled(
                    150, 150,
                    Qt.AspectRatioMode.KeepAspectRatio,
                    Qt.TransformationMode.SmoothTransformation
                )
            self.image_label.setPixmap(pixmap)

            # Настройка максимума QSpinBox и блокировка кнопки при нулевом остатке
            qty = int(total_quantity)
            if qty <= 0:
                self.quantity_spin.setMinimum(0)
                self.quantity_spin.setMaximum(0)
                self.add_button.setEnabled(False)
                self.add_button.setText("Нет в наличии")
            else:
                self.quantity_spin.setMinimum(1)
                self.quantity_spin.setMaximum(qty)

        except psycopg2.Error as e:
            QMessageBox.critical(self, "Ошибка БД", f"Ошибка загрузки товара: {e}")
        finally:
            self.db.release_connection(conn)

    def add_selected_to_cart(self):
        QMessageBox.information(self, "Информация", "Корзина будет подключена в РТ 19")
