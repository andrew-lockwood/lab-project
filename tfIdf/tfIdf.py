
from sklearn.feature_extraction.text import TfidfVectorizer 
from sklearn.decomposition import NMF, LatentDirichletAllocation
from time import time
import settings
import sqlite3
import os
import sys
import random

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
            HAVING count(articleID) >= 5)
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

    return test_titles

def print_top_words(model, feature_names, n_top_words):
    for topic_idx, topic in enumerate(model.components_):
        print("topic #%d: " % topic_idx)
        print(" ".join([feature_names[i]
                        for i in topic.argsort()[:-n_top_words - 1: -1]]))
    print()

def run(n):
    curr.execute("""SELECT  txt 
                    FROM    ArticleTXT 
                    ORDER BY RANDOM() 
                    LIMIT {n}""".format(n=n))

    train = curr.fetchall()
    #print(train)
    train_data = []
    for t in train:
        train_data.append(t[0])

    vectorizer = TfidfVectorizer(max_df=0.95, min_df=2,
                                max_features=1000,
                                stop_words='english')
    t0 = time()

    tfidf = vectorizer.fit_transform(train_data)

    features = vectorizer.get_feature_names()

    print("done in %0.3fs. " % (time() - t0))

    nmf = NMF(n_components=10, random_state=1,
                alpha=0.1, l1_ratio=0.5).fit(tfidf)

    print_top_words(nmf, features, 10)

if __name__ == "__main__":
    conn = sqlite3.connect(settings.db, 
                detect_types=sqlite3.PARSE_DECLTYPES)

    curr = conn.cursor()
    #print(random_titles(4))
    run(10)