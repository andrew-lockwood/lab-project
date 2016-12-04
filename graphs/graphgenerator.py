
import sqlite3
import matplotlib.pyplot as plt
import re
from collections import Counter
db = "C:\\Users\\Andrew\\lab-project\\data\\frontiers_corpus.db"

def wordvsline():
    q = "SELECT wordcount, linecount FROM ArticleTXT"
    curr.execute(q)
    x,y = zip(*curr.fetchall())

    mpl_fig = plt.figure()
    ax = mpl_fig.add_subplot(111)

    plt.scatter(x,y)
    plt.xlim(0,25000)
    plt.ylim(0,450)
    ax.set_xlabel('Word Count')
    ax.set_ylabel('Line Count')
    ax.set_title('Words vs Lines')
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



def kwd_frequency():
    c1 = Counter()
    c2 = Counter()
    q = """ SELECT  keyword, count(articleID)
            FROM    OriginalKeywords 
            GROUP BY keyword"""

    data = curr.execute(q)

    n = 10
    for kwd, count in data.fetchall():
        if count < 20:
            c2[int(count)] += 1
        else:
            c1[int(count/n)] += 1


    x = [i for i in range(len(c1))]

    labels,y = zip(*c1.items())

    labels = ["%s-%s"%(l*n, l*n+n) for l in labels]

    mpl_fig = plt.figure()
    ax = mpl_fig.add_subplot(111)

    plt.margins(0.025, 0)

    plt.bar(x, y, align='center')
    plt.xticks(x, labels, rotation=90)
    plt.show()


    x = [i for i in range(len(c2))]

    labels,y = zip(*c2.items())

    mpl_fig = plt.figure()
    ax = mpl_fig.add_subplot(111)

    plt.margins(0.025, 0)

    plt.bar(x, y, align='center')
    plt.xticks(x, labels, rotation=90)
    plt.show()




if __name__ == "__main__":
    conn = sqlite3.connect(db)
    curr = conn.cursor()
    kwd_frequency()
