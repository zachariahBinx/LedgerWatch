import os
import sys
from pathlib import Path
import pandas as pd

for i in range(2):
    sys.path.append(
        str(Path(__file__).resolve().parents[i])
    )

from db_manage import DatabaseManager
from utils.settings import Settings

CREDIT_FOLDER_PATH = "../test_data/credit_history_csv"
DEBIT_FOLDER_PATH = "../test_data/debit_history_csv"

def get_most_recent_csv(folder_path: str) -> str:
    files = list(Path(folder_path).rglob("*.csv"))
    if not files:
        raise FileNotFoundError(f"No CSV files found in {folder_path}")
    newest_file = max(files, key=os.path.getctime)
    return newest_file

def main():
    db = DatabaseManager("db_tracker.sqlite3")
    conn = db.connection

    # Load data
    latest_credit_path = get_most_recent_csv(CREDIT_FOLDER_PATH)
    latest_debit_path = get_most_recent_csv(DEBIT_FOLDER_PATH)
    df_credit = pd.read_csv(latest_credit_path, usecols=Settings.DATA_COLS)
    df_debit = pd.read_csv(latest_debit_path, usecols=Settings.DATA_COLS)

    # Update date col to date type
    df_credit["Post Date"] = pd.to_datetime(df_credit["Post Date"], errors="coerce")
    df_debit["Post Date"] = pd.to_datetime(df_debit["Post Date"], errors="coerce")
    invalid_rows_credit = df_credit[df_credit["Post Date"].isna()]
    invalid_rows_debit = df_debit[df_debit["Post Date"].isna()]
    if not invalid_rows_credit.empty:
        raise ValueError(f"Credit has invalid dates: {invalid_rows_credit}")
    if not invalid_rows_debit.empty:
        raise ValueError(f"Debit has invalid dates: {invalid_rows_credit}")

    # Add data to db
    db.upsert_account_data(account="credit", df=df_credit)
    db.upsert_account_data(account="debit", df=df_debit)


if __name__ == "__main__":
    main()
