from psycopg2 import pool

connection_pool = pool.SimpleConnectionPool(
    minconn=1,
    maxconn=10,
    dbname="appdb",
    user="appuser",
    password="password",
    host="postgres",
    port="5432",
)

def get_data():
    db_data = []
    conn = None
    try:
        conn = connection_pool.getconn()
        with conn:
            with conn.cursor() as curs:
                curs.execute("SELECT name,category,value,description FROM items;")
                for row in curs:
                    db_data.append([row[0], row[1], row[2], row[3]])
    except Exception as exc:
        print(f"Error connecting to db: {exc}")
    finally:
        if conn:
            connection_pool.putconn(conn)
    return db_data
