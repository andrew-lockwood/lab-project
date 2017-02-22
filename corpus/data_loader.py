from context import settings
import pickle
import gensim.models
from random import shuffle, sample
import sqlite3
import numpy as np 

class DataLoader():
    def __init__(self, n):
        self.n = n
        self.conn = sqlite3.connect(settings.db)
        self.curr = self.conn.cursor()

        q = """ SELECT  DISTINCT(articleID)
                FROM    OriginalKeywords 
                WHERE   keyword IN
                       (SELECT  keyword
                        FROM    OriginalKeywords 
                        GROUP BY keyword 
                        HAVING count(articleID) > {n})""".format(n=n)

        self.valid_articles = set()
        self.curr.execute(q)

        for article in self.curr.fetchall():
            self.valid_articles.add(article[0])

    def analyze(self, kwd):
        """Fetches original author assigned keywords."""
        q = """ SELECT  articleID
                FROM    OriginalKeywords
                WHERE   keyword='{k}'       """.format(k=kwd)

        positive_title_set = set([t[0] for t in self.curr.execute(q).fetchall()])

        negative_title_set = sample(self.valid_articles.difference(positive_title_set), 
                                    len(positive_title_set))

        p = [(t, "1") for t in positive_title_set]
        n = [(t, "0") for t in negative_title_set]
        self.data = p + n
        shuffle(self.data)

    def get_title_dict(self):
        return self.data

    def load_text(self): 
        q = """ SELECT  articleID, txt 
                FROM    articleTXT
                WHERE   articleID IN
                       (SELECT  DISTINCT(articleID)
                        FROM    OriginalKeywords 
                        WHERE   keyword IN
                               (SELECT  keyword
                                FROM    OriginalKeywords 
                                GROUP BY keyword 
                                HAVING count(articleID) > {n}))""".format(n=self.n)

        self.curr.execute(q)

        return {i:t for i, t in self.curr.fetchall()}


    def get_keywords(self):
        q = """ SELECT  keyword
                FROM    OriginalKeywords 
                GROUP BY keyword 
                HAVING count(articleID) > {n}""".format(n=self.n)

        self.curr.execute(q)

        kwds = [k[0] for k in self.curr.fetchall()]

        return kwds


    def num_titles(self):
        return len(self.data)
