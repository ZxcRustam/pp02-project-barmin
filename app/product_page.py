# -*- coding: utf-8 -*-
from PySide6.QtWidgets import QLabel, QVBoxLayout, QWidget
from styles import PAGE_TITLE_STYLE


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
