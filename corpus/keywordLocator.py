

from corpusProcessors import DataLoader
from collections import defaultdict
from util import ProgressBar
data = DataLoader()
import os
from directories import articles, word_dir, parsed_articles
article_dir =   articles()
parsed_dir =    parsed_articles()
word_dir =      os.path.join(word_dir(), 'word_count.csv')
from nltk.stem.porter import *
stemmer = PorterStemmer()



def run():
    data = DataLoader()
    #titles = data.pos_kwd_title_set('emotion')
    titles = ['2010_00033']
    pb = ProgressBar(len(titles))

    dicts = []
    for title in titles:
        kwds = data.title_kwd_set(title)
        stemkwds = []

        for kwd in kwds:
            if '_' in kwd: 
                stemkwd = ''
                for k in re.sub("_", " ", kwd).split(): 
                    stemkwd += stemmer.stem(k) + ' '
                stemkwds.append(stemkwd)
            else:
                stemkwds.append(stemmer.stem(kwd))

        parse_dir = os.path.join(parsed_dir, title + '.txt')

        totalcount = 0
        with open(parse_dir) as f:
            for word in f.readline().split():
                totalcount += 1

        countdict = defaultdict(list)
        for kwd in stemkwds:
            with open(parse_dir) as f:
                if (len(kwd.split()) == 1):
                    for count, word in enumerate(f.readline().split()):
                        if word == kwd: 
                            countdict[kwd].append(round(100*count/float(totalcount), 2))
                else:
                    i = 0
                    splitkwd = kwd.split()
                    kwdsize = len(splitkwd)
                    for count, word in enumerate(f.readline().split()):
                        if word == splitkwd[i]:
                            i += 1
                            if i == kwdsize: 
                                countdict[kwd].append(round(100*count/float(totalcount), 2))
                                i = 0
                        else:
                            i = 0
        dicts.append(countdict)
        pb.step()

    for dictionary in dicts:
        print (dictionary)


"""
total = 0.0
first = 0
for dictionary in dicts: 
    for kwd, appearance in dictionary.items():
        if kwd == 'emot':
            if len(appearance) != 0:
                total += 1
                first += appearance[0]

print (first/total)
"""