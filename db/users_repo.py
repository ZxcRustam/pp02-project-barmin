# -*- coding: utf-8 -*-
import psycopg2


class UsersRepo:
    def __init__(self, db):
        self.db = db

    def get_user_by_login(self, login):
        conn = self.db.get_connection()
        if conn is None:
            return None
        cursor = None
        try:
            cursor = conn.cursor()
            cursor.execute(
                "SELECT user_id, role_id, last_name, first_name, COALESCE(middle_name, '') "
                "FROM users WHERE login = %s",
                (login,),
            )
            return cursor.fetchone()
        except psycopg2.Error as e:
            print(f"❌ Ошибка БД при поиске пользователя: {e}")
            return None
        finally:
            if cursor:
                cursor.close()
            self.db.release_connection(conn)
