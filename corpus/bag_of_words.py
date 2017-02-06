
from sklearn.feature_extraction.text import TfidfTransformer, CountVectorizer
from sentenceiterator import RawDocuments
from time import time

documents = RawDocuments()

t0 = time()


count_vectorizer = CountVectorizer(max_df=0.95, min_df=2, stop_words='english')

train_counts = count_vectorizer.fit_transform(documents)
print(train_counts.shape)

tf_transformer = TfidfTransformer(use_idf=False).fit(train_counts)

train_tf = tf_transformer.transform(train_counts)
print(train_tf.shape)

print("done in %0.3fs." % (time() - t0))
