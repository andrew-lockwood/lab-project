# Simple iterator that goes over every full text article in
# the database 
import sqlite3

from context import settings
conn = sqlite3.connect(settings.db)
curr = conn.cursor()


class RawDocuments:

    def __init__(self):
        q = """ SELECT  articleID, txt 
                FROM    articleTXT      
                ORDER BY RANDOM() LIMIT 4"""  # Set for testing

        curr.execute(q)

        self.articles = curr.fetchall()

    def __iter__(self):
        for article in self.articles:
            yield article[1]
