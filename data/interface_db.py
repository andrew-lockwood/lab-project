import sqlite3
from tabulate import tabulate
import settings 


def schema():
    q = """ SELECT  name 
            FROM    sqlite_master 
            WHERE   type = 'table'"""

    tables = list(map(lambda x: x[0], curr.execute(q)))

    for table in tables:
        print("\n%s:" % table)
        curr.execute('PRAGMA TABLE_INFO({})'.format(table))
        columns = [(x[1], x[2]) for x in curr.fetchall()]
        print(tabulate(columns, headers=['name', 'type']))


if __name__ == "__main__":
    conn = sqlite3.connect(settings.db)
    curr = conn.cursor()
    schema()
