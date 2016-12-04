from data.dbinterface import DatabaseInterface
from tabulate import tabulate
from operator import itemgetter
from collections import Counter
import sqlite3
db = "C:\\Users\\Andrew\\lab-project\\data\\frontiers_corpus.db"


def type_table():
    """Creates a table of type data.

    Query creates two temporary tables, one containing all type data from the 
    article information table, the other removing any type data that doesn't 
    appear in the keyword assignment table. 
    """
    q = """ SELECT  a.type, a.ac, b.ac, b.ac - a.ac,  
                    100 * (CAST((b.ac - a.ac) AS REAL) / b.ac)
            FROM
               (SELECT      type, count(DISTINCT articleID) ac
                FROM        ArticleInformation NATURAL JOIN OriginalKeywords
                GROUP BY    type) a, 
               (SELECT      type, count(DISTINCT articleID) ac
                FROM        ArticleInformation
                GROUP BY    type) b
            WHERE a.type = b.type"""

    data = di.execute_query(q)
    data = sorted(data, key=itemgetter(1), reverse=True)

    h = ("type", "articles w/ kwds", "total articles", "diff", "% total")

    print(tabulate(data, headers=h, floatfmt=".2f"))


def total_table():
    q = """ SELECT a.c, b.c, 100* CAST(b.c AS REAL) / a.c
            FROM 
                (SELECT     count(DISTINCT articleID) c
                FROM        ArticleInformation) a,
                (SELECT     count(DISTINCT articleID) c
                FROM        OriginalKeywords) b"""

    h = ("total", "total w/ kwds", "% w/ kwds")

    data = di.execute_query(q)

    print(tabulate(data, headers=h, floatfmt=".2f"))

def kwd_frequency():
    c1 = Counter()
    c2 = Counter()
    q = """ SELECT  keyword, count(articleID)
            FROM    OriginalKeywords
            GROUP BY keyword"""

    data = curr.execute(q)

    for kwd, count in data.fetchall():
        c1[int(count/10)] += 1
        if count < 10:
            c2[int(count)] += 1

if __name__ == "__main__":
    conn = sqlite3.connect(db)
    curr = conn.cursor()
    kwd_frequency()
