
import sqlite3

import settings


def find_subsets():
    unigram_redirect = []
    bigram_original = []

    q = """ SELECT  keyword, redirect
            FROM    KeywordForms
            WHERE   redirect!='NULL' """

    sameCount = 0
    diffCount = 0
    totalCount = 0
    for t in curr.execute(q).fetchall():
        if t[0] != t[1]:
            diffCount += 1
        else:
            sameCount += 1

    print(diffCount)
    print(sameCount)

if __name__ == "__main__":
    conn = sqlite3.connect(settings.db)
    curr = conn.cursor()
    find_subsets()