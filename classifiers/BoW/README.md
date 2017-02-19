
Needs finishing. The code will look almost identical to `d2v_tester.py` except for using a multinomial Naive Bayes.  

Right now the issue is saving and loading the model, as well as only using a subset of a CountVectorizer.  It's easy enough to implement using a pipeline, but trying to force feed the right vectors makes sklearn angry.  
