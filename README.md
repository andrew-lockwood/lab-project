
# Organization

I've tried to improve the sensibility of file organization

classifiers -- contains every related to running and testing classifiers.  The two folders are for the two types of models we will be looking at (bag of words and document vectors). In my opinion, the most important code goes here.  

corpus -- contains everythin relevant to iterating over/grabbing data and sending it to classifiers.  Must have the proper connection to the database or it does nothing.  Has a folder related to n_gram discovery.

database -- pretty much useless after the database has been populated.  Each file is a different table made in the sqlite database.  I have toyed around with making a seperate table for abstracts, but never became useful. As a sanity check when, run print_db_schema to make sure the db is in the right place and functioning (looks to the place where settings.db is pointing).

graphs -- has scripts for creating and displaying graphs.  Not of much use at the moment.  

models -- has everything related to creating and saving models.  This is where the classifiers look to when loading models.  Has folders relating to unsupervised clustering and tf-idf.  

summary_statistics -- similar to graphs, but mostly prints to command line.  

util -- useful functions that didn't really fit elsewhere. settings.py is THE most important file as its how different files in this project find eachother.   



`context.py` is how files in different folders communicate. 