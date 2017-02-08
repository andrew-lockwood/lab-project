
from sklearn.feature_extraction.text import TfidfTransformer, CountVectorizer
from document_iterator import RawDocuments
from time import time

from sklearn.pipeline import Pipeline

import sqlite3
import numpy as np

from sklearn.cross_validation import KFold
from sklearn.metrics import confusion_matrix, f1_score
from sklearn.naive_bayes import MultinomialNB

from random import shuffle

from context import settings 

import sys

conn = sqlite3.connect(settings.db)
curr = conn.cursor()


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


def run_classifier(text, targets):
    k_fold = KFold(n=len(text), n_folds=5)
    scores = []
    confusion = np.array([[0, 0], [0, 0]])
    for train_indices, test_indices in k_fold:
        train_text = [text[i] for i in train_indices] 
        train_y = [targets[i] for i in train_indices]

        test_text = [text[i] for i in test_indices] 
        test_y = [targets[i] for i in test_indices] 

        text_clf = Pipeline([('vect', CountVectorizer()),
                             ('tfidf', TfidfTransformer()),
                             ('clf', MultinomialNB())])

        text_clf = text_clf.fit(train_text, train_y)
        predictions = text_clf.predict(test_text)
        confusion += confusion_matrix(test_y, predictions)
        score = f1_score(test_y, predictions, pos_label='1')
        scores.append(score)

    avg_score = sum(scores)/len(scores)

    print('Total articles classified:', len(text))
    print('Score:', avg_score)
    print('Confusion matrix:')
    print(confusion)

def get_txt(articleID):
    q = """ SELECT  txt
            FROM    ArticleTXT
            WHERE   articleID='{id}'       """.format(id=articleID)

    return curr.execute(q).fetchall()[0][0]


if __name__ == "__main__":
    keyword = sys.argv[1]
    data = get_original_data(keyword)
    titles, targets = zip(*data)
    print("getting text")
    text = [get_txt(t) for t in titles]
    print("running classifier")
    run_classifier(text, targets)


def create_bag_of_words():
    documents = RawDocuments()

    t0 = time()

    count_vectorizer = CountVectorizer( max_df=0.95, 
                                        min_df=2, 
                                        stop_words='english')

    train_counts = count_vectorizer.fit_transform(documents)
    print(train_counts.shape)

    tf_transformer = TfidfTransformer().fit(train_counts)

    train_tf = tf_transformer.transform(train_counts)
    print(train_tf.shape)

    print("done in %0.3fs." % (time() - t0))

