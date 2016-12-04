

from sklearn.preprocessing import MultiLabelBinarizer
from sklearn.naive_bayes import BernoulliNB, GaussianNB

from sklearn.multiclass import OneVsRestClassifier
import gensim.models
import sqlite3
import numpy as np

import sys
from tabulate import tabulate

di = DatabaseInterface("C:\\Users\\Andrew\\lab-project\\data\\frontiers_corpus.db")

def get_titles(key, total):
    q = """ SELECT      DISTINCT articleID
            FROM        KeywordForms NATURAL JOIN OriginalKeywords
            WHERE       {k} IN
           (SELECT      {k}
            FROM        KeywordForms NATURAL JOIN OriginalKeywords
            GROUP BY    {k}
            HAVING      count(articleID) >= {t})
            AND         {k} != 'NULL'""".format(k=key, t=total)

    return di.execute_query(q)

def graph():
    di.print_schema()

    totals = [i*10 for i in range(26)]
    x = [i for i in range(26)]

    keys = ['keyword', 'parse', 'redirect', 'stem']

    table = []
    for key in keys:
        row = []
        for total in totals:
            row.append(get_titles(key, total))
        table.append(row)

    import matplotlib.pyplot as plt 

    plt.plot(x, table[0])
    plt.plot(x, table[1])
    plt.plot(x, table[2])
    plt.plot(x, table[3])

    plt.legend(keys, loc='lower left')
    plt.xticks(x, totals)


    plt.show()


from collections import Counter


def binned():
    q = """ SELECT      {k}, count(articleID)
            FROM        KeywordForms NATURAL JOIN OriginalKeywords
            WHERE       {k} != 'NULL'
            GROUP BY    {k}""".format(k='stem')

    c = Counter()
    for k, count in di.execute_query(q):
        c[int(count/10)] += 1

    print (c)

def run():
    classif = OneVsRestClassifier(GaussianNB())
    mlb = MultiLabelBinarizer()

    text = []
    targets = []
    
    q2 = """SELECT      txt, kwds
            FROM 
           (SELECT      articleID, group_concat({k}) kwds
            FROM        KeywordForms NATURAL JOIN OriginalKeywords
            WHERE       {k} IN
           (SELECT      {k}
            FROM        KeywordForms NATURAL JOIN OriginalKeywords
            GROUP BY    {k}
            HAVING      count(articleID) >= {t})
            AND         {k} != 'NULL'
            GROUP BY    articleID) a, ArticleTXT b
            WHERE       a.articleID = b.articleID""".format(k='redirect', t=200)

    for txt, kwds in di.execute_query(q2):
        text.append(txt)
        targets.append(kwds.split(','))

    t = mlb.fit_transform(targets)
    classif.fit(text, t)
    #print (di.execute_query(q2))

    #print(di.execute_query(q2))


if __name__ == "__main__":
    conn = sqlite3.connect(settings.db)
    curr = conn.cursor()
    schema()
