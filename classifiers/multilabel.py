

from sklearn.preprocessing import MultiLabelBinarizer
from corpusProcessors import DataLoader, txtFiles, KeywordCount
from collections import defaultdict, Counter
from directories import kwd_dir,feature_dir, parsed_articles
import sys
import csv
import os
from sklearn.naive_bayes import BernoulliNB, GaussianNB

from sklearn.multiclass import OneVsRestClassifier

feature_dir =   feature_dir()
kwd_dir = kwd_dir()
data = DataLoader()
import gensim.models

import numpy as np

def title_kwd ():
    title_to_kwd = defaultdict(list)

    kc = KeywordCount()

    i = 0
    for title in txtFiles().title_set():
        sys.stdout.write("\r%d" % i)
        for kwd in data.title_kwd_set(title):
            if kc.get_count(kwd) >= 5:
                title_to_kwd[title].append(kwd)
        i += 1
        sys.stdout.flush()

    sys.stdout.write('\n')

    print ("saving new title_to_kwd")

    path = os.path.join(kwd_dir, "title_to_kwd_greater_than_5.csv") 
    with open(path, 'wt', encoding='utf-8') as f:
        fieldnames = ['title', 'keyword']
        w = csv.DictWriter(f, fieldnames=fieldnames)
        w.writeheader()
        for title, kwds in title_to_kwd.items():
            kwd = ''
            for k in kwds:
                kwd += (k + ' ')
            w.writerow({'title': title, 'keyword': kwd})


def load_title_kwd (n):
    kwddict = defaultdict(list)
    kwddictdir = os.path.join(kwd_dir, 'title_to_kwd_greater_than_'\
                    +str(n)+'.csv')
    with open(kwddictdir, 'rt', encoding='utf-8') as f:
        fieldnames = ['keyword', 'title']
        r = csv.DictReader(f, fieldnames=fieldnames)
        for row in r:
            for title in row['title'].split():
                kwddict[row['keyword']].append(title)

    return kwddict

def run(features, exclude, test):
    model_name = str(features) + 'model'
    model_dir = os.path.join(feature_dir, \
                    str(features), model_name)
    model = gensim.models.doc2vec.Doc2Vec.load(model_dir)


    classif = OneVsRestClassifier(GaussianNB())
    mlb = MultiLabelBinarizer()

    vectors = []
    targets = []
    i = 0
    e = ['title']
    for title in exclude:
        e.append(title)
    for title, kwds in load_title_kwd(5).items():
        if title in e:
            continue

        else:
            vectors.append(model.docvecs[title])
            targets.append(kwds)

    d = np.array(vectors)
    t = mlb.fit_transform(targets)

    classif.fit(d, t)
    testmodel = []
    for title in test: 
        testmodel.append(model.docvecs[title])

    results = []
    for kwds in mlb.inverse_transform(classif.predict(testmodel)):
        results.append(kwds)
    return results

def run_tests():
    features = [50, 100, 300, 500]
    titledict = load_title_kwd(5)

    for f in features:
        print ("testing " + str(f) + " features")
        test = ['2013_00685', '2013_00203']
        exclude = [] 

        e_results = run(f, test, test)
        i_results = run(f, exclude, test)

        v_kwds = []
        
        for title in test: 
             v_kwds.append(titledict[title])

        a_kwds = []
        for title in test: 
            for key, value in data.title_to_kwd(title).items():
                 a_kwds.append(value)

        for i, t in enumerate(test):
            print("--- article: "+t+ " ---")
            sys.stdout.write("exclude: ")
            for kwd in sorted(e_results[i]):
                sys.stdout.write(kwd+', ')
            sys.stdout.write('\n')

            sys.stdout.write("include: ")
            for kwd in sorted(i_results[i]):
                sys.stdout.write(kwd+', ')
            sys.stdout.write('\n')

            sys.stdout.write("kwds>5:  ")
            for kwd in sorted(v_kwds[i]):
                sys.stdout.write(kwd+', ')
            sys.stdout.write('\n')

            sys.stdout.write("actual:  ")
            for kwd in sorted(a_kwds[i]):
                sys.stdout.write(kwd+', ')
            sys.stdout.write('\n')


run_tests()
parsed_dir =    parsed_articles()


def word_count(title):
        c = Counter()
        title_path = os.path.join(parsed_dir, title + '.txt')

        with open(title_path, 'r') as f:
            for line in f.readlines():
                for word in line.split():
                    c[word] += 1

        print (c.most_common(100))

#word_count('2016_00343')

