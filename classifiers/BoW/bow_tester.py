# Running as is spits out raw data (as long as the DataLoader class is properly
# implemented).  Requires manual formatting in Excel to view.
#
#  TODO: Comment and Document

from sklearn.metrics import confusion_matrix, precision_recall_fscore_support
from sklearn.cross_validation import KFold
from sklearn.feature_extraction.text import TfidfVectorizer, CountVectorizer
from sklearn.naive_bayes import MultinomialNB
from scipy.sparse import vstack
from collections import defaultdict
from time import time
import numpy as np
import csv

from context import DataLoader


def summary_stats(x):
    """Takes an array and returns summary statistics."""
    x = np.array(x)
    return np.mean(x), np.median(x), np.var(x)


def classify(text, targets, vectorizer):
    # Vectorize the test set
    vectors = vectorizer.fit_transform(text)
    test_size = len(targets)

    k_fold = KFold(n=test_size, shuffle=True, n_folds=5)

    confusion = np.array([[0, 0], [0, 0]])
    scores = []

    for train_indices, test_indices in k_fold:
        train_vectors = vstack([vectors[i] for i in train_indices])
        train_labels = [targets[i] for i in train_indices]

        test_vectors = vstack([vectors[i] for i in test_indices])
        test_labels = [targets[i] for i in test_indices]

        classifier = MultinomialNB()
        classifier.fit(train_vectors, train_labels)

        predictions = classifier.predict(test_vectors)

        confusion += confusion_matrix(test_labels, predictions)

        score = precision_recall_fscore_support(test_labels, predictions, average='binary', pos_label='1')
        scores.append(score)

    avg_scores = []

    for y in zip(*scores):
        if None in y:
            break
        else:
            avg_scores.append(sum(y)/len(y))

    norm_confusion = confusion/test_size

    return avg_scores, norm_confusion


def run_tests(iterations, file_name, text_transformer):
    data = DataLoader()
    text_data = data.load_text_greater_than()

    t0 = time()

    with open(file_name, 'w', newline='') as f:
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
                # Generates a new negative set of articles
                data.analyze(kwd)

                titles, targets = zip(*data.get_title_dict())

                text = [text_data[t] for t in titles]

                score, confusion = classify(text, targets, text_transformer)

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

    elapsed_time = t0 - time()
    print("Elapsed Time : %0.3f" % elapsed_time)


if __name__ == '__main__':
    run_tests(20, "bow_tfidf.csv", TfidfVectorizer())
    run_tests(20, "bow.csv", CountVectorizer())
