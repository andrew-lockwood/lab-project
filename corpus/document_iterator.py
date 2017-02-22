from context import settings
import sqlite3
import re

class Documents():
    def __init__(self, n):
        conn = sqlite3.connect(settings.db)
        curr = conn.cursor()

        q = """ SELECT  articleID, txt
                FROM    articleTXT     
                WHERE   articleID IN 
                       (SELECT  DISTINCT(articleID)
                        FROM    OriginalKeywords 
                        WHERE   keyword IN
                               (SELECT  keyword
                                FROM    OriginalKeywords 
                                GROUP BY keyword 
                                HAVING count(articleID) > {n}))""".format(n=n)

        curr.execute(q)
        self.articles = curr.fetchall()

    def __iter__(self):
        for article in self.articles:
            parsed_article = re.sub('[^a-z ]', '', article[1].lower())
            title = article[0]

            yield (title, parsed_article)

if __name__ == '__main__':
    pass
