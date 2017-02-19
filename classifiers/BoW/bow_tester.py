

from sklearn.naive_bayes import MultinomialNB
from sklearn.cross_validation import KFold
from sklearn.metrics import confusion_matrix, f1_score
from sklearn.feature_extraction.text import CountVectorizer
from time import time
from context import DataLoader
import numpy as np

def run_bow_classifier(vectors, targets):
    k_fold = KFold(n=len(targets), n_folds=5)
    scores = []
    confusion = np.array([[0, 0], [0, 0]])

    for train_indices, test_indices in k_fold:
        train_vecs = [vectors[i] for i in train_indices] 
        train_y = [targets[i] for i in train_indices]

        test_vecs = [vectors[i] for i in test_indices] 
        test_y = [targets[i] for i in test_indices] 

        gnb = MultinomialNB()
        gnb.fit(train_vecs, train_y)
        predictions = gnb.predict(test_vecs)
        confusion += confusion_matrix(test_y, predictions)
        score = f1_score(test_y, predictions, pos_label='1')
        scores.append(score)

    avg_score = sum(scores)/len(scores)

    return (len(vectors), avg_score, confusion)


if __name__ == '__main__':

	print("Loading text with common keywords...")
	t0 = time()
	dl = DataLoader(70)
	text = dl.load_text()

	print("Creating tf_model... ")
	tf_model = CountVectorizer()
	#tf_model.fit(text.values())


	print("Fitting test set")
	dl.analyze("emotion")

	titles = dl.get_title_dict()

	#vectors = tf_model.fit_transform([text[k] for k,v in titles])

	#targets = [v for k,v in titles]

	vectors = []

	gnb = MultinomialNB()
    gnb.fit(train_vecs, train_y)

	run_bow_classifier(vectors, targets)
	print("Time Elapsed: " + str(time()-t0))
