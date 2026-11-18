import psycopg2
from psycopg2 import pool


class Database:

    def __init__(self):
        try:
            self.connection_pool = pool.SimpleConnectionPool(
                minconn=1,
                maxconn=5,
                dbname="podcasts_db",
                user="postgres",
                password="123",  # <-- Ваш пароль от PostgreSQL
                host="127.0.0.1",
                port=5432,
            )
        except psycopg2.Error as e:
            print(f"❌ Ошибка БД при инициализации пула: {e}")
            self.connection_pool = None

    def get_connection(self):
        if not self.connection_pool:
            return None
        try:
            return self.connection_pool.getconn()
        except psycopg2.Error as e:
            print(f"❌ Ошибка получения соединения из пула: {e}")
            return None

    def release_connection(self, conn):
        if conn and self.connection_pool:
            try:
                self.connection_pool.putconn(conn)
            except psycopg2.Error:
                pass

    # --- ЗАДАНИЕ 1.1: Получение списка уникальных категорий из БД ---
    def get_categories(self):
        conn = self.get_connection()
        if conn is None:
            return []
        cursor = None
        try:
            cursor = conn.cursor()
            cursor.execute("SELECT name FROM categories ORDER BY category_id")
            categories = cursor.fetchall()
            cursor.close()
            # Распаковываем кортежи в плоские элементы
            return [str(row[0]) for row in categories]
        except psycopg2.Error as e:
            print(f"❌ Ошибка БД при получении категорий: {e}")
            return []
        finally:
            self.release_connection(conn)

    # --- ЗАДАНИЕ 5.1 и 7.1: Получение подкастов с поиском, фильтром и сортировкой (PostgreSQL) ---
    def get_products(self, search="", category_text="Все категории", order="ASC"):
        conn = self.get_connection()
        if conn is None:
            return []
        cursor = None
        try:
            cursor = conn.cursor()
            pattern = f"%{search}%"

            clean_category = str(category_text).replace("('", "").replace("',)", "").replace("(", "").replace(")", "").strip()

            query = f"""
                SELECT 
                    p.product_id, 
                    p.name, 
                    c.name AS category_name, 
                    p.manufacturer AS studio, 
                    p.price, 
                    p.image_path, 
                    COALESCE(SUM(si.quantity), 0) AS total_quantity
                FROM products p
                LEFT JOIN categories c ON p.category_id = c.category_id
                LEFT JOIN stock_items si ON p.product_id = si.product_id
                WHERE (p.name ILIKE %s OR p.manufacturer ILIKE %s)
                  AND (c.name = %s OR %s = 'Все категории')
                GROUP BY 
                    p.product_id, 
                    p.name, 
                    c.name, 
                    p.manufacturer, 
                    p.price, 
                    p.image_path
                ORDER BY p.price {order}
            """

            cursor.execute(query, (pattern, pattern, clean_category, category_text))
            products = cursor.fetchall()
            cursor.close()
            return products
        except psycopg2.Error as e:
            print(f"❌ Ошибка БД при получении подкастов: {e}")
            return []
        finally:
            self.release_connection(conn)


    def get_user_by_login(self, login):
        conn = self.get_connection()
        if conn is None:
            return None
        cursor = None
        try:
            cursor = conn.cursor()
            cursor.execute(
                "SELECT user_id, role_id, last_name, first_name, COALESCE(middle_name, '') "
                "FROM users WHERE login = %s",
                (login,)
            )
            return cursor.fetchone()
        except psycopg2.Error as e:
            print(f"❌ Ошибка БД при поиске пользователя: {e}")
            return None
        finally:
            if cursor:
                cursor.close()
            self.release_connection(conn)

    def close_all(self):
        if self.connection_pool is not None:
            self.connection_pool.closeall()

    # === ЗАДАНИЕ 12: Оформление заказа (Откатоустойчивая транзакция через пул) ===
    def create_order(self, user_id, product_id, size_id, quantity, price):
        conn = self.get_connection()
        if conn is None:
            return False, "Нет соединения с базой данных!"
        cursor = None
        try:
            cursor = conn.cursor()
            
            cursor.execute(
                "SELECT quantity FROM stock_items WHERE product_id = %s AND size_id = %s",
                (product_id, size_id)
            )
            res = cursor.fetchone()
            if not res or res[0] < quantity:
                return False, "Недостаточно доступных лицензий на складе!"

            cursor.execute(
                "INSERT INTO orders (order_date, user_id) VALUES (CURRENT_DATE, %s) RETURNING order_id",
                (user_id,)
            )
            order_res = cursor.fetchone()
            if not order_res:
                return False, "Ошибка при генерации ID заказа!"
            order_id = order_res[0]
            
            cursor.execute(
                "INSERT INTO order_items (order_id, product_id, size_id, quantity, price) VALUES (%s, %s, %s, %s, %s)",
                (order_id, product_id, size_id, quantity, price)
            )
            
            cursor.execute(
                "UPDATE stock_items SET quantity = quantity - %s WHERE product_id = %s AND size_id = %s",
                (quantity, product_id, size_id)
            )
            
            conn.commit()
            return True, f"Заказ №{order_id} успешно оформлен! База обновлена."
        except psycopg2.Error as e:
            conn.rollback()
            return False, f"❌ Ошибка при оформлении транзакции: {e}"
        finally:
            if cursor:
                cursor.close()
            self.release_connection(conn)

    # === ЗАДАНИЕ 13: Управление заказами ===
    def get_all_orders_for_manager(self):
        conn = self.get_connection()
        if conn is None:
            return []
        cursor = None
        try:
            cursor = conn.cursor()
            cursor.execute("""
                SELECT 
                    o.order_id, 
                    TO_CHAR(o.order_date, 'DD.MM.YYYY') AS date, 
                    u.last_name, 
                    u.first_name, 
                    SUM(oi.quantity * oi.price) AS total_sum
                FROM orders o
                JOIN users u ON o.user_id = u.user_id
                JOIN order_items oi ON o.order_id = oi.order_id
                GROUP BY o.order_id, o.order_date, u.last_name, u.first_name
                ORDER BY o.order_id DESC
            """)
            orders = cursor.fetchall()
            cursor.close()
            return orders
        except psycopg2.Error as e:
            print(f"❌ Ошибка при выгрузке списка заказов: {e}")
            return []
        finally:
            self.release_connection(conn)

    # === ЗАДАНИЕ ДЛЯ АДМИН-ПАНЕЛИ: Сбор сводной статистики системы ===
    def get_admin_stats(self):
        conn = self.get_connection()
        if conn is None:
            return None
        cursor = None
        try:
            cursor = conn.cursor()
            
            cursor.execute("SELECT COUNT(*) FROM users")
            u_res = cursor.fetchone()
            total_users = u_res[0] if u_res else 0
            
            cursor.execute("SELECT COUNT(*) FROM products")
            p_res = cursor.fetchone()
            total_products = p_res[0] if p_res else 0
            
            cursor.execute("SELECT COALESCE(SUM(quantity * price), 0) FROM order_items")
            s_res = cursor.fetchone()
            total_sales = s_res[0] if s_res else 0
            
            cursor.close()
            # Исправлено: теперь возвращаются все три значения корректно
            return total_users, total_products, total_sales
        except psycopg2.Error as e:
            print(f"❌ Ошибка БД при сборе статистики админа: {e}")
            return None
        finally:
            self.release_connection(conn)
