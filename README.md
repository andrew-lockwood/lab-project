
# Building a Better Keyword Classifier 
### The Corpus 
The corpus as of now contains **6561** articles from 2010-01-15 until 2016-06-23.  More articles have been put out since then and could be incorporated later.  

Of these articles, **6360** have keywords assigned to them.  The other 201 were ruled out. 

Among articles with keywords assigned, the min and max assignments are **1** and **14** with the average being **5.75**. Therefore, any classifier that assigns between 4 and 7 is on the right track (since the variance of those assignments is **1.5**).

## Approaches
### Naive-Bayes Classifier
This can be done in a single or multi lable fashion. The latter trains a classifier for each label whereas the former only does it once.  

Scikit learn expects the input to be vectorized. In this approach we compare feeding it a bag of words vs document vectors to see if there is any information encoded in document vectors that are missing from bag of words.  Ideally, since doc2vec looks at the entire corpus there is additional information.

### Cosine Similarity Between Document and Word Vectors 

Word2vec is able to discover interesting semantic relationships. The classic example uses analogies
`king is to queen as man is to woman`

However, does the relationship between documents and word vectors have any meaning? For example, a paper about emotion in theory should be related the word emotion. 

The benefits of this approach are enormous. In the Naive-Bayes approach, the classifier can never make an assignments outside of the labels. In this approach, if the word appears in the corpus its a candidate for a keyword.  

There are several drawbacks that need to be addressed. 1) The training set can't be stemmed, but the results might have to 2) it can't find any unigrams without additional fine-tuning (see graphs for the "gram-ness" of the original keywords).
