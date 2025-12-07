import sqlite3
import os, sys
import ctypes
from uuid import uuid4
import re
import pandas


class DatabaseManager:
    def __init__(self, db_file):
        # Set up connections to database
        self.db_file = db_file
        self.connection = sqlite3.connect(self.db_file)
        self.cursor = self.connection.cursor()

        self.create_categories_table()
        self.create_account_table("credit")
        self.create_account_table("debit")

    def create_categories_table(self):
        create_cat_table_sql = f'''
            CREATE TABLE IF NOT EXISTS categories (
                "id" INTEGER PRIMARY KEY AUTOINCREMENT,
                "name" TEXT UNIQUE NOT NULL
            );
        '''
        self.connection.execute(create_cat_table_sql)

    def create_account_table(self, account):
        create_account_table_sql = f'''
            CREATE TABLE IF NOT EXISTS "{account}"(
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                "Post Date" DATE NOT NULL,
                "Description" TEXT NOT NULL,
                "Debit" REAL,
                "Credit" REAL,
                "category_id" INTEGER,
                FOREIGN KEY (category_id) REFERENCES categories(id),
                UNIQUE ("Post Date", "Description", "Debit", "Credit")
            );
        '''
        self.connection.execute(create_account_table_sql)

    def upsert_account_data(self, account, df):
        # Validate table name
        if not re.match(r'^[A-Za-z_][A-Za-z0-9_]*$', account):
            raise ValueError(f"Invalid table name: {account}")

        # Generate temp table
        temp_table = f"tmp_{account}_{uuid4().hex[:8]}"
        df.to_sql(
            name=temp_table,
            con=self.connection,  # use sqlite3 connection
            if_exists="replace",
            index=False,
            method="multi"
        )

        self.cursor.execute(f'SELECT COUNT(*) FROM "{temp_table}"')
        print("Temp table rows:", self.cursor.fetchone()[0])

        # UPSERT
        upsert_sql = f'''
        INSERT OR IGNORE INTO "{account}" ("Post Date", "Description", "Debit", "Credit")
        SELECT "Post Date", "Description", "Debit", "Credit"
        FROM "{temp_table}";
        '''

        drop_sql = f'DROP TABLE IF EXISTS "{temp_table}";'

        with self.connection:
            self.connection.execute(upsert_sql)
            self.connection.execute(drop_sql)

    def update_categories(self, row_id, account, category):
        # Select category foreign id
        foreign_id_sql = "SELECT id FROM categories WHERE name = ?"
        self.cursor.execute(foreign_id_sql, (category,))
        result = self.cursor.fetchone()
        self.cursor.execute(f'''
            UPDATE {account}
            SET category_id = ?
            WHERE id = ?
        ''', (result, row_id))
        self.connection.commit()

    def add_category(self, new_category):
        # Title case to avoid duplicates
        self.cursor.execute("""
            INSERT OR IGNORE INTO categories (name)
            VALUES (?)
        """, (new_category.title(),))
        self.connection.commit()
