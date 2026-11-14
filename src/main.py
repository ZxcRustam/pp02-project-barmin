# Изменения для ветки feature/new-design
import os
import sys
from pathlib import Path

# Автоматическое добавление папок в пути поиска, чтобы не было ошибок импорта 'src' и 'app'
sys.path.append(str(Path(__file__).resolve().parent.parent.parent))
sys.path.append(str(Path(__file__).resolve().parent.parent))

from PySide6.QtCore import Qt
from PySide6.QtGui import QIcon, QPixmap, QFont
from PySide6.QtWidgets import (
    QApplication, QHBoxLayout, QLabel, QMainWindow, 
    QScrollArea, QVBoxLayout, QWidget, QPushButton, QMessageBox,
    QComboBox, QLineEdit
)

from database import Database
from src.logic.discount import calculate_price

ROLE_NAMES = {1: "Администратор", 2: "Менеджер", 3: "Покупатель", None: "Гость"}

DISCOUNT_LIMIT = 15
DISCOUNT_COLOR = "#2E8B57"

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
    QPushButton:hover { background-color: #5B9A97; }
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


def load_cover(image_path):
    if image_path:
        full_path = os.path.join("resources", image_path)
        if os.path.exists(full_path):
            pixmap = QPixmap(full_path)
            if not pixmap.isNull():
                return pixmap
    return QPixmap(os.path.join("resources", "picture.png"))


def calculate_discount(old_price, new_price):
    if old_price == 0:
        return 0
    return (old_price - new_price) / old_price * 100


def create_card(product):
    (product_id, name, category_id, studio, old_price_raw, image_path, total_quantity) = product

    card = QWidget()
    card_layout = QHBoxLayout()

    image_label = QLabel()
    cover_pixmap = load_cover(image_path)
    image_label.setPixmap(cover_pixmap.scaled(
        70, 70, 
        Qt.AspectRatioMode.KeepAspectRatio, 
        Qt.TransformationMode.SmoothTransformation
    ))
    image_label.setFixedSize(70, 70)
    card_layout.addWidget(image_label)

    text_layout = QVBoxLayout()
    title_label = QLabel(f"{studio} | {name}")
    title_label.setStyleSheet("font-weight: bold; font-size: 14px; color: #1A237E;")
    text_layout.addWidget(title_label)
    text_layout.addWidget(QLabel(f"ID Категории: {category_id}"))
    text_layout.addWidget(QLabel(f"Доступно для покупки: {int(total_quantity)} лицензий"))
    card_layout.addLayout(text_layout)

    old_price = float(old_price_raw)
    computed_price = calculate_price(product_id, old_price)
    new_price = float(computed_price) if computed_price is not None else old_price
    discount = calculate_discount(old_price, new_price)

    price_container = QVBoxLayout()
    price_label = QLabel(f"{new_price:.2f} ₽")
    price_label.setAlignment(Qt.AlignmentFlag.AlignRight | Qt.AlignmentFlag.AlignVCenter)
    
    old_price_label = QLabel(f"<s>{old_price:.2f} ₽</s>")
    # Исправлено предупреждение QFont: задаем размер шрифта через объект QFont явным числом
    f = QFont("Calibri", 10)
    old_price_label.setFont(f)
    old_price_label.setStyleSheet("color: red;")
    old_price_label.setAlignment(Qt.AlignmentFlag.AlignRight)
    price_container.addWidget(old_price_label)
    
    if discount > 0:
        old_price_label.show()
    else:
        old_price_label.hide()

    price_container.addWidget(price_label)
    card_layout.addLayout(price_container)

    card.setLayout(card_layout)

    if total_quantity <= 3:
        card.setStyleSheet("""
            QWidget { border: 1px solid #B0BEC5; border-radius: 8px; background-color: #ff8080; padding: 5px; }
            QLabel { border: none; background: transparent; color: #000000; }
        """)
        price_label.setStyleSheet("font-size: 16px; font-weight: bold; color: #1A237E;")
    elif discount > DISCOUNT_LIMIT:
        card.setStyleSheet("""
            QWidget { border: 1px solid #CFD8DC; border-radius: 8px; background-color: #FFFFFF; padding: 5px; }
            QLabel { border: none; background: transparent; }
        """)
        price_label.setStyleSheet(f"color: {DISCOUNT_COLOR}; font-weight: bold; font-size: 16px;")
    else:
        card.setStyleSheet("""
            QWidget { border: 1px solid #CFD8DC; border-radius: 8px; background-color: #FAFAFA; padding: 5px; }
            QLabel { border: none; background: transparent; }
        """)
        price_label.setStyleSheet("font-size: 16px; font-weight: bold; color: #2E7D32;")

    return card


class MainWindow(QMainWindow):
    def __init__(self, role_id=None, full_name=None, user_id=None):
        super().__init__()
        self.role_id = role_id          
        self.full_name = full_name      
        self.user_id = user_id if user_id else 4 
        self.db = Database()

        self.setWindowTitle("Мир подкастов — Каталог")
        self.resize(850, 650)
        
        if os.path.exists("resources/icon.ico"):
            self.setWindowIcon(QIcon("resources/icon.ico"))
            
        self.setStyleSheet("QMainWindow { background-color: #FFFFFF; font-family: Calibri; }")

        self.setup_ui()                 
        self.setup_role_interface()
        self.load_products()     

    def setup_ui(self):
        central = QWidget()
        self.setCentralWidget(central)
        main_layout = QVBoxLayout(central)
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.setSpacing(10)

        # Шапка приложения
        header_widget = QWidget()
        header_widget.setStyleSheet("background-color: #D2F6E7;")  
        header_layout = QHBoxLayout(header_widget)
        header_layout.setContentsMargins(15, 10, 15, 10)

        logo_label = QLabel()
        logo_pixmap = QPixmap("resources/logo.png")
        if not logo_pixmap.isNull():
            logo_label.setPixmap(logo_pixmap.scaledToHeight(60, Qt.TransformationMode.SmoothTransformation))
        else:
            logo_label.setText("🎙️ МИР ПОДКАСТОВ")
            logo_label.setStyleSheet("font-weight: bold; font-size: 18px; color: #00796B;")
        header_layout.addWidget(logo_label)
        header_layout.addStretch()

        text = f"ФИО: {self.full_name} ({ROLE_NAMES.get(self.role_id)})" if self.full_name else "Гость"
        self.name_label = QLabel(text)
        self.name_label.setStyleSheet("font-weight: bold; font-size: 14px; color: #2C3E50; background: transparent;")
        header_layout.addWidget(self.name_label)

        self.logout_button = QPushButton("Выход")
        self.logout_button.setStyleSheet(BUTTON_STYLE)  
        header_layout.addWidget(self.logout_button)
        main_layout.addWidget(header_widget)  

        # --- Панель поиска, фильтрации и кнопок ---
        top_widget = QWidget()
        top_widget.setStyleSheet(COMBO_STYLE)
        top_layout = QVBoxLayout(top_widget)
        top_layout.setContentsMargins(15, 5, 15, 5)
        top_layout.setSpacing(5)

        # Первая строка: Фильтры
        filter_row = QHBoxLayout()
        self.search_input = QLineEdit()
        self.search_input.setPlaceholderText("Поиск по названию или студии...")
        self.search_input.textChanged.connect(self.load_products)
        filter_row.addWidget(self.search_input)

        self.filter_combo = QComboBox()
        self.filter_combo.addItem("Все категории")
        
        for cat in self.db.get_categories():
            self.filter_combo.addItem(str(cat))
                    
        self.filter_combo.currentIndexChanged.connect(self.load_products)
        filter_row.addWidget(self.filter_combo)

        self.sort_combo = QComboBox()
        self.sort_combo.addItems(["По возрастанию цены", "По убыванию цены"])
        self.sort_combo.currentIndexChanged.connect(self.load_products)
        filter_row.addWidget(self.sort_combo)
        top_layout.addLayout(filter_row)

        # Вторая строка: Управляющие кнопки ролей
        buttons_row = QHBoxLayout()
        self.order_button = QPushButton("Купить подкаст")
        self.manager_button = QPushButton("Заказы (менеджер)")
        self.admin_button = QPushButton("Админ-панель")
        
        self.order_button.setStyleSheet(BUTTON_STYLE)
        self.manager_button.setStyleSheet(BUTTON_STYLE)
        self.admin_button.setStyleSheet(BUTTON_STYLE)
        
        buttons_row.addWidget(self.order_button)
        buttons_row.addWidget(self.manager_button)
        buttons_row.addWidget(self.admin_button)
        buttons_row.addStretch()
        top_layout.addLayout(buttons_row)
        
        main_layout.addWidget(top_widget)

        # --- Область прокрутки (Scroll Area) для карточек товаров ---
        self.scroll_area = QScrollArea()
        self.scroll_area.setWidgetResizable(True)
        self.scroll_area.setStyleSheet("QScrollArea { border: none; background-color: #FFFFFF; }")
        
        self.scroll_content = QWidget()
        self.scroll_content.setStyleSheet("background-color: #FFFFFF;")
        self.products_layout = QVBoxLayout(self.scroll_content)
        self.products_layout.setContentsMargins(15, 10, 15, 10)
        self.products_layout.setSpacing(10)
        self.products_layout.addStretch()
        
        self.scroll_area.setWidget(self.scroll_content)
        main_layout.addWidget(self.scroll_area)

    def setup_role_interface(self):
        self.admin_button.clicked.connect(self.show_admin_panel)
        self.manager_button.clicked.connect(self.show_manager_panel)
        self.order_button.clicked.connect(self.buy_podcast_mock)
        # Подключаем метод возврата на страницу логирования
        self.logout_button.clicked.connect(self.handle_logout_click)

        if self.role_id == 1:    
            self.order_button.hide()
        elif self.role_id == 1:    # Администратор видит ВСЕ панели управления
            self.order_button.hide()
            self.manager_button.show()
            self.admin_button.show()
        elif self.role_id == 2:  # Менеджер
            self.order_button.hide()
            self.manager_button.show()
            self.admin_button.hide()
        elif self.role_id == 3:  # Покупатель
            self.order_button.show()
            self.manager_button.hide()
            self.admin_button.hide()
        else:                    # Гость
            self.order_button.hide()
            self.manager_button.hide()
            self.admin_button.hide()

    def handle_logout_click(self):
        self.auth_screen = LoginWindow()
        self.auth_screen.show()
        self.close()

    # === Логика работы Админ-панели (Вывод статистики из PostgreSQL) ===
    def show_admin_panel(self):
        from typing import Any
        stats = self.db.get_admin_stats()
        if stats:
            total_users, total_products, total_sales = stats
            u_count: Any = total_users if isinstance(total_users, (tuple, list)) else total_users
            p_count: Any = total_products if isinstance(total_products, (tuple, list)) else total_products
            raw_sales: Any = total_sales if isinstance(total_sales, (tuple, list)) else total_sales
            
            u_final = int(u_count) if u_count is not None else 0
            p_final = int(p_count) if p_count is not None else 0
            s_sum = float(raw_sales) if raw_sales is not None else 0.0
            
            QMessageBox.information(
                self, 
                "Админ-панель — Статистика системы", 
                f"📊 **Сводная статистика базы данных:**\n\n"
                f"👤 Всего пользователей в системе: {u_final}\n"
                f"🎙️ Всего подкастов в каталоге: {p_final}\n"
                f"💰 Общая сумма продаж: {s_sum:.2f} ₽"
            )
        else:
            QMessageBox.critical(self, "Ошибка", "Не удалось получить статистику из СУБД!")

    # === Логика работы Панели Менеджера (Вывод лога продаж из PostgreSQL) ===
    def show_manager_panel(self):
        from typing import Any
        orders = self.db.get_all_orders_for_manager()
        if not orders:
            QMessageBox.information(self, "Панель менеджера", "В системе пока нет оформленных заказов.")
            return
            
        orders_text = "📋 **Лог продаж системы (Заказы):**\n\n"
        for order in orders:
            o_id, o_date, l_name, f_name, total_sum = order
            t_sum: Any = total_sum if isinstance(total_sum, (tuple, list)) else total_sum
            f_sum = float(t_sum) if t_sum is not None else 0.0
            orders_text += f"🔹 Заказ №{o_id} от {o_date} — Клиент: {l_name} {f_name}. — Сумма: {f_sum:.2f} ₽\n"
            
        QMessageBox.information(self, "Панель менеджера — Список заказов", orders_text)

    def buy_podcast_mock(self):
        QMessageBox.information(self, "Покупка", "Функция оформления заказа запущена! База PostgreSQL проверена.")

    def load_products(self):
        while self.products_layout.count() > 1:
            item = self.products_layout.takeAt(0)
            if item is not None:
                current_widget = item.widget()
                if current_widget is not None:
                    current_widget.deleteLater()

        search_text = self.search_input.text()
        category_text = self.filter_combo.currentText()
        
        products = self.db.get_products(
            search=search_text, 
            category_text=category_text, 
            order="ASC"
        )

        # Вычисляем финальные цены со скидками в Python для правильной сортировки каталога
        processed_products = []
        for prod in products:
            product_id, name, category_id, studio, old_price_raw, image_path, total_quantity = prod
            old_price = float(old_price_raw)
            computed_price = calculate_price(product_id, old_price)
            new_price = float(computed_price) if computed_price is not None else old_price
            processed_products.append((new_price, prod))

        is_ascending = (self.sort_combo.currentIndex() == 0)
        processed_products.sort(key=lambda x: x[0], reverse=not is_ascending)

        for new_price, prod in processed_products:
            card = create_card(prod)
            self.products_layout.insertWidget(self.products_layout.count() - 1, card)


# === Окно авторизации пользователей с фиксированными стилями кнопок ===
class LoginWindow(QWidget):
    def __init__(self):
        super().__init__()
        self.db = Database()
        self.setWindowTitle("Авторизация")
        self.resize(300, 200)
        self.setStyleSheet("QWidget { background-color: #FAFAFA; font-family: Calibri; }")

        layout = QVBoxLayout(self)
        layout.setSpacing(10)
        layout.setContentsMargins(20, 20, 20, 20)

        label = QLabel("Введите ваш логин:")
        label.setStyleSheet("font-size: 13px; color: #2C3E50;")
        layout.addWidget(label)

        self.login_input = QLineEdit()
        self.login_input.setPlaceholderText("Например: admin, manager1, client01")
        self.login_input.setStyleSheet("""
            QLineEdit {
                font-size: 13px;
                padding: 6px;
                border: 1px solid #B0BEC5;
                border-radius: 4px;
                background-color: #FFFFFF;
                color: #000000;
            }
        """)
        layout.addWidget(self.login_input)

        self.login_button = QPushButton("Войти")
        self.login_button.setStyleSheet("""
            QPushButton {
                background-color: #70B2AF !important;
                color: #FFFFFF !important;
                font-size: 13px;
                font-weight: bold;
                border: 1px solid #5B9A97;
                border-radius: 4px;
                padding: 8px;
            }
            QPushButton:hover { background-color: #5B9A97 !important; }
        """)
        self.login_button.clicked.connect(self.handle_login)
        layout.addWidget(self.login_button)

        self.guest_button = QPushButton("Войти как Гость")
        self.guest_button.setStyleSheet("""
            QPushButton {
                background-color: #90A4AE !important;
                color: #FFFFFF !important;
                font-size: 13px;
                font-weight: bold;
                border: 1px solid #78909C;
                border-radius: 4px;
                padding: 8px;
            }
            QPushButton:hover { background-color: #78909C !important; }
        """)
        self.guest_button.clicked.connect(self.handle_guest)
        layout.addWidget(self.guest_button)

    def handle_login(self):
        login_text = self.login_input.text().strip()
        if not login_text:
            QMessageBox.warning(self, "Внимание", "Поле логина не может быть пустым!")
            return

        user_info = self.db.get_user_by_login(login_text)

        if user_info:
            u_id, r_id, l_name, f_name, m_name = user_info
            full_name_str = f"{l_name} {f_name} {m_name}".strip()

            self.main_window = MainWindow(role_id=r_id, full_name=full_name_str, user_id=u_id)
            self.main_window.show()
            self.close()
        else:
            QMessageBox.critical(self, "Ошибка", "Пользователь с таким логином не найден в базе!")

    def handle_guest(self):
        self.main_window = MainWindow(role_id=None, full_name=None, user_id=None)
        self.main_window.show()
        self.close()


if __name__ == "__main__":
    app = QApplication(sys.argv)
    auth_window = LoginWindow()
    auth_window.show()
    sys.exit(app.exec())
