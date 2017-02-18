# Simple iterator that goes over every full text article in the database 
# Uses the same parsing as the unlabled sentence iterator
import sqlite3
import re

# Settings tells Documents where the database is located
from context import settings

conn = sqlite3.connect(settings.db)
curr = conn.cursor()


class Documents:
    def __init__(self, n):
        q = """ SELECT  articleID, txt
                FROM    articleTXT     
                WHERE   articleID IN 
                       (SELECT  DISTINCT(articleID)
                        FROM    OriginalKeywords 
                        WHERE   keyword IN
                               (SELECT  keyword
                                FROM    OriginalKeywords 
                                GROUP BY keyword 
                                HAVING count(articleID) > {n})""".format(n=n)

        curr.execute(q)
        self.articles = curr.fetchall()

    def __iter__(self):
        for article in self.articles:
            parsed_article = re.sub('[^a-z ]', '', article[1].lower())
            title = article[0]

            yield (title, parsed_article)
