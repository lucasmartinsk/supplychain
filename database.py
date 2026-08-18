import sqlite3
import pandas as pd

DB_NAME = "tprm_database.db"

def save_excel_table(df, table_name):
    """Saves or replaces the table data from the uploaded dataframe."""
    conn = sqlite3.connect(DB_NAME)
    df.to_sql(table_name, conn, if_exists='replace', index=False)
    conn.close()

def load_data(table_name):
    """Loads a table from the SQLite database into a pandas DataFrame."""
    try:
        conn = sqlite3.connect(DB_NAME)
        df = pd.read_sql(f"SELECT * FROM {table_name}", conn)
        conn.close()
        return df
    except Exception:
        return pd.DataFrame()
