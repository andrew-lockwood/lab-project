
import sqlite3
import gensim.models
import numpy as np

from sklearn.cross_validation import KFold
from sklearn.metrics import confusion_matrix, f1_score
from sklearn.naive_bayes import GaussianNB

from random import shuffle

from context import settings 

import sys



conn = sqlite3.connect(settings.db)
curr = conn.cursor()
model = gensim.models.Word2Vec.load(settings.model)

display = False


def get_original_data(kwd, scale=1):
    """Fetches original author assigned keywords."""
    data = []
    q = """ SELECT  articleID
            FROM    OriginalKeywords
            WHERE   keyword='{k}'       """.format(k=kwd)

    data.extend([(t[0],'1') for t in curr.execute(q).fetchall()])
    pos_count = len(data)

    q = """ SELECT  DISTINCT(articleID)
            FROM    OriginalKeywords
            WHERE   articleID NOT IN
                   (SELECT  articleID
                    FROM    OriginalKeywords
                    WHERE   keyword = '{k}')
            ORDER BY RANDOM() LIMIT {n}""".format(k=kwd,n=pos_count)

    data.extend([(t[0],'0') for t in curr.execute(q).fetchall()])
    neg_count = len(data) - pos_count

    shuffle(data)
    return data


def get_redirect_data(kwd, scale=1):
    data = []
    q = """ SELECT  articleID
            FROM    OriginalKeywords NATURAL JOIN KeywordForms
            WHERE   redirect='{k}'       """.format(k=kwd)

    data.extend([(t[0],'1') for t in curr.execute(q).fetchall()])
    pos_count = len(data)

    q = """ SELECT  DISTINCT(articleID)
            FROM    OriginalKeywords NATURAL JOIN KeywordForms
            WHERE   articleID NOT IN
                   (SELECT  articleID
                    FROM    OriginalKeywords NATURAL JOIN KeywordForms
                    WHERE   redirect='{k}')
            ORDER BY RANDOM() LIMIT {n}""".format(k=kwd,n=pos_count)

    data.extend([(t[0],'0') for t in curr.execute(q).fetchall()])
    neg_count = len(data) - pos_count

    shuffle(data)
    return data


def get_stem_data(kwd, scale=1):
    data = []
    q = """ SELECT  articleID
            FROM    OriginalKeywords NATURAL JOIN KeywordForms
            WHERE   stem='{k}'       """.format(k=kwd)

    data.extend([(t[0],'1') for t in curr.execute(q).fetchall()])
    pos_count = len(data)

    q = """ SELECT  DISTINCT(articleID)
            FROM    OriginalKeywords NATURAL JOIN KeywordForms
            WHERE   articleID NOT IN
                   (SELECT  articleID
                    FROM    OriginalKeywords NATURAL JOIN KeywordForms
                    WHERE   stem='{k}')
            ORDER BY RANDOM() LIMIT {n}""".format(k=kwd,n=pos_count)

    data.extend([(t[0],'0') for t in curr.execute(q).fetchall()])
    neg_count = len(data) - pos_count

    shuffle(data)
    return data


def run_classifier(vectors, targets):
    k_fold = KFold(n=len(vectors), n_folds=5)
    scores = []
    confusion = np.array([[0, 0], [0, 0]])
    for train_indices, test_indices in k_fold:
        train_vecs = [vectors[i] for i in train_indices] 
        train_y = [targets[i] for i in train_indices]

        test_vecs = [vectors[i] for i in test_indices] 
        test_y = [targets[i] for i in test_indices] 

        gnb = GaussianNB()
        gnb.fit(train_vecs, train_y)
        predictions = gnb.predict(test_vecs)
        confusion += confusion_matrix(test_y, predictions)
        score = f1_score(test_y, predictions, pos_label='1')
        scores.append(score)

    avg_score = sum(scores)/len(scores)

    if display:
        print('Total articles classified:', len(vectors))
        print('Score:', avg_score)
        print('Confusion matrix:')
        print(confusion)

    return (avg_score, confusion)


if __name__ == "__main__":
    display = True
    keyword = sys.argv[1]
    data = get_original_data(keyword)
    titles, targets = zip(*data)
    vectors = [model.docvecs[t] for t in titles]

    run_classifier(vectors, targets)

    #d2v_tester('functional magnetic resonance imaging',n,'redirect')
    #d2v_tester('fMRI',n,'original')

