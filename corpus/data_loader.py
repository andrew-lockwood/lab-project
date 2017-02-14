from context import settings 

import gensim.models
from random import shuffle
import sqlite3

class DataLoader():
    def __init__(self):
        self.conn = sqlite3.connect(settings.db)
        self.curr = self.conn.cursor()

        self.datatype = None
        self.data = []

    def analyze(self, kwd):
        """Fetches original author assigned keywords."""
        q = """ SELECT  articleID
                FROM    OriginalKeywords
                WHERE   keyword='{k}'       """.format(k=kwd)

        self.data.extend([(t[0],'1') for t in self.curr.execute(q).fetchall()])

        q = """ SELECT  DISTINCT(articleID)
                FROM    OriginalKeywords
                WHERE   articleID NOT IN
                       (SELECT  articleID
                        FROM    OriginalKeywords
                        WHERE   keyword = '{k}')
                ORDER BY RANDOM() LIMIT {n}""".format(k=kwd,n=len(self.data))

        self.data.extend([(t[0],'0') for t in self.curr.execute(q).fetchall()])

        shuffle(self.data)

    def num_titles(self):
        return len(self.data)

    def set_type(self, datatype):
        self.datatype = datatype

    def get_type(self):
        return self.datatype

    def __iter__(self):
        if len(self.data) == 0: 
            raise NotImplementedError("initialize data by calling a DataLoader class method")

        # Return titles
        elif self.datatype == None:
            for t in self.data:
                yield t

        # Return full text
        elif self.datatype == "text":
            for title, label in self.data: 
                q = """ SELECT  txt
                        FROM    ArticleTXT
                        WHERE   articleID='{id}'       """.format(id=title)

                text = self.curr.execute(q).fetchall()[0][0]
                yield (text, label)

        # Return document vectors 
        elif self.datatype == "vectors":
            model = gensim.models.Word2Vec.load(settings.model)
            for title, label in self.data: 
                try:
                    vector = model.docvecs[title[0:16]]
                    yield(vector, label) 
                except KeyError as e:
                    print(title[0:16])

