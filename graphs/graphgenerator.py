

import sys
sys.path.insert(0, "C:\\Users\\Andrew\\lab-project\\data")
import matplotlib.pyplot as plt
from dbinterface import DatabaseInterface

di = DatabaseInterface("C:\\Users\\Andrew\\lab-project\\data\\frontiers_corpus.db")

def wordvsline():
    q = "SELECT wordcount, linecount FROM ArticleTXT"
    x,y = zip(*di.execute_query(q))

    plt.scatter(x,y)
    plt.xlim(0,)
    plt.ylim(0,)

    plt.show()



def count_between(start, end):
    q = """ SELECT  count(articleID) 
            FROM    ArticleInformation
            WHERE   date BETWEEN
            '{s}' AND '{e}'""".format(s=start, e=end)

    print (di.execute_query(q)[0][0])

count_between('2010-00-00', '2010-99-99')
count_between('2011-00-00', '2011-99-99')
count_between('2012-00-00', '2012-99-99')
count_between('2013-00-00', '2013-99-99')
