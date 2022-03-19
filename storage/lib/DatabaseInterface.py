import sqlite3
import logging


class DatabaseInterface:
    def __init__(self, db_name):
        self.connection = None
        self.db_name = db_name
        self.db = self.prepare_db()

    def prepare_db(self):
        return f"databases/{self.db_name}"

    def connect(self):
        self.connection = sqlite3.connect(self.db_name)
        self.connection.isolation_level = None
        self.connection.execute("PRAGMA journal_mode=wal")

    def create_table(self):
        self.connection.execute("create table if not exists news(id integer primary key autoincrement, title)")

    def prepare_query(self, action, data):
        if action == "add_data":
            query = f"insert into news(title) values(?)"
            self.execute_query(query, data)
        else:
            logging.warning("Invalid query requested")

    def execute_query(self, query, data):
        self.connection.execute(query, data)

    def checkpoint(self):
        self.connection.execute("PRAGMA journal_size_limit=0")
        self.connection.execute("PRAGMA wal_checkpoint(truncate)")

    def disconnect(self):
        self.connection.close()
