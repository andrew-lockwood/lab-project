import matplotlib.pyplot as plt 
import gensim.models  
import sqlite3

from context import settings


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
    return curr.fetchall()


def similar_titles(n):
    rt = random_title()

    model = gensim.models.Word2Vec.load(settings.model)

    #print(title_keywords(rt))

    sims = [(i+1, score[1]) for i, score in enumerate(
                            model.docvecs.most_similar([rt], topn=n))]
    
    #for title in model.docvecs.most_similar([rt], topn=3):
    #    print(title_keywords(title[0]))

    return (sims, rt)                


if __name__ == "__main__":
    conn = sqlite3.connect(settings.db)
    curr = conn.cursor()

    similar = similar_titles(30)

    plt.scatter(*zip(*similar[0]))
    plt.title(similar[1])
    plt.show()