import logging
# logging.basicConfig(format='%(asctime)s : %(levelname)s : %(message)s', level=logging.INFO)

from collections import Counter
import gensim.models
import csv

from util import Progress_Bar
from util import Time
import config 

import sys
import os 

reload(sys)
sys.setdefaultencoding('utf-8')

###############################################################################
# 
# Creates a model object that can be trained using gensims word2vec. At 
# initializtion, it only requires a single .txt file corpus.  
# 
###############################################################################

class Model (object): 
    # Takes an already parsed text file from the createcorpus class 
    def __init__ (self, size = 0, min_count = 0, file = None, save = 'mymodel'):
        self.min_count = min_count
        self.size = size
        self.file = file 
        self.save = os.path.join(config.mDir, save)

    def train_model (self):
        self.model.train(self.sentences)
        self.model.init_sims(replace = True)
        self.model.save(self.save)

    def create_model (self):
        # This only needs to be done once during the initialization of the model 
        model = gensim.models.Word2Vec(size = self.size, \
                    min_count = self.min_count)   
        sentences = gensim.models.word2vec.LineSentence(self.file)
        model.build_vocab(sentences, keep_raw_vocab = False)
        
        self.sentences = sentences
        self.model = model

        self.train_model()        # Do an initial round of training 

    def finalize_training (self): 
        self.model.init_sims(replace = True)

    def get_vocab(self): 
        return self.model.vocab

    # Use this method to skip the create_model step -- allows to resume training
    # ONLY if finalize_training has not been called on the model. Otherwise, it 
    # only allows querying
    def load_model (self): 
        self.model = gensim.models.Word2Vec.load(self.save)

    def similar_words (self, word, N = 10):
        return self.model.similar_by_word(word, topn = N)

    def model_info (self): 
        num_w = self.model.syn0.shape[0]
        num_f = self.model.syn0.shape[1]

        print"--------------------------------------"
        print   "There are " + str(num_w) + \
                " words with feature vectors of size " + str(num_f)
        print"--------------------------------------"

###############################################################################
# 
# Takes two models created from the above class, reloads them within the class
# below, then scores word similarity. 
#   NOTE ON SCORING: A 'score' is how much two sets cross one another. A score 
#   0 implies they are the same, a score of 1 implies they have no words in 
#   common at all. The absolute difference between sets is averaged, with 1 
#   being added if there are word mismatches. 
#
#   For example, if a word produces the following from two different models:
#       set1 = {c:0.7, a:0.5, b:0.1}
#       set2 = {a:0.4, d:0.3, b:0.2}
#   The 'score' from that word would be [(0.5-0.4) + abs(0.1-0.2) + 1] / 3
#   giving the answer 1.2/3 = 0.4 
#
#   This value is then recorded with a counter and then the process is repeated 
#
###############################################################################

class CompareModels(object):
    #N specifies how many words to look back in similar_words
    def __init__ (self, model1, model2, N):
        self.m1 = Model(save = model1)
        self.m2 = Model(save = model2)
        self.N = N

    def load_models(self):
        self.m1.load_model()
        self.m2.load_model()

    def models_info(self):
        self.m1.model_info()
        self.m2.model_info()

    def jaccard_score (self, word):
        m1_list = self.m1.similar_words(word, N = self.N)
        m2_list = self.m2.similar_words(word, N = self.N)

        print m1_list


    """
    #old method of scoring two sets 
    def score(self, word):
        sim_words = 0 
        sim_score = 0
        m1_list = self.m1.similar_words(word, N = self.N)
        m2_list = self.m2.similar_words(word, N = self.N)

        #get the difference between words in both listsx
        for w1, d1 in m1_list:
            for w2, d2 in m2_list:
                if w1 == w2:
                    sim_words += 1
                    sim_score += abs(d1 - d2)

        #add in the missing word score
        sim_score += self.N - sim_words

        #uncomment this to get specific information about a word to visualize 
        #differences the number of features makes 
        
        print "words in common: " + str(sim_words) 
        print "score of words in common: " + str(sim_score/float(self.N))
        print "-----------------------------------------"
        print "model 1 words -"
        print self.m1.similar_words(word, N = self.N)
        print "-----------------------------------------"
        print "model 2 words -"
        print self.m2.similar_words(word, N = self.N)
        

        return sim_score/float(self.N)
    """

    def load_frequency_dict (self, total_keys):
        #loads a .csv already made in the createCorpus class 
        c = Counter()
        f = os.path.join(config.cDir, 'parsed_frequency_counts.csv')
        for key, value in csv.reader(open(f)):
            #this check might not be necessary. functions the same as min_count.
            if int(value) > 4:
                c[key] = int(value)
            else:
                continue

        return c.most_common(total_keys)

"""
def model_corpus(size): 
    file = os.path.join(config.cDir, 'parsed_complete_corpus.txt')
    model = Model(size = size, min_count = 5, file = file, save = '100model')
    model.load_model()

    for key in model.get_vocab():
        print key
"""

def score_corpus (total_keys): 
    test_scores = Counter()
    compare = CompareModels (model1 = '50model', model2 = '300model', N = 20)
    compare.load_models()
    compare.jaccard_score('brain')
    """
    test_keys = compare.load_frequency_dict(total_keys)
    b = Progress_Bar(len(test_keys))
    for word, value in test_keys:
        test_scores[word] = compare.score(word)
        b.step()
    """

score_corpus(1000)


