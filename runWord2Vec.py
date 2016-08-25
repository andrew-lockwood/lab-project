# Slimmed down version of previous iterations of this file. Has a few less
# checks, but because it clearer and more concise, it shouldn't be an issue.

# Directories that need to be set before using.  Models is where the 
# created models will be stored, score is where scores and frequencies
# will be stored, and article is where every article resides as a .txt file.  
models_dir =    '/media/removable/SD Card/frontiers_data/models/word2vec/'
score_dir =     '/media/removable/SD Card/frontiers_data/models/word2vec_scores/'
article_dir =   '/media/removable/SD Card/frontiers_data/article_txt/'

# De-comment to set up gensims native logging. Extremely useful when 
# training models, not so much for querying. 
#import logging
#logging.basicConfig(format='%(asctime)s : %(levelname)s : %(message)s', level=logging.INFO)

# Only gensim needs to be installed for this to work. Util can be 
# decommented. The only thing it controls is a progress bar on the 
# command line. The other five imports are native to python.  
import gensim.models  

from util import ProgressBar

from collections import Counter
from random import shuffle
import multiprocessing
import csv
import re 
import os

cores = multiprocessing.cpu_count()

def time_this(original_function):    
    """Decorator used to quickly time a function."""  
    def new_function(*args,**kwargs):
        import datetime                 
        before = datetime.datetime.now()                     
        x = original_function(*args,**kwargs)                
        after = datetime.datetime.now()                      
        print "Elapsed Time = {0}".format(after-before)      
        return x                                             
    return new_function

# Iterates randomly through through all the articles, preserving the
# order within the article themselves. Parses text on the fly. This 
# can be modified by changing parsed_line within the iterator.
class Sentences (object): 
    def __init__ (self, article_dir = article_dir):
        """Initialization creates a new randomized file list."""
        self.file_dirs = []
        for file in os.listdir(article_dir):
            self.file_dirs.append(os.path.join(article_dir, file))
        shuffle(self.file_dirs)

    def __len__ (self): 
        """Returns the total amount of files looked at."""
        return len(self.file_dirs)

    def __iter__ (self):
        """Reads each line of each file, parsing as it goes."""
        for file_dir in self.file_dirs: 
            with open(file_dir) as file: 
                for line in file.readlines():
                    parsed_line = (re.sub("[^a-z ]","", line.lower())).split()
                    yield parsed_line

# This class manually controls the learning rate, decreasing alpha by 0.001
# with each subsequent class, from 0.025 --> 0.005. To change that rate, modify
# train_model with the number of epochs and the rate of decay.
class Word2VecModel (object): 
    def __init__ (self, model_name, models_dir = models_dir):
        """Initialize a model with a size and a path to save the model."""
        self.model_path = os.path.join(models_dir, model_name)
        self.model_name = model_name
        self.model = None

    ### Methods for creating and training models ###
    def create_model (self, size):
        """Creates the model and builds the vocab."""
        self.model = gensim.models.Word2Vec(\
                        size = size, \
                        min_count = 5, \
                        alpha = 0.025, \
                        min_alpha = 0.025, \
                        workers = cores)
        sentences = Sentences()
        self.model.build_vocab(sentences)

    def train_model (self): 
        """Trains the model in 20 passes, each time reducing alpha by 0.001."""
        for epoch in range(20):
            print 'Beginning Epoch: %s' % (epoch + 1)
            self.model.train(Sentences())
            self.model.alpha -= 0.001               # Alpha rate of decay
            self.model.min_alpha = self.model.alpha
        self.model.save(self.model_path)  

    ### I/O methods for loading and saving models ###
    def load_model (self): 
        """Loads a preexisting word2vec model into memory for querying."""
        self.model = gensim.models.Word2Vec.load(self.model_path)

    def save_model (self, save): 
        """Saves a model to memory. Override save for custom naming."""
        self.model.save(save)

    def model_info (self): 
        """Displays information about the given model."""
        print '%s information--' % self.model_name
        print 'Features: %i' % self.num_features()
        print 'Words: %i' % self.num_words()

    ### Helper get methods ### 
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

# Only needs to be ran once for creating a histogram of the data later on 
# Make sure the load path is correct at the top of binnedHistogram when used
class FrequencyDict (object): 
    def __init__ (self, score_dir = score_dir):
        """Creates and saves a frequency dictionary from Sentences().""" 
        sentences = Sentences()

        word_count = Counter()
        for sentence in sentences: 
            for word in sentence: 
                word_count[word] += 1

        save_path = os.path.join(score_dir, save)
        frequency_file = csv.writer(open(save_path, 'w')) 
        for word, frequency in word_count.iteritems(): 
            frequency_file.writerow([word, frequency])

# Takes about 20 minutes for ~80,000 words 
# For initial comparison, use create_comparison then score
# For querying, load_comparison, then display 
class CompareModels(object):
    def __init__ (  self, model1, model2, N = 25, save = 'mycompare.csv',\
                    models_dir = models_dir, score_dir = score_dir):
        """Initialize with two different models and a path to save the results."""
        self.save_path = os.path.join(score_dir, save)
        self.model1 = model1 
        self.model2 = model2
        self.N = N

    def load_comparison (self): 
        score_file = csv.reader(open(self.save_path))
        score_file.next()   
        self.c = Counter()
        for word, intersection, union, index, distance in score_file: 
            self.c[word] = index

    def display_similar_words (self, N):
        """Displays the N most dissimlar words to the terminal."""
        print 'The ' + str(N) + ' most similar words are...'
        print 'distance | word'
        for  key, value in self.c.most_common(N):
            print str(round(float(value), 5)) + "  | " + key    

    def display_disimilar_words (self, N):
        """Displays the N most similar words to the terminal."""
        print 'The ' + str(N) + ' most dissimilar words are...'
        print 'distance | word'
        for  key, value in self.c.most_common()[:-N-1:-1]:
            print str(round(float(value), 5)) + "  | " + key  

    def create_comparison (self):
        """Sets up the class variables for scoring the models."""
        print "Loading models..."
        self.m1 = Word2VecModel(model_name = self.model1)
        self.m2 = Word2VecModel(model_name = self.model2)
        self.m1.load_model()
        self.m2.load_model()

        print "Creating score file..."
        fieldnames = [  'word', 'intersection', 'union', \
                        'jaccard_index', 'jaccard_distance']
        file = open(self.save_path, 'w')
        self.writer = csv.DictWriter(file, fieldnames = fieldnames)
        self.writer.writeheader()

    def to_set (self, model_dict):
        """Takes a dictionary and returns the set of keys."""
        model_set = set()
        for key, value in model_dict: 
            model_set.add(key)
        return model_set

    def jaccard_score(self, word):
        """Scores the similarity and diversity of two given sets."""
        m1_list = self.m1.similar_words(word, N = self.N)
        m2_list = self.m2.similar_words(word, N = self.N)
        m1_set = self.to_set(m1_list)
        m2_set = self.to_set(m2_list)

        i = len(m1_set.intersection(m2_set))
        u = len(m1_set.union(m2_set))

        # Calculate the Jaccard index and distance 
        j_index = i / float(u)
        j_distance = 1 - j_index
        self.writer.writerow({'word':word, \
                'intersection':i, \
                'union':u, \
                'jaccard_index':j_index, \
                'jaccard_distance':j_distance})

    def score (self): 
        """Scores every word in the vocabulary of the models."""
        print 'Scoring every word in the models...'
        words = self.m1.vocab()
        displaybar = ProgressBar(len(words))
        for word in words:
            self.jaccard_score(word)
            displaybar.step()