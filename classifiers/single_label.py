import numpy as np


from sklearn.feature_extraction.text import TfidfTransformer, CountVectorizer
from sklearn.pipeline import Pipeline
from sklearn.cross_validation import KFold
from sklearn.metrics import confusion_matrix, f1_score
from sklearn.naive_bayes import GaussianNB
from sklearn.naive_bayes import MultinomialNB

from time import time

import sys

from context import DataLoader

display = False


def run_vec_classifier(vectors, targets):
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


def run_bow_classifier(text, targets):
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
                             ('clf', GaussianNB())])

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



if __name__ == "__main__":
    display = True
    keyword = sys.argv[1]
    data = DataLoader()

    data.analyze(keyword)

    t0 = time()
    data.set_type("text")
    text, targets = zip(*[t for t in data])
    print("Running Bag of Words Classifier...")
    run_bow_classifier(text, targets)

    data.set_type("vectors")
    vector, targets = zip(*[t for t in data])

    print("--------------------------------")
    print("Running Doc2Vec Classifier...")
    run_vec_classifier(vector, targets)

    print("done in %0.3fs." % (time() - t0))
