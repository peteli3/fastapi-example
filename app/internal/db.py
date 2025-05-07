from psycopg2 import pool
import os
import time

from .migrations import Migrations
from .authentication import Authentication
from .items import ItemRepository

connection_pool = pool.SimpleConnectionPool(
    minconn=1,
    maxconn=10,
    host=os.getenv("POSTGRES_HOST"),
    dbname=os.getenv("POSTGRES_DB"),
    user=os.getenv("POSTGRES_USER"),
    password=os.getenv("POSTGRES_PASSWORD"),
    port=os.getenv("POSTGRES_PORT"),
)

class DB:
    class Connection:
        def __init__(self):
            self.conn = None

        def __enter__(self):
            self.conn = connection_pool.getconn()
            return self.conn.cursor()

        def __exit__(self, exc_type, exc_val, exc_tb):
            if self.conn:
                if exc_type is None:
                    self.conn.commit()
                connection_pool.putconn(self.conn)

    def __init__(self):
        self.migrations     = Migrations(self)
        self.authentication = Authentication(self)
        self.items          = ItemRepository(self)

    def is_ready(self):
        try:
            with self.Connection() as curs:
                curs.execute("SELECT 1")
                return True
        except Exception as exc:
            print(f"Error connecting to db: {exc}")
            return False

    def wait_until_ready(self, max_retries=10, initial_delay=1):
        delay = initial_delay
        for attempt in range(max_retries):
            print(f"Waiting for database to be ready... (attempt {attempt + 1}/{max_retries})")
            if self.is_ready():
                return True
            if attempt < max_retries - 1:  # Don't sleep on the last attempt
                time.sleep(delay)
                delay = min(delay * 2, 30)  # Exponential backoff with max 30s delay
        return False
