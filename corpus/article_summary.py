
import sys

from context import settings
import sqlite3

conn = sqlite3.connect(settings.db)
curr = conn.cursor()




if __name__ == '__main__':
    for title in sys.argv[1:]:
        print("------------------------------------")
        get_title(title)
        get_keywords(title)