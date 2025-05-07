from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from .db import DB

MIGRATIONS = [
    ("001_add_uuid_extension", """
        CREATE EXTENSION IF NOT EXISTS "uuid-ossp";
    """),
    ("002_add_pgcrypto_extension", """
        CREATE EXTENSION IF NOT EXISTS "pgcrypto";
    """),
    ("003_create_categories_table", """
        CREATE TABLE IF NOT EXISTS categories (
            name VARCHAR(256) PRIMARY KEY
        );
    """),
    ("004_create_items_table", """
        CREATE TABLE IF NOT EXISTS items (
            name VARCHAR(256) PRIMARY KEY NOT NULL,
            category VARCHAR(256) REFERENCES categories(name),
            value INTEGER DEFAULT 0,
            description TEXT
        );
    """),
    ("005_create_users_table", """
        CREATE TABLE IF NOT EXISTS users (
            id UUID PRIMARY KEY DEFAULT uuid_generate_v4() NOT NULL,
            email VARCHAR(256) UNIQUE NOT NULL,
            password_hash TEXT NOT NULL
        );
    """),
]

class Migrations:
    def __init__(self, db: 'DB'):
        self.db = db

    def run(self):
        if not self.db.wait_until_ready():
            raise RuntimeError("Could not connect to database after multiple retries")

        with self.db.Connection() as curs:
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
