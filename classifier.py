
from sklearn.naivebayes import MultinomialNB
import gensim.models  
import numpy as np


modeldir = '/media/removable/SD Card/frontiers_data/models/doc2vec' 


def trainingvectors ():
	model = gensim.models.doc2vec.Doc2Vec.load(self.model_path)
