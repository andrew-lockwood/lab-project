# Simple iterator that goes over every full text article in the database 
# Uses the same parsing as the unlabled sentence iterator

import sqlite3
import re
from context import settings

conn = sqlite3.connect(settings.db)
curr = conn.cursor()


class Documents:
    def __init__(self):
        q = (" SELECT  articleID, txt \n"
             " FROM    articleTXT      \n"
             " WHERE   articleID IN (SELECT DISTINCT(articleID) \n"
             "                       FROM   OriginalKeywords)  ")

        curr.execute(q)
        self.articles = curr.fetchall()

    def __iter__(self):
        for article in self.articles:
            parsed_article = re.sub('[^a-z ]', '', article[1].lower())
            title = article[0]

            yield (title, parsed_article)
