from context import settings

import sqlite3
import numpy as np
import matplotlib.pyplot as plt

def word_count():
	q = "SELECT wordcount FROM ArticleTXT"
	curr.execute(q)

	counts = np.array([wc[0] for wc in curr.fetchall()])

	plt.hist(counts, bins='auto')
	plt.title("Distribution of Word Counts")
	plt.xlabel("Articles")
	plt.ylabel("Words")
	plt.show()


if __name__ == "__main__":
    conn = sqlite3.connect(settings.db)
    curr = conn.cursor()
    word_count()
