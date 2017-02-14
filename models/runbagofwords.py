
from context import Documents 
from sklearn.feature_extraction.text import CountVectorizer
import pickle
from time import time

def create_model():
	tf = CountVectorizer(max_df=0.95,min_df=2,stop_words='english')

	titles, text = zip(*Documents())
	vector_dict = {}

	t0 = time()
	tf_model = tf.fit_transform(text)

	for i in range(tf_model.shape[0]):
		vector_dict[titles[i]] = tf_model[i]

	pickle.dump(vector_dict, open("bagofwordsmodels/bow.pickle", "wb"))

	print(time() - t0)

def load_model():
	vector_dict = pickle.load(open("bagofwordsmodels/bow.pickle", "rb"))

	return vector_dict
	for k, v in vector_dict.items():
		print(k)

create_model()
test()