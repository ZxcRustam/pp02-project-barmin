# -*- coding: utf-8 -*-
import psycopg2


class OrdersRepo:
    def __init__(self, db):
        self.db = db

    def create_order(self, user_id, product_id, size_id, quantity, price):
        conn = self.db.get_connection()
        if conn is None:
            return False, "Нет соединения с базой данных!"
        cursor = None
        try:
            cursor = conn.cursor()
            cursor.execute(
                "SELECT quantity FROM stock_items WHERE product_id = %s AND size_id = %s",
                (product_id, size_id),
            )
            res = cursor.fetchone()
            if not res or res[0] < quantity:
                return False, "Недостаточно доступных лицензий на складе!"

            cursor.execute(
                "INSERT INTO orders (order_date, user_id) VALUES (CURRENT_DATE, %s) RETURNING order_id",
                (user_id,),
            )
            order_res = cursor.fetchone()
            if not order_res:
                return False, "Ошибка при генерации ID заказа!"
            order_id = order_res[0]

            cursor.execute(
                "INSERT INTO order_items (order_id, product_id, size_id, quantity, price) "
                "VALUES (%s, %s, %s, %s, %s)",
                (order_id, product_id, size_id, quantity, price),
            )

            cursor.execute(
                "UPDATE stock_items SET quantity = quantity - %s "
                "WHERE product_id = %s AND size_id = %s",
                (quantity, product_id, size_id),
            )

            conn.commit()
            return True, f"Заказ №{order_id} успешно оформлен! База обновлена."
        except psycopg2.Error as e:
            conn.rollback()
            return False, f"❌ Ошибка при оформлении транзакции: {e}"
        finally:
            if cursor:
                cursor.close()
            self.db.release_connection(conn)

    def get_all_orders_for_manager(self):
        conn = self.db.get_connection()
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
            return cursor.fetchall()
        except psycopg2.Error as e:
            print(f"❌ Ошибка при выгрузке списка заказов: {e}")
            return []
        finally:
            if cursor:
                cursor.close()
            self.db.release_connection(conn)

    def get_admin_stats(self):
        conn = self.db.get_connection()
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

            return total_users, total_products, total_sales
        except psycopg2.Error as e:
            print(f"❌ Ошибка БД при сборе статистики админа: {e}")
            return None
        finally:
            if cursor:
                cursor.close()
            self.db.release_connection(conn)
