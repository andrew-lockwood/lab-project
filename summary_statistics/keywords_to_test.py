from context import settings

import sqlite3
import sys


class Papers(): 
    def __init__(self, n): 
        conn = sqlite3.connect(settings.db)
        curr = conn.cursor()

        q = """ SELECT  DISTINCT(articleID)
                FROM    OriginalKeywords 
                WHERE   keyword IN
                       (SELECT keyword
                        FROM OriginalKeywords 
                        GROUP BY keyword 
                        HAVING count(articleID) > {n})""".format(n=n)

        curr.execute(q)
        
        self.titles = []

        for title in curr.fetchall():
            self.titles.append(title[0])

    def get_valid_papers(self):
        return self.titles

def main(n):
    conn = sqlite3.connect(settings.db)
    curr = conn.cursor()

    q = """ SELECT  DISTINCT(keyword)
            FROM    OriginalKeywords 
            GROUP BY keyword HAVING count(articleID) > {n}""".format(n=n)

    curr.execute(q)

    kwds = []

    c = 0
    for t in curr.fetchall():
        c += 1
        kwds.append(t[0])

    print("Number of keywords: " + str(c))
    print("---------------------------------")
    print(", ".join(kwds))
    print("---------------------------------")


    q = """ SELECT  DISTINCT(articleID)
            FROM    OriginalKeywords 
            WHERE   keyword IN
                   (SELECT keyword
                    FROM OriginalKeywords 
                    GROUP BY keyword HAVING count(articleID) > {n})""".format(n=n)

    curr.execute(q)
    c = 0
    for t in curr.fetchall():
        c += 1

    print("Number of papers: " + str(c))


if __name__ == '__main__':
    main(sys.argv[1])
