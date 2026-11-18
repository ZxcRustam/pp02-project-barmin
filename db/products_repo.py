# -*- coding: utf-8 -*-
import psycopg2


class ProductsRepo:
    def __init__(self, db):
        self.db = db

    def get_categories(self):
        conn = self.db.get_connection()
        if conn is None:
            return []
        cursor = None
        try:
            cursor = conn.cursor()
            cursor.execute("SELECT name FROM categories ORDER BY category_id")
            categories = cursor.fetchall()
            return [str(row[0]) for row in categories]
        except psycopg2.Error as e:
            print(f"❌ Ошибка БД при получении категорий: {e}")
            return []
        finally:
            if cursor:
                cursor.close()
            self.db.release_connection(conn)

    def get_products(self, search="", category_text="Все категории", order="ASC"):
        conn = self.db.get_connection()
        if conn is None:
            return []
        cursor = None
        try:
            cursor = conn.cursor()
            pattern = f"%{search}%"
            clean_category = (
                str(category_text)
                .replace("('", "")
                .replace("',)", "")
                .replace("(", "")
                .replace(")", "")
                .strip()
            )

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
            return cursor.fetchall()
        except psycopg2.Error as e:
            print(f"❌ Ошибка БД при получении подкастов: {e}")
            return []
        finally:
            if cursor:
                cursor.close()
            self.db.release_connection(conn)

    def get_monthly_orders_count(self, product_id):
        conn = self.db.get_connection()
        if conn is None:
            return None
        cursor = None
        try:
            cursor = conn.cursor()
            query = """
                SELECT COUNT(*) 
                FROM order_items oi
                JOIN orders o ON oi.order_id = o.order_id
                WHERE oi.product_id = %s
                  AND o.order_date >= CURRENT_DATE - INTERVAL '1 month';
            """
            cursor.execute(query, (product_id,))
            result = cursor.fetchone()
            return result[0] if result is not None else None
        except psycopg2.Error as e:
            print(f"Ошибка БД: {e}")
            return None
        finally:
            if cursor:
                cursor.close()
            self.db.release_connection(conn)
