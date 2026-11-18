# -*- coding: utf-8 -*-
import os
from typing import Any
from PySide6.QtCore import Qt
from PySide6.QtGui import QIcon, QPixmap
from PySide6.QtWidgets import (
    QHBoxLayout,
    QLabel,
    QMainWindow,
    QPushButton,
    QStackedWidget,
    QVBoxLayout,
    QWidget,
)

from app.catalog_page import CatalogPage
from app.orders_page import OrdersPage
from app.product_page import ProductPage
from config import ICON_PATH, LOGO_PATH, ROLE_NAMES, WINDOW_TITLES
from db.connection import Database
from db.orders_repo import OrdersRepo
from db.products_repo import ProductsRepo
from styles import (
    APP_STYLE,
    BUTTON_STYLE,
    HEADER_LOGO_FALLBACK_STYLE,
    HEADER_STYLE,
    HEADER_USER_STYLE,
)
from utils.messages import show_error, show_info, show_warning_confirm


class MainWindow(QMainWindow):
    def __init__(self, role_id=None, full_name=None, user_id=None, db=None):
        super().__init__()
        self.role_id = role_id
        self.full_name = full_name
        self.user_id = user_id if user_id else 4

        self.db = db if db is not None else Database()
        self.products_repo = ProductsRepo(self.db)
        self.orders_repo = OrdersRepo(self.db)

        self.setWindowTitle(WINDOW_TITLES[0])
        self.resize(850, 650)

        if os.path.exists(ICON_PATH):
            self.setWindowIcon(QIcon(ICON_PATH))

        self.setStyleSheet(APP_STYLE)

        self.setup_ui()
        self.setup_role_interface()
        self.load_products()

    def setup_ui(self):
        central = QWidget()
        self.setCentralWidget(central)
        main_layout = QVBoxLayout(central)
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.setSpacing(10)

        header_widget = QWidget()
        header_widget.setStyleSheet(HEADER_STYLE)
        header_layout = QHBoxLayout(header_widget)
        header_layout.setContentsMargins(15, 10, 15, 10)

        logo_label = QLabel()
        logo_pixmap = QPixmap(LOGO_PATH)
        if not logo_pixmap.isNull():
            logo_label.setPixmap(
                logo_pixmap.scaledToHeight(60, Qt.TransformationMode.SmoothTransformation)
            )
        else:
            logo_label.setText("🎙️ МИР ПОДКАСТОВ")
            logo_label.setStyleSheet(HEADER_LOGO_FALLBACK_STYLE)
        header_layout.addWidget(logo_label)
        header_layout.addStretch()

        text = f"ФИО: {self.full_name} ({ROLE_NAMES.get(self.role_id)})" if self.full_name else "Гость"
        self.name_label = QLabel(text)
        self.name_label.setStyleSheet(HEADER_USER_STYLE)
        header_layout.addWidget(self.name_label)

        self.logout_button = QPushButton("Выход")
        self.logout_button.setStyleSheet(BUTTON_STYLE)
        self.logout_button.clicked.connect(self.handle_logout_click)
        header_layout.addWidget(self.logout_button)
        main_layout.addWidget(header_widget)

        self.stacked_widget = QStackedWidget()
        self.catalog_page = CatalogPage(
            products_repo=self.products_repo,
            on_open_product=lambda: self.switch_page(1),
            on_open_orders=self.handle_manager_click,
            on_open_admin=self.show_admin_panel,
            on_buy_click=self.buy_podcast_mock,
        )
        self.product_page = ProductPage(orders_repo=self.orders_repo)
        self.orders_page = OrdersPage(orders_repo=self.orders_repo)

        self.stacked_widget.addWidget(self.catalog_page)
        self.stacked_widget.addWidget(self.product_page)
        self.stacked_widget.addWidget(self.orders_page)
        self.stacked_widget.setCurrentIndex(0)
        main_layout.addWidget(self.stacked_widget)

        bottom_layout = QHBoxLayout()
        bottom_layout.setContentsMargins(15, 5, 15, 10)

        self.back_button = QPushButton("Назад")
        self.back_button.setStyleSheet(BUTTON_STYLE)
        self.back_button.clicked.connect(self.go_back)
        bottom_layout.addWidget(self.back_button)

        btn_page2 = QPushButton("Стр. 2 (Карточка)")
        btn_page2.setStyleSheet(BUTTON_STYLE)
        btn_page2.clicked.connect(lambda: self.switch_page(1))
        bottom_layout.addWidget(btn_page2)

        btn_page3 = QPushButton("Стр. 3 (Заказы)")
        btn_page3.setStyleSheet(BUTTON_STYLE)
        btn_page3.clicked.connect(lambda: self.switch_page(2))
        bottom_layout.addWidget(btn_page3)

        bottom_layout.addStretch()
        main_layout.addLayout(bottom_layout)

        self.setWindowTitle(WINDOW_TITLES[0])

    def handle_manager_click(self):
        self.switch_page(2)
        self.show_manager_panel()

    def go_back(self):
        current_index = self.stacked_widget.currentIndex()
        if current_index > 0:
            self.switch_page(current_index - 1)

    def switch_page(self, index):
        self.stacked_widget.setCurrentIndex(index)
        self.setWindowTitle(WINDOW_TITLES.get(index, WINDOW_TITLES[0]))
        if index == 0:
            self.refresh_catalog()

    def refresh_catalog(self):
        self.catalog_page.load_products()

    def load_products(self):
        self.catalog_page.load_products()

    def setup_role_interface(self):
        self.catalog_page.apply_role_visibility(self.role_id)

    def handle_logout_click(self):
        if getattr(self, "_logged_out", False) or getattr(self, "_dialog_open", False):
            return
        self._dialog_open = True

        confirmed = show_warning_confirm(self, "Вы уверены, что хотите выйти?")
        self._dialog_open = False

        if confirmed:
            self._logged_out = True
            self._skip_close_confirm = True
            from app.login_window import LoginWindow

            self.auth_screen = LoginWindow(db=self.db)
            self.auth_screen.show()
            self.close()

    def show_admin_panel(self):
        stats = self.orders_repo.get_admin_stats()
        if stats:
            total_users, total_products, total_sales = stats
            u_count: Any = total_users[0] if isinstance(total_users, (tuple, list)) else total_users
            p_count: Any = total_products[0] if isinstance(total_products, (tuple, list)) else total_products
            raw_sales: Any = total_sales[0] if isinstance(total_sales, (tuple, list)) else total_sales

            u_final = int(u_count) if u_count is not None else 0
            p_final = int(p_count) if p_count is not None else 0
            s_sum = float(raw_sales) if raw_sales is not None else 0.0

            show_info(
                self,
                f"📊 **Сводная статистика базы данных:**\n\n"
                f"👤 Всего пользователей в системе: {u_final}\n"
                f"🎙️ Всего подкастов в каталоге: {p_final}\n"
                f"💰 Общая сумма продаж: {s_sum:.2f} ₽",
                title="Админ-панель — Статистика системы",
            )
        else:
            show_error(self, "Не удалось получить статистику из СУБД!")

    def show_manager_panel(self):
        orders = self.orders_repo.get_all_orders_for_manager()
        if not orders:
            show_info(
                self,
                "В системе пока нет оформленных заказов.",
                title="Панель менеджера",
            )
            return

        orders_text = "📋 **Лог продаж системы (Заказы):**\n\n"
        for order in orders:
            o_id, o_date, l_name, f_name, total_sum = order
            t_sum: Any = total_sum[0] if isinstance(total_sum, (tuple, list)) else total_sum
            f_sum = float(t_sum) if t_sum is not None else 0.0
            orders_text += (
                f"🔹 Заказ №{o_id} от {o_date} — Клиент: {l_name} {f_name}. — Сумма: {f_sum:.2f} ₽\n"
            )

        show_info(self, orders_text, title="Панель менеджера — Список заказов")

    def buy_podcast_mock(self):
        show_info(
            self,
            "Функция оформления заказа запущена! База PostgreSQL проверена.",
            title="Покупка",
        )
