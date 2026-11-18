# -*- coding: utf-8 -*-
import psycopg2
from config import DB_CONFIG


def calculate_price(product_id, base_price, products_repo=None):
    if isinstance(product_id, bool) or not isinstance(product_id, int):
        print("Ошибка: product_id должен быть целым числом")
        return None

    if isinstance(base_price, bool) or not isinstance(base_price, (int, float)):
        print("Ошибка: base_price должен быть числом")
        return None

    if base_price <= 0:
        print("Ошибка: цена должна быть > 0")
        return None

    if products_repo is not None:
        orders_count = products_repo.get_monthly_orders_count(product_id)
        if orders_count is None:
            return None
        return round(base_price * 0.75, 2) if orders_count == 0 else round(base_price, 2)

    connection = None
    cursor = None
    try:
        connection = psycopg2.connect(**DB_CONFIG)
        cursor = connection.cursor()
        query = """
            SELECT COUNT(*) 
            FROM order_items oi
            JOIN orders o ON oi.order_id = o.order_id
            WHERE oi.product_id = %s
              AND o.order_date >= CURRENT_DATE - INTERVAL '1 month';
        """
        cursor.execute(query, (product_id,))
        result = cursor.fetchone()
        if result is None:
            print("Ошибка: нет результата")
            return None

        orders_count = result[0]
        return round(base_price * 0.75, 2) if orders_count == 0 else round(base_price, 2)
    except psycopg2.Error as e:
        print(f"Ошибка БД: {e}")
        return None
    except Exception as e:
        print(f"Системная ошибка: {e}")
        return None
    finally:
        if cursor:
            cursor.close()
        if connection:
            connection.close()


def calculate_discount(old_price, new_price):
    if old_price == 0:
        return 0
    return (old_price - new_price) / old_price * 100
