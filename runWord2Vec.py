###############################################################################
# 
# Creates a model object that can be trained using gensims word2vec. At 
# initializtion, it only requires a single .txt file corpus.  
# 
###############################################################################

import logging
logging.basicConfig(format='%(asctime)s : %(levelname)s : %(message)s', level=logging.INFO)

import gensim.models

import config 
import util

import sys
import os 

reload(sys)
sys.setdefaultencoding('utf-8')

class Model (object): 
    # Takes an already parsed text file from the createcorpus class 
    def __init__ (self, size, min_count, file, save = 'mymodel'):
        self.min_count = min_count
        self.size = size
        self.file = file 
        self.save = os.path.join(config.mDir, save)

    def train_model (self):
        self.model.train(self.sentences)
        self.model.save(self.save)

    def create_model (self):
        # This only needs to be done once during the initialization of the model 
        model = gensim.models.Word2Vec(size = self.size, \
                    min_count = self.min_count)   
        sentences = gensim.models.word2vec.LineSentence(file)
        model.build_vocab(sentences, keep_raw_vocab = False)
        
        self.sentences = sentences
        self.model = model

        self.train_model()        # Do an initial round of training 

    def finalize_training (self): 
        self.model.init_sims(replace = True)

    # Use this method to skip the create_model step -- allows to resume training
    # ONLY if finalize_training has not been called on the model. Otherwise, it 
    # only allows querying
    def load_model (self): 
        self.model = gensim.models.Word2Vec.load(self.save)

    def similar_words (self, word, N = 10):
        print self.model.similar_by_word(word, topn = N)

    def model_info (self): 
        num_w = self.model.syn0.shape[0]
        num_f = self.model.syn0.shape[1]

        print"--------------------------------------"
        print   "There are " + str(num_w) + \
                " words with feature vectors of size " + str(num_f)
        print"--------------------------------------"

    # Still in the process of working on data clustering 
    """
    def cluster_model (self): 
        word_vectors = self.model.syn0
        num_clusters = word_vectors[0] / 5

        kmeans_clustering = KMeans (n_clusters = num_clusters)
        idx = kmeans_clustering.fit_predict(word_vectors)

        word_centroid_map = dict(zip( model.index2word, idx ))
    """

file = 'mycorpus.txt'
file_dir = os.path.join(config.cDir, file)
size = 300 
min_count = 5

# model = Model(size, min_count, file_dir)
# model.create_model()
# model.model_info()


