import matplotlib.pyplot as plt
from collections import Counter
import sqlite3 

from context import settings

def graph2():

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


def graph():
    # Find size of keywords that were NOT redirected
    q = """ SELECT  keyword 
            FROM    KeywordForms
            WHERE   redirect != 'NULL' """

    nullredirects = []
    for kwd in curr.execute(q).fetchall():
        nullredirects.append(
                ''.join([i if ord(i) < 128 else ' ' 
                for i in kwd[0]]))

    redirectNGrams = Counter() 
    for kwd in nullredirects:
        redirectNGrams[len(kwd.split())] += 1

    # Find size of every keyword 
    q = """ SELECT  keyword 
            FROM    KeywordForms    """

    originalkwds = []
    for kwd in curr.execute(q).fetchall():
        originalkwds.append(
                ''.join([i if ord(i) < 128 else ' ' 
                for i in kwd[0]]))

    originalNGrams = Counter() 
    for kwd in originalkwds:
        originalNGrams[len(kwd.split())] += 1


    x1 = [i+1 for i in range(9)]
    x2 = [i+0.8 for i in range(9)]
    y = []
    z = []

    for count in x1:
        y.append(redirectNGrams[count])
        z.append(originalNGrams[count])

    ax = plt.subplot(111)
    # Z is every keyword
    ax.bar(x1, z, width=0.2, color='r',align='center')
    # Y is every sucessfully redirect keyword 
    ax.bar(x2, y, width=0.2, color='b',align='center')

    plt.xticks(x1)

    plt.show()


if __name__ == "__main__":
    conn = sqlite3.connect(settings.db)
    curr = conn.cursor()
    graph()
    #redirect_analysis()
    #keyword_analysis()

