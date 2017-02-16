
from context import settings, UnlabeledSentences
import sqlite3

from gensim.models.phrases import Phrases

import re
import operator

import logging
logging.basicConfig(format='%(asctime)s : %(levelname)s : %(message)s', level=logging.INFO)




def load_keywords():
	sentences = UnlabeledSentences()

	bigram = Phrases(sentences)

	trigram = Phrases(bigram[sentences])

	d = dict()

	for phrase, score in trigram.export_phrases(bigram[sentences]):
		d[phrase] = score

	sorted_d = sorted(d.items(), key=operator.itemgetter(1))

	with open("trigrams.txt",'w') as f:
		for key, value in sorted_d:
			f.write(re.sub(" ", "_", key.decode("utf-8")).ljust(50) + " " + str(value) + "\n")


if __name__ == "__main__":
    conn = sqlite3.connect(settings.db)
    curr = conn.cursor()
    load_keywords()