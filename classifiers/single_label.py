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

    return (len(vectors), avg_score, confusion)


def run_bow_classifier(text, targets):
    k_fold = KFold(n=len(text), n_folds=5)
    scores = []
    confusion = np.array([[0, 0], [0, 0]])

    for train_indices, test_indices in k_fold:
        train_text = [text[i] for i in train_indices] 
        train_y = [targets[i] for i in train_indices]

        test_text = [text[i] for i in test_indices] 
        test_y = [targets[i] for i in test_indices] 

        pipeline = Pipeline([
            ('vectorizer',  CountVectorizer()),
            ('classifier',  MultinomialNB()) ])

        pipeline.fit(train_text, train_y)

        predictions = pipeline.predict(test_text)

        confusion += confusion_matrix(test_y, predictions)
        score = f1_score(test_y, predictions, pos_label='1')
        scores.append(score)

    avg_score = sum(scores)/len(scores)

    return (len(text), avg_score, confusion)


if __name__ == "__main__":

    keyword = sys.argv[1]

    confusion = [[0,0],[0,0]]
    score = 0
    n = 500

    for i in range(n):
        data = DataLoader()
        data.analyze(keyword)
        data.set_type("vectors")
        vectors, targets = zip(*[t for t in data])
        results = run_vec_classifier(vectors, targets)

        score += results[1]
        confusion += results[2]

    print(score/n)
    print(confusion)


    """
    with open("results.txt", "w") as f:
        for i in range(5):
            data = DataLoader()

            data.analyze(keyword)
            f.write("-------------------------------- \n")
            t0 = time()
        
            data.set_type("text")
            text, targets = zip(*[t for t in data])
            f.write("Running Bag of Words Classifier... \n")
            results = run_bow_classifier(text, targets)

            f.write("Articles Classified: %i \n" % results[0])
            f.write("Score: %d \n" % results[1])
            f.write("Confusion \n")
            f.write(np.array_str(results[2]))
            f.write("\n")
            data.set_type("vectors")
            vector, targets = zip(*[t for t in data])

            f.write("-------------------------------- \n")
            f.write("Running Doc2Vec Classifier... \n")
            results = run_vec_classifier(vector, targets)

            f.write("Articles Classified: %i \n" % results[0])
            f.write("Score: %d \n" % results[1])
            f.write("Confusion \n")
            f.write(np.array_str(results[2]))
            f.write("\n")

            f.write("done in %0.3fs. \n" % (time() - t0))
            f.write("-------------------------------- \n")
    """
