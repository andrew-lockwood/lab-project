Tables were acquired using keywords with occurences of more than 70 times (original authoer assignment).  

Each word was ran 100 times through a classifier, with the negative papers changing each time.  The CSV files have the mean, median, and variance of the f1_scores, true positive, true negative, false positive, false negatives.  

These are fairly quick to run, so if you more informatiion is needed (precision/recall/column averages), they can be implemented.  

Dependencies -- 
1. sklearn/gensim/python 3 (I'm fairly certain this would run on python 2 since I used all these packages with 2, I just have not tried it)
2. trained Doc2Vec models (should be sent)
3. From this project 
a. settings -- controls the location of where the models are stored
b. DataLoader -- interfaces with the database to grab relevant papers for testing. The articleIDs are the same across doc2vec models/database. 

To change the model tested -- Right now it is set up to test the size 500 model, just change the loaded model and the results location to look at a different model.

