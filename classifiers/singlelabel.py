# installed imports -- need scikit, gensim, and numpy 
from sklearn.naive_bayes import BernoulliNB, GaussianNB
from sklearn.cross_validation import cross_val_score
import gensim.models
import numpy as np

# custom files that need to be in the same directory
from corpusProcessors import txtFiles
from util import time_this

# python imports 
from random import shuffle
import sys
import csv
import re
import os

from directories import kwd_dir, feature_dir
from corpusProcessors import DataLoader
from collections import defaultdict
from tabulate import tabulate


# directorys that need to be set 
kwd_dir =       kwd_dir()
feature_dir =   feature_dir()

class Classify (object): 
    def __init__ (self, features): 
        self.features = features
        self.data = DataLoader()
        self.load_vectors()

    def run_trials (self, kwd, n):
        score = 0
        for i in range(n): 
            score += self.test_kwd(kwd)

        ascore = score/float(n)

        return ascore

    def test_kwd (self, keyword):
        """Takes a keyword and creates a classifier based on that
        keyword.Calling several times in a row with different 
        keywords is fairly fast since the slow step is loading 
        vectors (1 minute for vector loading vs 1 second for grabbing
        vectors and creating multiple classifiers).
        """
        positive = self.data.pos_kwd_title_set(keyword)
        negative = self.data.neg_kwd_title_set(keyword)

        positive_articles = self.shuffle_set(positive)
        negative_articles = self.shuffle_set(negative)

        # Check to make sure testing doesn't access articles that 
        # aren't there
        pos_size = len(positive_articles)
        neg_size = len(positive_articles)

        data = []
        for i in range(pos_size):
            data.append([positive_articles[i], 1])
        for i in range(neg_size):
            data.append([negative_articles[i], 0])

        data = np.array(data)
        np.random.shuffle(data)

        # Convert titles to vectors 
        vectors = []
        titles = data[:,0]
        for d in titles:
            vectors.append(self.model.docvecs[d])

        # Data and Target 
        d = np.array(vectors)
        t = data[:,1]

        # Classifier testing -- using the same randomly generated 
        # data, test different classifiers and scoring methods
        gnb = GaussianNB()
        scores = cross_val_score(gnb, d, t, cv=5, scoring='f1_macro')
        #print("f1 score:  %0.3f (+/- %0.3f)" % \
        #    (scores.mean(), scores.std() * 2))
        return scores.mean()
        #scores = cross_val_score(gnb, d, t, cv=5)
        #print("default:   %0.3f (+/- %0.3f)" % \
        #    (scores.mean(), scores.std() * 2))


    def shuffle_set (self, s): 
        """Shuffles a set and returns a list."""
        x = list(s)
        shuffle(x)
        return x

    def load_vectors (self): 
        """Loads a trained model from featureTest."""
        model_name = str(self.features) + 'model'
        model_dir = os.path.join(feature_dir, \
                        str(self.features), model_name)
        self.model = gensim.models.doc2vec.Doc2Vec.load(model_dir)


class NaiveBayesTester (object):
    def __init__ (self, k):
        self.k = k
        self.features = [50, 100, 300, 500]
        self.data = DataLoader()

    def test (self, n):
        kwds = self.data.kwds_greater_than(n)
        results = defaultdict(list)
        for feature in self.features:
            print (feature)
            c = Classify(feature)
            for kwd in kwds: 
                results[kwd].append(c.run_trials(kwd, self.k))

        h = ['kwd']
        h.extend(self.features)
        table = []
        for kwd, scores in results.items():
            row = [kwd]
            row.extend(scores)
            table.append(row)

        print (tabulate(table, headers=h, floatfmt=".3f"))


nbt = NaiveBayesTester(100)
nbt.test(200)