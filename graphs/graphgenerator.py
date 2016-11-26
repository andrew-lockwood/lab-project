

import sys
sys.path.insert(0, "C:\\Users\\Andrew\\lab-project\\data")
import matplotlib.pyplot as plt
from dbinterface import DatabaseInterface
import re
di = DatabaseInterface("C:\\Users\\Andrew\\lab-project\\data\\frontiers_corpus.db")

def wordvsline():
    q = "SELECT wordcount, linecount FROM ArticleTXT"
    x,y = zip(*di.execute_query(q))

    plt.scatter(x,y)
    plt.xlim(0,)
    plt.ylim(0,)

    plt.show()



def titles_between(start, end):
    q = """ SELECT  DISTINCT articleID
            FROM    ArticleInformation
            WHERE   date BETWEEN
            '{s}' AND '{e}'""".format(s=start, e=end)

    return di.execute_query(q)


def by_year():
    q = """ SELECT      strftime('%Y', date), count(articleID)
            FROM        ArticleInformation
            GROUP BY    strftime('%Y', date)"""

    return di.execute_query(q)

def by_month():
    q = """ SELECT      strftime('%Y-%m', date), count(articleID)
            FROM        ArticleInformation
            GROUP BY    strftime('%Y-%m', date)"""

    return di.execute_query(q)

def by_quarter():
    q = """ SELECT      strftime('%Y', date), 
                CASE 
                    WHEN cast(strftime('%m', date) as integer) BETWEEN 1 AND 3 THEN 1
                    WHEN cast(strftime('%m', date) as integer) BETWEEN 4 AND 6 THEN 2
                    WHEN cast(strftime('%m', date) as integer) BETWEEN 7 AND 9 THEN 3
                    ELSE 4
                END AS Quarter, count(articleID)
            FROM        ArticleInformation
            GROUP BY    strftime('%Y', date),
                CASE 
                    WHEN cast(strftime('%m', date) as integer) BETWEEN 1 AND 3 THEN 1
                    WHEN cast(strftime('%m', date) as integer) BETWEEN 4 AND 6 THEN 2
                    WHEN cast(strftime('%m', date) as integer) BETWEEN 7 AND 9 THEN 3
                    ELSE 4
                END"""

    return di.execute_query(q)

def graph(value):
    data = []

    if value == 'year':
        for year, count in by_year():
            data.append((year, count))

    if value == 'month':
        for year, count in by_month():
            data.append((year, count))

    if value == 'quarter':
        for year, quarter, count in by_quarter():
            d = "%s%s"%(year,'q'+str(quarter))
            data.append((d, count))

    x = [i for i in range(len(data))]

    labels,y = zip(*data)

    mpl_fig = plt.figure()
    ax = mpl_fig.add_subplot(111)

    plt.margins(0.025, 0)

    plt.bar(x, y, align='center')
    ax.set_ylabel('Articles Recieved')
    plt.xticks(x, labels, rotation=45)
    plt.show()

