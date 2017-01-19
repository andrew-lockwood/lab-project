import sqlite3

import gensim.models  
import settings 
from tabulate import tabulate
import re 
import sys
from nltk.stem.snowball import SnowballStemmer 

stemmer = SnowballStemmer('english')

def title_count(kwd, key):
    stemkwd = stemmer.stem(kwd)

    total = 0

    curr.execute("""SELECT  title 
                    FROM    ArticleInformation 
                    WHERE   articleID='{aid}'""".format(aid=key))
    title = curr.fetchall()
    if len(title) == 1:
        for word in title[0][0].split():
            stemword = stemmer.stem(word)
            if stemword == stemkwd:
                total += 1
    else:
        print(key)
    return total

def kwd_count(kwd, key):
    stemkwd = stemmer.stem(kwd)

    total = 0

    curr.execute("""SELECT  keyword 
                    FROM    OriginalKeywords 
                    WHERE   articleID='{aid}'""".format(aid=key))
    for words in curr.fetchall():
        for word in words[0].split():
            stemword = stemmer.stem(word)
            if stemword == stemkwd:
                total += 1

    return total

def run():
    kwd = "attention"
    model = gensim.models.Word2Vec.load(settings.model)

    n = 2000

    origin = model[kwd]

    word_sims = [('w', word, score) for word, score in 
                    model.most_similar([origin], topn=n)]

    tag_sims = [('t', tag, score) for tag, score in 
                    model.docvecs.most_similar([origin], topn=n)]

    results = sorted((tag_sims),key=lambda tup: -tup[2])

    missing = 0
    k = 0 
    t = 0 

    curr.execute("""SELECT  count(articleID) 
                    FROM    OriginalKeywords
                    WHERE   keyword = '{k}'""".format(k=kwd))

    print(curr.fetchall())

    for i, tup in enumerate(results[:n]):
        #print(tup)
        #if tup[0] == 't':
        key = "fpsyg."+re.sub("_", ".", tup[1])
        tc = title_count(kwd, key)
        kc = kwd_count(kwd, key)

        if tc == 0 and kc == 0:
            missing += 1

        if tc > 0:
            t += 1

        if kc > 0: 
            k += 1
        #    print(str(i) + ". " + str(tc) + " " + str(kc) + " <---")
        #else:
        #    print(str(i) + ". " + str(tc) + " " + str(kc))

    print(str(missing) + " " + str(t) + " " + str(k))

if __name__ == "__main__":
    conn = sqlite3.connect(settings.db)
    curr = conn.cursor()

    run()

