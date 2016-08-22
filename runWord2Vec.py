# TODO: Write methods that retrieve sentence data

#######################################################################
#
# Directories that need to be set before using.  Models is where the 
# created models will be stored and article is where every article
# resides as a .txt file.  
#
#######################################################################

models_dir =    '/media/removable/SD Card/frontiers_data/models/'
article_dir =   '/media/removable/SD Card/frontiers_data/article_txt/'

#######################################################################
#
# De-comment to set up gensims native logging. Extremely useful when 
# training models, not so much for querying. 
#
#######################################################################

import logging
logging.basicConfig(format='%(asctime)s : %(levelname)s : %(message)s', level=logging.INFO)

#######################################################################
#
# Only gensim needs to be installed for this to work.  The other four
# imports are native to python.  
#
#######################################################################

import gensim.models  

from random import shuffle
import multiprocessing
import re 
import os

cores = multiprocessing.cpu_count()

#######################################################################
#
# Everything related to word2vec model creation. 
#
#######################################################################

class FileList (object):
    def __init__ (self, article_dir = article_dir): 
        """Every time initialized, it shuffles the order it is accessed."""
        self.file_dirs = []
        for file in os.listdir(article_dir):
            self.file_dirs.append(os.path.join(article_dir, file))
        shuffle(self.file_dirs)

    def __iter__ (self): 
        """Call file directories."""
        for file_dir in self.file_dirs: 
            yield file_dir

    def __len__ (self): 
        """Returns the number of files."""
        return len(self.file_dirs)

class Sentences (object): 
    def __init__ (self):
        """Initialization creates a new randomized file list."""
        self.files = FileList()

    def __len__ (self): 
        """Returns the total amount of files looked at."""
        return len(self.files)

    def __iter__ (self):
        """Reads each line of each file, parsing as it goes."""
        for file in self.files: 
            with open(file) as f: 
                for text in f.readlines():
                    parsed_text = (re.sub("[^a-z ]","", text.lower())).split()
                    yield parsed_text

class Word2VecModel (object): 
    def __init__ (self, model_name, models_dir = models_dir):
        """Initialize a model with a size and a path to save the model."""
        self.model_path = os.path.join(models_dir, model_name)
        self.model_name = model_name
        self.model = None

    # Methods for creating and training models
    @time_this
    def create_model (self):
        """Creates the model and builds the vocab."""
        self.model = gensim.models.Word2Vec(\
                        size = 100, \
                        min_count = 5, \
                        alpha = 0.025, \
                        min_alpha = 0.025, \
                        workers = cores)
        sentences = Sentences()
        self.model.build_vocab(sentences)

    @time_this
    def train_model (self): 
        """Trains the model in 20 passes, each time reducing alpha by 0.001."""
        for epoch in range(20):
            print 'Beginning Epoch: %s' % (epoch + 1)
            self.model.train(Sentences())
            self.model.alpha -= 0.001 
            self.model.min_alpha = self.model.alpha
        self.model.save(self.model_path)

    # I/O methods for loading and saving models 
    def load_model (self): 
        """Loads a preexisting word2vec model into memory for querying."""
        self.model = gensim.models.Word2Vec.load(self.model_path)

    def save_model (self, save): 
        """Saves a model to memory. Override save for custom naming."""
        self.model.save(save)

    # Helper get methods 
    def similar_words (self, word, N = 20): 
        """Returns the N most similar words to a given word."""
        return self.model.similar_by_word(word, topn = N)

    def vocab(self):
        """Returns all the vocab for a given model.""" 
        return self.model.vocab

    def num_words (self):
        """Returns the number of words in a given model."""
        return self.model.syn0.shape[0]

    def num_features (self):
        """Returns the number of features in a given model."""
        return self.model.syn0.shape[1]

    # Use after loading to confirm the right model is loaded
    def model_info (self): 
        """Displays information about the given model."""
        print '%s information--' % self.model_name
        print 'Features: %i' % self.num_features()
        print 'Words: %i' % self.num_words()


model = Word2VecModel('epochtraining100features')
model.create_model()
