

import sqlite3
from context import settings
import matplotlib.pyplot as plt
from collections import Counter


conn = sqlite3.connect(settings.db)
curr = conn.cursor()


class KeywordData():
    def kwd_grams(self, distinct):
        if distinct:
            curr.execute("SELECT DISTINCT(keyword) FROM OriginalKeywords")
        else:
            curr.execute("SELECT keyword FROM OriginalKeywords")

        c = Counter()

        for keyword in curr.fetchall():
            c[len(keyword[0].split())] += 1

        return c 
