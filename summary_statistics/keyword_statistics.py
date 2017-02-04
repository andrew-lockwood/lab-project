import sqlite3 
from context import settings

import matplotlib.pyplot as plt


def keyword_grams():
    q = """ SELECT  DISTINCT(keyword)
            FROM    OriginalKeywords    """

    curr.execute(q)

    keywords = [k[0] for k in curr.fetchall()]

    print(keywords)



if __name__ == "__main__":
    conn = sqlite3.connect(settings.db)
    curr = conn.cursor()
    keyword_grams()