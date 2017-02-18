# Class that iterates over full text documents -- in corpus/document_iterator
from context import Documents 

from sklearn.feature_extraction.text import CountVectorizer
import pickle
from time import time


class BoW: 

    def __init__(self): 
        self.model_path = "bagofwordsmodels/bow.pickle"
        self.titles_path = "bagofwordsmodels/titles.pickle"

    def create_model(self):
        t0 = time()

        tf = CountVectorizer(max_df=0.95,min_df=2,stop_words='english')

        titles, text = zip(*Documents(70))

        tf_model = tf.fit_transform(text)
        
        pickle.dump(tf_model, open(self.model_path, "wb"))
        pickle.dump(titles, open(self.titles_path, "wb"))

        print(time() - t0)

    def load_model(self):
        tf_model = pickle.load(open(self.model_path, "rb"))
        titles = pickle.load(open(self.titles_path, "rb"))

        return(titles, tf_model)


if __name__ == '__main__':
    model = BoW()
    model.create_model()
