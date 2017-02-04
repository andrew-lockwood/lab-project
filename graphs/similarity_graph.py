import matplotlib.pyplot as plt 
import gensim.models  
from sklearn.metrics.pairwise import cosine_similarity
import sqlite3

from context import settings


model = gensim.models.Word2Vec.load(settings.model)

def random_title():
    """Fetches a random title from the frontiers database"""
    q = """ SELECT  ArticleID
            FROM    ArticleInformation
            ORDER BY RANDOM()
            LIMIT 1                 """

    curr.execute(q)

    title = curr.fetchall()[0][0]

    return title


def title_keywords(title):
    """Given a title, returns every author assigned keyword"""
    q = """ SELECT  GROUP_CONCAT(keyword)
            FROM    OriginalKeywords
            WHERE   ArticleID='{t}'""".format(t=title)

    curr.execute(q)

    return curr.fetchall()[0][0].split(',')


def title_to_titles(n):
    rt = random_title()


    #print(title_keywords(rt))

    sims = [(i+1, score[1]) for i, score in enumerate(
                            model.docvecs.most_similar([rt], topn=n))]
    
    #for title in model.docvecs.most_similar([rt], topn=3):
    #    print(title_keywords(title[0]))

    return (sims, rt)

def title_to_words(n):
    rt = random_title()

    print(title_keywords(rt))


    title_keywords(rt)
    vec = model.docvecs[rt]

    sims = [score for score in model.most_similar([vec], topn=n)]
    
    #for title in model.docvecs.most_similar([rt], topn=3):
    #    print(title_keywords(title[0]))

    return (sims, rt)


def word_sims(word):
    vec = model[word]

    sims = [score for score in model.most_similar([vec], topn=n)]

    print(sims)


def author_kwd_sims():
    rt = random_title()

    titlevec = model.docvecs[rt]

    wordlist = set()

    print(title_keywords(rt))

    for kwd in title_keywords(rt):
        for word in kwd.split():
            wordlist.add(word)

    veclist = []
    vecwordlist = []

    for word in wordlist:
        try:
            veclist.append(model[word])
            vecwordlist.append(word)
        except KeyError as e:
            continue

    titlevec.reshape(1,-1)
    print(cosine_similarity(titlevec, veclist))
    print(vecwordlist)
    """
    print(words)
    for word in words.split():
        print(word)
        wordlist.add(word)
    """
    print(wordlist)

if __name__ == "__main__":
    conn = sqlite3.connect(settings.db)
    curr = conn.cursor()

    #author_kwd_sims()

    n = 30

    similar = title_to_words(n)
    print(similar)
    #print(*zip(*similar[0]))
    """
    plt.scatter(*zip(*similar[0]))
    plt.xlim(0, n+1)
    plt.title(similar[1])
    plt.show()
    """