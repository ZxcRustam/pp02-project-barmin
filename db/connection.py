# -*- coding: utf-8 -*-
import psycopg2
from psycopg2 import pool
from config import DB_CONFIG


class Database:
    def __init__(self):
        try:
            self.connection_pool = pool.SimpleConnectionPool(
                minconn=1,
                maxconn=5,
                **DB_CONFIG,
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

    def close_all(self):
        if self.connection_pool is not None:
            self.connection_pool.closeall()
