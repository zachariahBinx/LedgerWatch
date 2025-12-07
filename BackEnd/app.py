from flask import Flask, jsonify
from flask_cors import CORS
import sqlite3

app = Flask(__name__)
CORS(app)  # Allow requests from any origin

# Path to your SQLite database
DATABASE = "DB/db_tracker.sqlite3"

def get_table_data(table):
    conn = sqlite3.connect(DATABASE)
    conn.row_factory = sqlite3.Row  # Make rows dict-like
    cursor = conn.cursor()
    cursor.execute(f'''
        SELECT * FROM {table}
    ''')
    rows = cursor.fetchall()
    conn.close()
    return [dict(row) for row in rows]

@app.route("/api/credit")
def credit():
    return jsonify(get_table_data(table="credit"))

@app.route("/api/debit")
def debit():
    return jsonify(get_table_data(table="debit"))

@app.route("/api/categories")
def categories():
    return jsonify(get_table_data(table="categories"))

if __name__ == "__main__":
    app.run(debug=True)
