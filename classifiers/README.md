
# Classifiers

`single_label.py` has a method for classifying a block of text (converting them to count --> tfidf vectors) and a method for classifying document vector (with a size of 300).

If everything is loaded properly, running `python single_label.py emotion` will output

```
Running Bag of Words Classifier...
Total articles classified: 448
Score: 0.793345380257
Confusion matrix:
[[119 105]
 [ 10 214]]
--------------------------------
Running Doc2Vec Classifier...
Total articles classified: 448
Score: 0.848805603463
Confusion matrix:
[[197  27]
 [ 38 186]]
done in 30.394s.
```

### Issues to Resolve

1. The two classification strategies need different Naive Bayes methods (bag of words uses Multinomial, doc2vec uses Gaussian). 

Running doc2vec with Multinomial gives the error:

```
ValueError: Input X must be non-negative
```

Where X is the input vector 

Running bag of words with Gaussian gives the error: 

```
TypeError: A sparse matrix was passed, but dense data is required. Use X.toarray() to convert to a dense numpy array.
```

2. Tf-Idf is trained only on the subset of a corpus, whereas do2vec uses the entire corpus 
