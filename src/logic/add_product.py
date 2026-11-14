import psycopg2
from psycopg2 import errorcodes


def add_product(name, price, category_id):
    # 1. Проверка входных данных в Python
    if not isinstance(name, str) or not name.strip():
        print("Ошибка: название не должно быть пустым")
        return False

    if not isinstance(price, (int, float)) or price <= 0:
        print("Ошибка: цена должна быть > 0")
        return False

    if not isinstance(category_id, int):
        print("Ошибка: category_id должен быть числом")
        return False

    conn = None
    cursor = None

    try:
        # Подключение к вашей СУБД PostgreSQL
        conn = psycopg2.connect(
            dbname="podcasts_db",
            user="postgres",
            password="1234",  # Ваш рабочий пароль
            host="127.0.0.1",
            port=5432,
        )
        cursor = conn.cursor()

        # 2. Выполнение команды INSERT с обработкой ошибок структуры БД
        try:
            # Передаем обязательное поле manufacturer, так как поле NOT NULL
            query = """
                INSERT INTO products (name, price, category_id, manufacturer) 
                VALUES (%s, %s, %s, %s);
            """
            cursor.execute(
                query, (name.strip(), price, category_id, "Студия Диалог")
            )
        except psycopg2.Error as e:
            conn.rollback()
            # 23503 — код PostgreSQL для нарушения ограничений внешнего ключа (FOREIGN KEY)
            if e.pgcode == errorcodes.FOREIGN_KEY_VIOLATION:
                print("Ошибка: категории с таким category_id нет в БД")
            else:
                print(f"Ошибка вставки: {e}")
            return False

        # 3. Фиксация изменений в БД
        try:
            conn.commit()
        except psycopg2.Error as e:
            conn.rollback()
            print(f"Ошибка при сохранении: {e}")
            return False

        print("Товар добавлен в БД")
        return True

    except psycopg2.Error as e:
        print(f"Ошибка БД: {e}")
        return False
    except Exception as e:
        print(f"Неизвестная ошибка: {e}")
        return False

    # 4. Гарантированное закрытие соединений
    finally:
        if cursor:
            cursor.close()
        if conn:
            conn.close()


# --- БЛОК ТЕСТИРОВАНИЯ (Задание 5.2) ---
if __name__ == "__main__":
    print("--- СТАРТ ТЕСТИРОВАНИЯ ВСТАВКИ ---")

    print("\nТест 1 (Пустое имя):")
    add_product("", 1000, 1)

    print("\nТест 2 (Цена < 0):")
    add_product("Часы", -100, 1)

    print("\nТест 3 (Категория 99999):")
    add_product("Часы", 1000, 99999)

    print("\nТест 4 (Всё правильно):")
    add_product("Часы", 1000, 1)

    print("\n--- ТЕСТИРОВАНИЕ ЗАВЕРШЕНО ---")
