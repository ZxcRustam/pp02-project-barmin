# -*- coding: utf-8 -*-
from PySide6.QtCore import Qt
from PySide6.QtGui import QFont
from PySide6.QtWidgets import (
    QComboBox,
    QHBoxLayout,
    QLabel,
    QLineEdit,
    QPushButton,
    QScrollArea,
    QVBoxLayout,
    QWidget,
)

from config import DISCOUNT_LIMIT
from styles import (
    BUTTON_STYLE,
    CARD_DEFAULT_PRICE_STYLE,
    CARD_DEFAULT_STYLE,
    CARD_DISCOUNT_PRICE_STYLE,
    CARD_DISCOUNT_STYLE,
    CARD_LOW_STOCK_PRICE_STYLE,
    CARD_LOW_STOCK_STYLE,
    CARD_OLD_PRICE_STYLE,
    CARD_TITLE_STYLE,
    COMBO_STYLE,
    SCROLL_AREA_STYLE,
    SCROLL_CONTENT_STYLE,
)
from utils.discount import calculate_discount, calculate_price
from utils.image_loader import load_cover


def create_card(product, products_repo=None):
    (product_id, name, category_id, studio, old_price_raw, image_path, total_quantity) = product

    card = QWidget()
    card_layout = QHBoxLayout()

    image_label = QLabel()
    cover_pixmap = load_cover(image_path)
    image_label.setPixmap(
        cover_pixmap.scaled(
            70,
            70,
            Qt.AspectRatioMode.KeepAspectRatio,
            Qt.TransformationMode.SmoothTransformation,
        )
    )
    image_label.setFixedSize(70, 70)
    card_layout.addWidget(image_label)

    text_layout = QVBoxLayout()
    title_label = QLabel(f"{studio} | {name}")
    title_label.setStyleSheet(CARD_TITLE_STYLE)
    text_layout.addWidget(title_label)
    text_layout.addWidget(QLabel(f"Категория: {category_id}"))
    text_layout.addWidget(QLabel(f"Доступно для покупки: {int(total_quantity)} лицензий"))
    card_layout.addLayout(text_layout)

    old_price = float(old_price_raw)
    computed_price = calculate_price(product_id, old_price, products_repo=products_repo)
    new_price = float(computed_price) if computed_price is not None else old_price
    discount = calculate_discount(old_price, new_price)

    price_container = QVBoxLayout()
    price_label = QLabel(f"{new_price:.2f} ₽")
    price_label.setAlignment(Qt.AlignmentFlag.AlignRight | Qt.AlignmentFlag.AlignVCenter)

    old_price_label = QLabel(f"<s>{old_price:.2f} ₽</s>")
    old_price_label.setFont(QFont("Calibri", 10))
    old_price_label.setStyleSheet(CARD_OLD_PRICE_STYLE)
    old_price_label.setAlignment(Qt.AlignmentFlag.AlignRight)
    price_container.addWidget(old_price_label)

    price_container.addWidget(price_label)
    card_layout.addLayout(price_container)

    card.setLayout(card_layout)
    old_price_label.setVisible(discount > 0)

    if total_quantity <= 3:
        card.setStyleSheet(CARD_LOW_STOCK_STYLE)
        price_label.setStyleSheet(CARD_LOW_STOCK_PRICE_STYLE)
    elif discount > DISCOUNT_LIMIT:
        card.setStyleSheet(CARD_DISCOUNT_STYLE)
        price_label.setStyleSheet(CARD_DISCOUNT_PRICE_STYLE)
    else:
        card.setStyleSheet(CARD_DEFAULT_STYLE)
        price_label.setStyleSheet(CARD_DEFAULT_PRICE_STYLE)

    return card


class CatalogPage(QWidget):
    def __init__(
        self,
        products_repo,
        on_open_product=None,
        on_open_orders=None,
        on_open_admin=None,
        on_buy_click=None,
    ):
        super().__init__()
        self.products_repo = products_repo
        self.on_open_product = on_open_product
        self.on_open_orders = on_open_orders
        self.on_open_admin = on_open_admin
        self.on_buy_click = on_buy_click

        self._setup_ui()

    def _setup_ui(self):
        catalog_layout = QVBoxLayout(self)
        catalog_layout.setContentsMargins(0, 0, 0, 0)
        catalog_layout.setSpacing(10)

        top_widget = QWidget()
        top_widget.setStyleSheet(COMBO_STYLE)
        top_layout = QVBoxLayout(top_widget)
        top_layout.setContentsMargins(15, 5, 15, 5)
        top_layout.setSpacing(5)

        filter_row = QHBoxLayout()
        self.search_input = QLineEdit()
        self.search_input.setPlaceholderText("Поиск по названию или студии...")
        self.search_input.textChanged.connect(self.load_products)
        filter_row.addWidget(self.search_input)

        self.filter_combo = QComboBox()
        self.filter_combo.addItem("Все категории")
        for cat in self.products_repo.get_categories():
            self.filter_combo.addItem(str(cat))
        self.filter_combo.currentIndexChanged.connect(self.load_products)
        filter_row.addWidget(self.filter_combo)

        self.sort_combo = QComboBox()
        self.sort_combo.addItems(["По возрастанию цены", "По убыванию цены"])
        self.sort_combo.currentIndexChanged.connect(self.load_products)
        filter_row.addWidget(self.sort_combo)
        top_layout.addLayout(filter_row)

        buttons_row = QHBoxLayout()
        self.order_button = QPushButton("Купить подкаст")
        self.manager_button = QPushButton("Заказы (менеджер)")
        self.admin_button = QPushButton("Админ-панель")

        self.order_button.setStyleSheet(BUTTON_STYLE)
        self.manager_button.setStyleSheet(BUTTON_STYLE)
        self.admin_button.setStyleSheet(BUTTON_STYLE)

        if self.on_open_product:
            self.order_button.clicked.connect(self.on_open_product)
        if self.on_buy_click:
            self.order_button.clicked.connect(self.on_buy_click)
        if self.on_open_orders:
            self.manager_button.clicked.connect(self.on_open_orders)
        if self.on_open_admin:
            self.admin_button.clicked.connect(self.on_open_admin)

        buttons_row.addWidget(self.order_button)
        buttons_row.addWidget(self.manager_button)
        buttons_row.addWidget(self.admin_button)
        buttons_row.addStretch()
        top_layout.addLayout(buttons_row)

        catalog_layout.addWidget(top_widget)

        self.scroll_area = QScrollArea()
        self.scroll_area.setWidgetResizable(True)
        self.scroll_area.setStyleSheet(SCROLL_AREA_STYLE)

        self.scroll_content = QWidget()
        self.scroll_content.setStyleSheet(SCROLL_CONTENT_STYLE)
        self.products_layout = QVBoxLayout(self.scroll_content)
        self.products_layout.setContentsMargins(15, 10, 15, 10)
        self.products_layout.setSpacing(10)
        self.products_layout.addStretch()

        self.scroll_area.setWidget(self.scroll_content)
        catalog_layout.addWidget(self.scroll_area)

    def apply_role_visibility(self, role_id):
        if role_id == 1:
            self.order_button.hide()
            self.manager_button.show()
            self.admin_button.show()
        elif role_id == 2:
            self.order_button.hide()
            self.manager_button.show()
            self.admin_button.hide()
        elif role_id == 3:
            self.order_button.show()
            self.manager_button.hide()
            self.admin_button.hide()
        else:
            self.order_button.hide()
            self.manager_button.hide()
            self.admin_button.hide()

    def load_products(self):
        while self.products_layout.count() > 1:
            item = self.products_layout.takeAt(0)
            if item is not None:
                current_widget = item.widget()
                if current_widget is not None:
                    current_widget.deleteLater()

        search_text = self.search_input.text()
        category_text = self.filter_combo.currentText()

        products = self.products_repo.get_products(
            search=search_text,
            category_text=category_text,
            order="ASC",
        )

        processed_products = []
        for prod in products:
            product_id, name, category_id, studio, old_price_raw, image_path, total_quantity = prod
            old_price = float(old_price_raw)
            computed_price = calculate_price(product_id, old_price, products_repo=self.products_repo)
            new_price = float(computed_price) if computed_price is not None else old_price
            processed_products.append((new_price, prod))

        is_ascending = self.sort_combo.currentIndex() == 0
        processed_products.sort(key=lambda x: x[0], reverse=not is_ascending)

        for _, prod in processed_products:
            card = create_card(prod, products_repo=self.products_repo)
            self.products_layout.insertWidget(self.products_layout.count() - 1, card)
