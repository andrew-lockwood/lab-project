from sklearn.preprocessing import MultiLabelBinarizer
from sklearn.naive_bayes import BernoulliNB, GaussianNB

from sklearn.multiclass import OneVsRestClassifier

import gensim.models

import os
import random
import settings
import sqlite3
import numpy as np
import io
from timers import time_this


def random_titles(n, m=None):
    """Selects n titles at random.

    Returns a set of (title, kwds) tuples where the kwds 
    are delimited by commas
    Refining q can make the set more restrictive (such as only 
    using articles with a keyword that shows up x amount of times)

    Attributes:
        n: number of test keywords 
        m: numer of training keywords

    As a general rule, m >>> n 
    """
    q = """ SELECT articleID, group_concat(redirect) kwd
            FROM OriginalKeywords NATURAL JOIN KeywordForms
            WHERE redirect IN
            (SELECT  redirect
            FROM OriginalKeywords NATURAL JOIN KeywordForms
            GROUP BY redirect
            HAVING count(articleID) >= 10)
            AND redirect != 'NULL'
            GROUP BY articleID"""

    titles = curr.execute(q).fetchall()


    test_titles = set()
    for i in range(n):
        r = random.randint(0, len(titles) - 1)
        title = titles[r]
        titles.remove(title)
        # Ignore keywords in the training set (since thats what 
        # we are trying to predict)
        test_titles.add(title[0])


    train_titles = set()
    # Take the complement of the test set if m is None
    if m == None:
        m = len(titles)
    for i in range(m):
        r = random.randint(0, len(titles) - 1)
        title = titles[r]
        titles.remove(title)
        train_titles.add(title)

    return(test_titles, train_titles)



@time_this
def load_vectors():
    mlb = MultiLabelBinarizer()

    titleset = random_titles(2, 2)
    classif = OneVsRestClassifier(GaussianNB())

    n = 2002
    m = 2
    curr.execute("""SELECT  * 
                    FROM    ArticleVectors 
                    ORDER BY RANDOM() 
                    LIMIT {n}""".format(n=n))

    train = curr.fetchall()
    test = []

    for i in range(m):
        r = random.randint(0, len(train) - 1)
        title = train[r]
        train.remove(title)
        test.append(title)

    test_vecs = np.array([x[1] for x in test])
    train_vecs = np.array([x[1] for x in train])
    train_ids = [x[0] for x in train]
    train_kwds = []

    while train_ids: 
        curr.execute("""SELECT  group_concat(keyword) kwds
                        FROM    OriginalKeywords
                        GROUP BY articleID 
                        """% ','.join('?'*len(train_ids[:500])), train_ids[:500])
        for kwds in curr.fetchall():
            train_kwds.append(kwds[0].split(','))
        del train_ids[:500]

    t = mlb.fit_transform(train_kwds)
    print(len(t))
    #classif.fit(train_vecs, mlb.fit_transform(train_kwds))


@time_this
def test_model():
    model = gensim.models.doc2vec.Doc2Vec.load(settings.model)

    titleset = random_titles(2, 2000)

    mlb = MultiLabelBinarizer()
    classif = OneVsRestClassifier(GaussianNB())

    test_vecs = np.array([model.docvecs[title] for title in titleset[0]])
    train_vecs = np.array([model.docvecs[t] for t, k in titleset[1]])
    train_kwds = [k.split(',') for t, k in titleset[1]]

    targets = mlb.fit_transform(train_kwds)
    classif.fit(train_vecs, mlb.fit_transform(train_kwds))

    for kwds in mlb.inverse_transform(classif.predict(test_vecs)):
        print(kwds)

    for title in titleset[0]:
        q = """ SELECT title 
                FROM ArticleInformation 
                WHERE articleID='{id}'""".format(id=title)

        curr.execute(q)
        print(curr.fetchall()[0][0])

if __name__ == "__main__":
    def adapt_array(arr):
        out = io.BytesIO()
        np.save(out, arr)
        out.seek(0)
        return sqlite3.Binary(out.read())

    def convert_array(text):
        out = io.BytesIO(text)
        out.seek(0)
        return np.load(out)

    sqlite3.register_adapter(np.ndarray, adapt_array)
    sqlite3.register_converter("NUMPY", convert_array)

    conn = sqlite3.connect(settings.db, 
                detect_types=sqlite3.PARSE_DECLTYPES)

    curr = conn.cursor()
    #load_vectors()
    test_model()
    #test()