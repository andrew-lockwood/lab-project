
This experiment uses 2000 articles filtered by whether or not they have frequent, author assigned keywords. Currently, there are 4 different vector representations of the full text of these articles.


1. Classic Bag of Words -- stopwords are automatically removed using sci-kit learn
2. Doc2Vec -- 100/300/500 features

Using a Naive Bayes classifier, with the original author keywords as labels, the Bag of Words vectors performed slightly better than the document vectors.  However, the performance difference was not correlated with the size of the vector -- in terms of efficiency (in my opinion) the document vectors performed good enough.  

Methods for improvement
1. N-grams -- both Bag of Words and d2v miss words like "functional magnetic resonance imaging." Both scikit and gensim have n-gram detectors built in (that use probabiity to find words that co-occur with each other)
2. Standardization -- this work is done, but was NOT used for the initial testing.  A lot of keywords mean the exact same thing, but might be excluded due the frequency cut off. 
3. TF-IDF -- not implemented for BoW yet, but has been consistently proven to improve performance

Possibility for unsupervised clustering -- DBSCAN seems like a more promising approach. Tentative use proved it didn't find any clusters so that will need to be worked on.

filter by greater than 70 - 2214
filter by greater than 0 - 6360

Look into section headings of the other paper -- look into the email


Start with methods and results -- what figures do we need?
write out a paragraph of what figure/table support the results
 -- don't really know what it is when we start

start with best shot of an outline

start pulling together a bibliography --

look up zatero -- free citation manager -- runs inside of firefox

endnote



