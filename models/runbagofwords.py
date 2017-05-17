# Class that iterates over full text documents -- in corpus/document_iterator
from context import Documents 
from context import settings

from sklearn.feature_extraction.text import CountVectorizer
from time import time

import pickle
import os


class BagofWords: 
    def __init__(self): 
        self.model_path = os.path.join(settings.bowmodel, "bow.pickle")
        self.titles_path = os.path.join(settings.bowmodel, "titles.pickle")

    def create_model(self):

        t0 = time()

        tf = CountVectorizer(max_df=0.95,min_df=2,stop_words='english')

        titles, text = zip(*Documents(70))

        tf_model = tf.fit_transform(text)
        
        #pickle.dump(tf_model, open(self.model_path, "wb"))
        #pickle.dump(titles, open(self.titles_path, "wb"))

        print(time() - t0)

    def titles(self):
        return pickle.load(open(self.titles_path, "rb"))

    def model(self):
        return pickle.load(open(self.model_path, "rb"))

if __name__ == '__main__':
    bow = BagofWords()
    bow.create_model()