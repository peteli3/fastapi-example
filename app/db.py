from psycopg2 import pool
import psycopg2.errors

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

