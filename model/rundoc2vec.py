#### Directories that need to be set before using ####  
# Models: where models will be stored 
# Scores: where model scores will be stored 

import sys
sys.path.insert(0, "C:\\Users\\Andrew\\Desktop\\lab-project\\data")

from sentenceiterator import LabeledSentences
# De-comment to set up gensims native logging. Extremely useful when 
# training models to visualize progress
import logging
logging.basicConfig(format='%(asctime)s : %(levelname)s : %(message)s', \
level=logging.INFO)

# Imported packages. Make sure gensim is installed.   
from gensim.models.doc2vec import Doc2Vec

from collections import Counter
import os

# Set the number of cores 
import multiprocessing
cores = multiprocessing.cpu_count() * 2

class Doc2VecModel (object):    
    def __init__ (self, model_name):
        self.model_path = os.path.join('doc2vecmodels', model_name)
        self.model_name = model_name
        self.model = None

    def create_build_train_model (self, size): 
        self.create_model(size)
        self.build_vocab()
        self.train_model()

    def create_model (self, size):
        """Initializes a model of a given size."""
        self.model = Doc2Vec(size = size, \
                        workers = cores, \
                        sample = 1e-5, \
                        iter = 20)
       
    def build_vocab (self):
        """Builds vocab from a SentenceLabels object."""
        self.sentences = LabeledSentences()
        self.model.build_vocab(self.sentences)

    def train_model (self):
        self.model.train(self.sentences)
        """
        for epoch in range(10):
            print 'Beginning Epoch: %s' % (epoch + 1)
            
            self.model.alpha -= 0.002 
            self.model.min_alpha = self.model.alpha
        """
        self.model.save(self.model_path)

    def save_model (self):  
        self.model.save(self.model_path)

    def load_model (self): 
        self.model = gensim.models.doc2vec.Doc2Vec.load(self.model_path)

    def vocab (self): 
        return self.model.vocab

    def docvecs (self): 
        return self.model.docvecs.doctag_syn0

    def docfeats (self):
        return self.model.docvecs.doctag_syn0.shape[1]

    def docnumber (self): 
        return self.model.docvecs.doctag_syn0.shape[0]

    def get_docvec (self, index): 
        return self.model.docvecs[index]

    def get_doctag (self, index):
        return self.model.docvecs.index_to_doctag(index)

    def get_index (self, doctag):
        return self.model.docvecs.indexed_doctags(doctag)

    def get_similar_words (self, word, N = 20): 
        return self.model.similar_by_word(word, topn = N)

    def get_similar_doc (self, docvec, N = 20):
        return self.model.docvecs.mostsimilar(docvec, topn = N)

    def get_wordvec (self, word): 
        return self.model.syn0[word]

d2v = Doc2VecModel('testmodel')
d2v.create_build_train_model(10)