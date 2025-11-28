import os
import sys
from pathlib import Path
import pandas as pd

for i in range(2):
    sys.path.append(
        str(Path(__file__).resolve().parents[i])
    )

from DB.db_manage import DatabaseManager
from utils.settings import Settings

CREDIT_FOLDER_PATH = "test_data/credit_history_csv"
DEBIT_FOLDER_PATH = "test_data/debit_history_csv"


def main():
    db = DatabaseManager("DB/db_tracker.sqlite3")
    conn = db.connection

    # Find files
    credit_csvs = Path(CREDIT_FOLDER_PATH).rglob("*.csv")
    debit_csvs = Path(DEBIT_FOLDER_PATH).rglob("*.csv")

    # Load data
    dfs_credit = [pd.read_csv(f, usecols=Settings.DATA_COLS) for f in credit_csvs]
    dfs_debit = [pd.read_csv(f, usecols=Settings.DATA_COLS) for f in debit_csvs]
    db_debit_data = [pd.read_sql("SELECT * FROM debit", conn)]
    db_credit_data = [pd.read_sql("SELECT * FROM credit", conn)]
    db_cat_data = pd.read_sql("SELECT * FROM categories", conn)

    # Append data and drop duplicates-(don't use categories column)
    df_credit = pd.concat(dfs_credit + db_credit_data, ignore_index=True).drop_duplicates(subset=Settings.DATA_COLS).reset_index(drop=True)
    df_debit =  pd.concat(dfs_debit + db_debit_data, ignore_index=True).drop_duplicates(subset=Settings.DATA_COLS).reset_index(drop=True)

    # Update date col to date type
    df_credit["Post Date"] = pd.to_datetime(df_credit["Post Date"], errors="coerce")
    df_debit["Post Date"] = pd.to_datetime(df_debit["Post Date"], errors="coerce")
    invalid_rows_credit = df_credit[df_credit["Post Date"].isna()]
    invalid_rows_debit = df_debit[df_debit["Post Date"].isna()]
    if not invalid_rows_credit.empty:
        print("credit has invalid date")
        print(invalid_rows_credit)
    if not invalid_rows_debit.empty:
        print("debit has invalid date")
        print(invalid_rows_debit)

    # Add data to db
    db.insert_account_data("credit", df_credit)
    db.insert_account_data("debit", df_debit)

    # # Group
    # df_credit_group = df_credit.groupby(df_credit['Post Date'].dt.month)
    # for _, credit_groups in df_credit_group:
    #     print(credit_groups)


if __name__ == "__main__":
    main()
