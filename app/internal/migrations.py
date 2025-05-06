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
