import pandas as pd
import sqlite3
from pathlib import Path

def excel_to_db(excel_file, db_file, table_name):
    # Read the Excel file
    df = pd.read_excel(excel_file)

    # Connect to the SQLite database
    conn = sqlite3.connect(db_file)
    cursor = conn.cursor()

    # Create the table if it doesn't exist
    columns = ', '.join([f"{col} TEXT" for col in df.columns])
    cursor.execute(f"CREATE TABLE IF NOT EXISTS {table_name} ({columns})")

    # Insert the data into the table
    for _, row in df.iterrows():
        placeholders = ', '.join(['?' for _ in row])
        cursor.execute(f"INSERT INTO {table_name} VALUES ({placeholders})", tuple(row))

    # Commit the changes and close the connection
    conn.commit()
    conn.close()

    print(f"Data from {excel_file} has been successfully imported into {table_name} table in {db_file}.")

def main():
    excel_file = input("Enter the path to your Excel file: ")
    db_file = input("Enter the path to your SQLite database file (dictionary.db): ") or "dictionary.db"
    table_name = input("Enter the name of the table to import data into (dictionary): ") or "dictionary"

    if not Path(excel_file).is_file():
        print(f"Error: The file {excel_file} does not exist.")
        return

    try:
        excel_to_db(excel_file, db_file, table_name)
    except Exception as e:
        print(f"An error occurred: {str(e)}")

if __name__ == "__main__":
    main()