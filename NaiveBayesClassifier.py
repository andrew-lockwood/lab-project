
from sklearn.naive_bayes import BernoulliNB, GaussianNB, MultinomialNB
from corpusProcessors import txtFiles
from collections import defaultdict
from random import shuffle
import gensim.models
import numpy as np
from util import time_this
from sklearn.cross_validation import train_test_split
from sklearn.cross_validation import cross_val_score
import csv
import re
import os

kwd_dir =     '/media/removable/SD Card/frontiers_data/data/kwd_data/'

class Classify (object): 
    def __init__ (self, keyword, size=None): 
        """
        Creates the sets needed for classification later one. 
        If size is left as None, the full set of titles is used. 
        If not, random titles will be pulled from the set for 
        classification. 
        """
        self.keyword = keyword
        self.size  = size

    def load_articles (self):
        features = 500
        model_name = str(features) + 'model'
        feature_dir = '/media/removable/SD Card/frontiers_data/featureTest'
        model_dir = os.path.join(feature_dir, str(features), model_name)
        model = gensim.models.doc2vec.Doc2Vec.load(model_dir)

        articles = txtFiles()
        positive_set = articles.kwd_title_set(self.keyword)
        negative_set = articles.complement_kwd_title_set(self.keyword)

        positive_articles = self.shuffle_set(positive_set)
        negative_articles = self.shuffle_set(negative_set)

        data = []
        for i in xrange(self.size):
            data.append([positive_articles[i], 1])
            data.append([negative_articles[i], 0])

        data = np.array(data)
        np.random.shuffle(data)

        vectors = []
        titles = data[:,0]
        for d in titles:
            vectors.append(model.docvecs[d])

        d = np.array(vectors)
        t = data[:,1]

        bnb = BernoulliNB()
        scores = cross_val_score(bnb, d, t, cv=5)
        print("Bernoulli Accuracy: %0.3f (+/- %0.3f)" % \
            (scores.mean(), scores.std() * 2))

        gnb = GaussianNB()
        scores = cross_val_score(gnb, d, t, cv=5)
        print("Guassian Accuracy:  %0.3f (+/- %0.3f)" % \
            (scores.mean(), scores.std() * 2))

    def shuffle_set (self, s): 
        """Shuffles a set and returns a list."""
        x = list(s)
        shuffle(x)
        return x

@time_this
def run_trials (kwd, fold, size, n): 
    scores = []
    for i in xrange(n): 
        c = Classify(kwd, fold=fold, size=size)
        c.load_vectors(500)
        for score in c.train():
            scores.append(score)
    x = np.array(scores)
    print "total trials: " + str(n)
    print "variance: " + str(np.var(x))
    print "average: " + str(np.average(x))

#run_trials('emotion', 5, 200, 5)

c = Classify('emotion', size=200)
c.load_articles()

