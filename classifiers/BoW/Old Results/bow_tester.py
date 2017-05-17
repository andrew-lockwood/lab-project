from sklearn.metrics import confusion_matrix, f1_score
from sklearn.cross_validation import KFold
from sklearn.feature_extraction.text import CountVectorizer
from sklearn.naive_bayes import MultinomialNB, GaussianNB
from sklearn.pipeline import Pipeline

import gensim.models

from sklearn import decomposition
from collections import defaultdict
from time import time
import numpy as np
import csv

from context import DataLoader


def run_classifier(vectors, targets):
    k_fold = KFold(n=len(targets), n_folds=5)
    scores = []
    confusion = np.array([[0, 0], [0, 0]])

    for train_indices, test_indices in k_fold:
        train_vecs = [vectors[i] for i in train_indices]
        train_y = [targets[i] for i in train_indices]

        test_vecs = [vectors[i] for i in test_indices] 
        test_y = [targets[i] for i in test_indices] 

        pipeline = Pipeline([   ('vectorizer',  CountVectorizer()),
                                ('classifier',  MultinomialNB())    ])

        pipeline.fit(train_vecs, train_y)
        predictions = pipeline.predict(test_vecs)
        confusion += confusion_matrix(test_y, predictions)
        score = f1_score(test_y, predictions, pos_label='1')
        scores.append(score)

    avg_score = sum(scores)/len(scores)

    return (avg_score, confusion)


def summary_stats(x): 
    """Takes an array and returns summary statistics."""
    x = np.array(x)
    return(np.mean(x), np.median(x), np.var(x))



if __name__ == '__main__':
    t0 = time()
    data = DataLoader(70)
    text_data = data.load_text_greater_than()

    with open("new_results.csv", "w", newline='') as f:
        fieldnames = ["keyword", "articles tested",
                        "score mean", "score median", "score var",
                        "tp mean", "tp median", "tp var",
                        "fp mean", "fp median", "fp var",
                        "tn mean", "tn median", "tn var",
                        "fn mean", "fn median", "fn var"]
        w = csv.DictWriter(f, fieldnames=fieldnames)

        w.writeheader()

        for kwd in data.get_keywords():
            print(kwd)
            scores = []
            confusions = defaultdict(list)

            for i in range(10):
                data.analyze(kwd)

                titles, targets = zip(*data.get_title_dict())

                text = [text_data[t] for t in titles]

                score, confusion = run_classifier(text, targets)

                scores.append(score)

                confusions["true positive"].append(confusion[0][0])
                confusions["false negative"].append(confusion[0][1])
                confusions["false positive"].append(confusion[1][0])
                confusions["true negative"].append(confusion[1][1])

            row = {}

            row["keyword"] = kwd
            row["articles tested"] = data.num_titles()

            row["score mean"], row["score median"], row["score var"] = summary_stats(scores)

            row["tp mean"], row["tp median"], row["tp var"] = summary_stats(confusions["true positive"])
            row["fp mean"], row["fp median"], row["fp var"] = summary_stats(confusions["false positive"])
            row["fn mean"], row["fn median"], row["fn var"] = summary_stats(confusions["false negative"])
            row["tn mean"], row["tn median"], row["tn var"] = summary_stats(confusions["true negative"])

            w.writerow(row)
            #print(row)
        print("Time Elapsed: " + str(time()-t0))
