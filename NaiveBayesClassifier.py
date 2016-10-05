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
import csv
import re
import os

# directorys that need to be set 
kwd_dir =     '/media/removable/SD Card/frontiers_data/data/kwd_data/'
feature_dir = '/media/removable/SD Card/frontiers_data/featureTest'

class Classify (object): 
    def __init__ (self, features, size=None): 
        """Sets object variables."""
        self.size  = size
        self.features = features
        self.load_vectors()

    def test_kwd (self, keyword):
        """Takes a keyword and creates a classifier based on that
        keyword.Calling several times in a row with different 
        keywords in fairly fast since the slow step is loading 
        vectors (1 minute for vector loading vs 1 second for grabbing
        vectors and creating multiple classifiers).
        """
        articles = txtFiles()
        positive_set = articles.kwd_title_set(keyword)
        negative_set = articles.complement_kwd_title_set(keyword)

        positive_articles = self.shuffle_set(positive_set)
        negative_articles = self.shuffle_set(negative_set)

        # Check to make sure testing doesn't access articles that 
        # aren't there
        if self.size>len(positive_articles) or self.size==None:
            self.size = len(positive_articles)

        data = []
        for i in xrange(self.size):
            data.append([positive_articles[i], 1])
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
        print("f1 score:  %0.3f (+/- %0.3f)" % \
            (scores.mean(), scores.std() * 2))

        scores = cross_val_score(gnb, d, t, cv=5)
        print("default:  %0.3f (+/- %0.3f)" % \
            (scores.mean(), scores.std() * 2))


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


c = Classify(features=100, size=400)
c.test_kwd('emotion')
c.test_kwd('attention')
