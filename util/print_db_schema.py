
import sqlite3
import sys

from context import settings 


def get_tables():
    y = curr.execute("""SELECT 	name 
    					FROM 	sqlite_master 
    					WHERE 	type='table'""")

    table_names = list(map(lambda x: x[0], y))

    return table_names


def get_columns(table_name):
    # Pragma table data stored as
    # (id, name, type, notnull, default_value, primary_key)
    y = curr.execute('PRAGMA TABLE_INFO({})'.format(table_name))

    # Grab the name of each column
    column_names = [tup[1] for tup in curr.fetchall()]

    return column_names


def print_schema():
    print("Tables".ljust(20) + "| Attributes ")
    print("--------------------|----------------------------------")
    for table in get_tables():
        print(table.ljust(20) + "| "+", ".join(get_columns(table)))


if __name__ == "__main__":
    conn = sqlite3.connect(settings.db)
    curr = conn.cursor()

    print_schema()
