import sqlite3
import os, sys
import ctypes
from sqlalchemy import create_engine, Table, MetaData
import pandas


class DatabaseManager:
    def __init__(self, db_file):
        # Set up connections to database
        self.db_file = db_file
        self.connection = sqlite3.connect(self.db_file)
        self.cursor = self.connection.cursor()
        self.engine = create_engine(f"sqlite:///{db_file}")

        self.create_categories_table()
        self.create_account_table("credit")
        self.create_account_table("debit")

    def create_categories_table(self):
        self.cursor.execute('''
            CREATE TABLE IF NOT EXISTS categories (
                "id" INTEGER PRIMARY KEY AUTOINCREMENT,
                "name" TEXT UNIQUE NOT NULL
            )
        ''')
        self.connection.commit()

    def create_account_table(self, account):
        self.cursor.execute(f'''
            CREATE TABLE IF NOT EXISTS {account}(
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                "Post Date" DATE NOT NULL,
                "Description" TEXT NOT NULL,
                "Debit" REAL NOT NULL,
                "Credit" REAL NOT NULL,
                "category_id" INTEGER,
                FOREIGN KEY (category_id) REFERENCES categories(id)
            )
        ''')
        self.connection.commit()

    def insert_account_data(self, account, df):
        # Let's use append to avoid needing to rewrite all data
        # When do we see performance issues with rewriting?
        df.to_sql(
            name=f"{account}",
            con=self.engine,
            if_exists="append",  # Options: 'fail', 'replace', 'append'
            index=False,  # Set to True if the DataFrame index should be included
            method="multi" # verify datastore supports method
        )

    def update_categories(self, row_id, account, category):
        # Map string to category_id int
        self.cursor.execute("SELECT id FROM categories WHERE name = ?", (category,))
        result = self.cursor.fetchone()
        self.cursor.execute(f'''
            UPDATE {account}
            SET category_id = ?
            WHERE id = ?
        ''', (result, row_id))

    def add_category(self, new_category):
        # Title case to avoid duplicates
        self.cursor.execute("""
            INSERT OR IGNORE INTO categories (name)
            VALUES (?)
        """, (new_category.title(),))
        self.connection.commit()
