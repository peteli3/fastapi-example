from psycopg2 import pool
import psycopg2.errors
import time

from .migrations import MIGRATIONS

connection_pool = pool.SimpleConnectionPool(
    minconn=1,
    maxconn=10,
    dbname="appdb",
    user="appuser",
    password="password",
    host="postgres",
    port="5432",
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

    def migrate(self):
        if not self.wait_until_ready():
            raise RuntimeError("Could not connect to database after multiple retries")

        with self.Connection() as curs:
            curs.execute("""
                CREATE TABLE IF NOT EXISTS migrations (
                    name TEXT PRIMARY KEY NOT NULL,
                    applied_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP
                );
            """)
            total_migrations = len(MIGRATIONS)
            applied_count = 0

            for i, (name, sql) in enumerate(MIGRATIONS, 1):
                curs.execute("SELECT 1 FROM migrations WHERE name = %s", (name,))
                if curs.fetchone():
                    print(f"[{i}/{total_migrations}] Migration {name} already applied")
                    continue
                print(f"[{i}/{total_migrations}] Applying migration {name}")
                try:
                    curs.execute(sql)
                    status = curs.statusmessage
                    if status:
                        print(f"\tStatus: {status}")
                    curs.execute("INSERT INTO migrations (name) VALUES (%s)", (name,))
                    applied_count += 1

                except Exception as e:
                    print(f"\tError: {str(e)}")
                    raise

            print(f"\nMigration summary:")
            print(f"- Total migrations available: {total_migrations}")
            print(f"- Newly applied: {applied_count}")
            print(f"- Already applied: {total_migrations - applied_count}")
            print()

    def authenticate_user(self, email, password):
        with self.Connection() as curs:
            curs.execute("""SELECT (password_hash = crypt(%(password)s, password_hash)) AS verified
                            FROM users
                            WHERE email = %(email)s;""",
                            { 'email': email,
                              'password': password.decode() })
            row = curs.fetchone()
            return bool(row[0])

    def list_categories(self):
        db_data = []
        try:
            with self.Connection() as curs:
                curs.execute("""SELECT DISTINCT name
                                FROM categories
                                ORDER BY name ASC;""")
                for row in curs:
                    db_data.append(row[0])
        except Exception as exc:
            print(f"Error connecting to db: {exc}")
        return db_data

    def list_items(self):
        db_data = []
        try:
            with self.Connection() as curs:
                curs.execute("""SELECT name, category, value, description
                                FROM items
                                ORDER BY name ASC;""")
                for row in curs:
                    db_data.append([row[0], row[1], row[2], row[3]])
        except Exception as exc:
            print(f"Error connecting to db: {exc}")
        return db_data

    def add_item(self, name, category, value, description):
        try:
            with self.Connection() as curs:
                curs.execute("""INSERT INTO items
                                VALUES (%s, %s, %s, %s);""",
                            (name, category, value, description))
        except psycopg2.errors.UniqueViolation:
            raise RuntimeError("A row with the same primary key already exists.")
        except Exception as exc:
            print(f"Error connecting to db: {exc}")

    def edit_item(self, name, category, value, description):
        try:
            with self.Connection() as curs:
                curs.execute("""UPDATE items
                                SET category=%(category)s,
                                    value=%(value)s,
                                    description=%(description)s
                                WHERE name=%(name)s;""",
                            { 'name': name,
                              'category': category,
                              'value': value,
                              'description': description })
        except Exception as exc:
            print(f"Error connecting to db: {exc}")

    def delete_item(self, name):
        try:
            with self.Connection() as curs:
                curs.execute("""DELETE FROM items
                                WHERE name = %s;""",
                            (name, ))
        except Exception as exc:
            print(f"Error connecting to db: {exc}")

