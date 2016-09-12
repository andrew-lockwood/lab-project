# Directories that need to be set before using.  Models is where the 
# created models will be stored and article is where every article
# resides as a .txt file.  
models_dir =    '/media/removable/SD Card/frontiers_data/models/doc2vec'
article_dir =   '/media/removable/SD Card/frontiers_data/article_txt/'

# De-comment to set up gensims native logging. Extremely useful when 
# training models, not so much for querying. 
import logging
logging.basicConfig(format='%(asctime)s : %(levelname)s : %(message)s', level=logging.INFO)

# Only gensim needs to be installed for this to work.  The other four
# imports are native to python.  
import gensim.models  

from util import ProgressBar
from random import shuffle
import multiprocessing
import re 
import os

cores = multiprocessing.cpu_count()

# Decorator for displaying elapsed time of a function
def time_this(original_function):      
    def new_function(*args,**kwargs):
        import datetime                 
        before = datetime.datetime.now()                     
        x = original_function(*args,**kwargs)                
        after = datetime.datetime.now()                      
        print "Elapsed Time = {0}".format(after-before)      
        return x                                             
    return new_function

class SentenceLabels (object):
    def __init__ (self, article_dir = article_dir, label_lines = False):
        """Initialization creates a new randomized file list."""
        self.label_lines = label_lines
        self.file_dirs = []
        for file in os.listdir(article_dir):
            self.file_dirs.append(os.path.join(article_dir, file))
        shuffle(self.file_dirs)	

    def num_articles (self): 
        """Returns the number of files looked at."""
        return len(self.file_dirs)

    def num_lines (self): 
        """Returns the number of lines in the file."""
        num_lines = 0
        for file_dir in self.file_dirs:
            with open(file_dir) as file: 
                for line in file.readlines():
                    num_articles += 1
        return num_lines

    def __iter__ (self):
        """Iterates through each line in each file."""
        for file_dir in self.file_dirs:
            with open(file_dir) as file: 
                file_title = re.sub(article_dir, "", file_dir)
                for line in file.readlines():
                    parsed_line = (re.sub("[^a-z ]", "", line.lower())).split()
                    label = re.sub('.txt', '', file_title)
                    if self.label_lines:     
                        label = label + '_' + str(line)
                    yield gensim.models.doc2vec.LabeledSentence(words = parsed_line, tags = [label])

class Doc2VecModel (object):    
    def __init__ (self, model_name, models_dir = models_dir):
        self.model_path = os.path.join(models_dir, model_name)
        self.model_name = model_name
        self.model = None

    @time_this
    def create_model (self, label_lines = False, size = 300):
        """Creates a model and builds vocab via a SentenceLabels object."""
        self.model = gensim.models.doc2vec.Doc2Vec(\
                        size = size, \
                        min_count = 5, \
                        alpha = 0.025, \
                        min_alpha = 0.025, \
                        workers = cores)
        sentences = SentenceLabels(label_lines = label_lines)
        self.model.build_vocab(sentences)

        for epoch in range(10):
            sentences = SentenceLabels(label_lines = label_lines)
            print 'Beginning Epoch: %s' % (epoch + 1)
            self.model.train(sentences)
            self.model.alpha -= 0.002 
            self.model.min_alpha = self.model.alpha

        self.model.save(self.model_path)

    def save_model (self):  
        self.model.save(self.model_path)

    @time_this
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

