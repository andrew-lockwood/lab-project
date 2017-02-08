
### Corpus 

Both iterators go through the local database and yield sentences.  The document iterator does nothing to the text, while the sentence iterator strips out non-ascii characters and puts everything lower case. 

The bag of words (bow) vectorizer takes the document iterator and converts each document to a Tf-Idf vector for training later.  

TODO:
	1. Convert to bigrams and see if that changes -- only do this when there is an efficient pipeline between tfidf and a classifier
	