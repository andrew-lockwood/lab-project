from sklearn.metrics import confusion_matrix, precision_recall_fscore_support
from sklearn.cross_validation import KFold
from sklearn.naive_bayes import GaussianNB

import gensim.models

from collections import defaultdict, Counter
from time import time
import numpy as np
import csv

from context import DataLoader, settings


def summary_stats(x):
    """Takes an array and returns summary statistics."""
    x = np.array(x)
    return np.mean(x), np.median(x), np.var(x)


def run_classifier(vectors, targets):
    test_size = len(vectors)

    k_fold = KFold(n=test_size, n_folds=5)
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
        score = precision_recall_fscore_support(test_y, predictions, average='binary', pos_label='1')
        scores.append(score)

    avg_scores = []

    for y in zip(*scores):
        if None in y:
            break
        else:
            avg_scores.append(sum(y) / len(y))

    norm_confusion = confusion / test_size

    return avg_scores, norm_confusion


def false_positive_detector(titles, model, targets):
    vectors = [model.docvecs[t] for t in titles]

    false_positives = set()
    test_size = len(titles)

    k_fold = KFold(n=test_size, n_folds=5)

    for train_indices, test_indices in k_fold:
        train_vecs = [vectors[i] for i in train_indices]
        train_y = [targets[i] for i in train_indices]

        test_vecs = [vectors[i] for i in test_indices]
        test_y = [targets[i] for i in test_indices]

        gnb = GaussianNB()
        gnb.fit(train_vecs, train_y)
        predictions = gnb.predict(test_vecs)

        i = 0
        for predicted, actual in zip(predictions, test_y):
            if predicted == "1" and actual == "0":
                false_positives.add(titles[test_indices[i]])
            i += 1

    return false_positives


def find_false_positives(iterations, kwd):
    data = DataLoader()

    model = gensim.models.Doc2Vec.load(settings.d2v500)

    total_count = Counter()
    false_positive_count = Counter()

    t0 = time()
    for i in range(iterations):
        data.analyze(kwd)

        title_dict = data.get_title_dict()

        for title, target in title_dict:
            if target == "0":
                total_count[title] += 1

        titles, targets = zip(*title_dict)

        false_positives = false_positive_detector(titles, model, targets)

        for title in false_positives:
            false_positive_count[title] += 1

    false_positive_ratio = Counter()

    for title, count in false_positive_count.items():
        false_positive_ratio[title] = false_positive_count[title]/total_count[title]

    filename = kwd + ".csv"

    with open(filename, 'w', newline="") as f:
        fieldnames = [
            "article id", "fp ratio", "fp count", "support", "title", "original keywords"
        ]

        w = csv.DictWriter(f, fieldnames=fieldnames)

        w.writeheader()

        for article_id, ratio in false_positive_ratio.most_common():
            row = dict()

            row['article id'] = article_id
            row['fp ratio'] = ratio
            row['fp count'] = false_positive_count[article_id]
            row['support'] = total_count[article_id]

            article_title, kwds = data.article_title_keywords(article_id)

            row['title'] = article_title
            row['original keywords'] = kwds

            w.writerow(row)

    elapsed_time = time() - t0
    print("Elapsed Time : %0.3f" % elapsed_time)


def run_tests(iterations):
    """ Currently Configured to test the 100 model -- change the loaded model
        and the save location and different models can be tested."""
    data = DataLoader()
    model = gensim.models.Doc2Vec.load(settings.d2v500)
    t0 = time()

    with open("test.csv", "w", newline="") as f:
        fieldnames = [
                        "keyword", "articles tested",
                        "precision mean", "precision median", "precision var",
                        "recall mean", "recall median", "recall var",
                        "f1 mean", "f1 median", "f1 var",
                        "tp mean", "tp median", "tp var",
                        "fp mean", "fp median", "fp var",
                        "tn mean", "tn median", "tn var",
                        "fn mean", "fn median", "fn var"
                      ]

        w = csv.DictWriter(f, fieldnames=fieldnames)

        w.writeheader()

        for kwd in data.get_keywords():
            print(kwd)
            results = defaultdict(list)

            for i in range(iterations):
                data.analyze(kwd)

                titles, targets = zip(*data.get_title_dict())
         
                vectors = [model.docvecs[t] for t in titles]

                score, confusion = run_classifier(vectors, targets)

                results["precision"].append(score[0])
                results["recall"].append(score[1])
                results["fscore"].append(score[2])

                results["true positive"].append(confusion[0][0])
                results["false negative"].append(confusion[0][1])
                results["false positive"].append(confusion[1][0])
                results["true negative"].append(confusion[1][1])

            row = dict()

            row["keyword"] = kwd
            row["articles tested"] = data.num_titles()

            row["precision mean"], row["precision median"], row["precision var"] = summary_stats(results["precision"])
            row["recall mean"], row["recall median"], row["recall var"] = summary_stats(results["recall"])
            row["f1 mean"], row["f1 median"], row["f1 var"] = summary_stats(results["fscore"])

            row["tp mean"], row["tp median"], row["tp var"] = summary_stats(results["true positive"])
            row["fp mean"], row["fp median"], row["fp var"] = summary_stats(results["false positive"])
            row["fn mean"], row["fn median"], row["fn var"] = summary_stats(results["false negative"])
            row["tn mean"], row["tn median"], row["tn var"] = summary_stats(results["true negative"])

            w.writerow(row)

    elapsed_time = time() - t0
    print("Elapsed Time : %0.3f" % elapsed_time)


if __name__ == '__main__':
    find_false_positives(10000, "bilingualism")
    find_false_positives(10000, "cognition")
    find_false_positives(10000, "embodiment")
