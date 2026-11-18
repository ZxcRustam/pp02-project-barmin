# -*- coding: utf-8 -*-
from PySide6.QtWidgets import QLabel, QVBoxLayout, QWidget
from styles import PAGE_TITLE_STYLE


class OrdersPage(QWidget):
    def __init__(self, orders_repo=None):
        super().__init__()
        self.orders_repo = orders_repo
        self._setup_ui()

    def _setup_ui(self):
        orders_layout = QVBoxLayout(self)
        orders_layout.setContentsMargins(15, 15, 15, 15)
        lbl_ord = QLabel("Список заказов")
        lbl_ord.setStyleSheet(PAGE_TITLE_STYLE)
        orders_layout.addWidget(lbl_ord)
        orders_layout.addStretch()
