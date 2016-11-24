
from data.dbinterface import DatabaseInterface
import numpy as np
from scipy import stats

di = DatabaseInterface("data/frontiers_corpus")


def total_articles():
    q1 = "SELECT count(DISTINCT articleID) FROM ArticleInformation"
    print (di.execute_query(q1)[0][0])

    q2 = "SELECT count(DISTINCT articleID) FROM OriginalKeywords"

    print (di.execute_query(q2)[0][0])


    q3 = "SELECT count(DISTINCT type) FROM ArticleInformation"
    print (di.execute_query(q3))


q = """ SELECT      type, count(articleID)
        FROM        ArticleInformation
        WHERE       articleID NOT IN 
                    (SELECT DISTINCT articleID
                    FROM OriginalKeywords)
        GROUP BY    type"""

print (di.execute_query(q))



'''x = []
for count in di.execute_query(q): 
    x.append(count[0])

y = np.array(x)
print(stats.describe(y))'''


