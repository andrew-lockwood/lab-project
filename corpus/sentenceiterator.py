# Two sentenceiterators (labeled and unlabled for doc2vec and word2vec, 
# respectively) that get full text from the local database.  Tags for 
# labeled sentences are the ArticleIDs. 
#
# NLTK sentence detector returns sentences, as opposed to line by line. 
# Preprocessing involves replacing dashes with whitespace, and removing 
# every non alphabetical character (does this on the fly -- data stored
# on disk is raw)

import re

import nltk.data
from gensim.models.doc2vec import LabeledSentence
import sqlite3

from context import settings 

conn = sqlite3.connect(settings.db)
curr = conn.cursor()


class UnlabeledSentences: 
    def __init__(self):
        q = """ SELECT  articleID, txt 
                FROM    articleTXT      """
                #WHERE   articleID='fpsyg.2010.00030'"""  # Set for testing

        curr.execute(q)

        self.articles = curr.fetchall()
        self.sent_detector = nltk.data.load(
            'tokenizers\\punkt\\english.pickle')

    def __iter__(self):
        for article in self.articles:
            text = article[1]
            for line in self.sent_detector.tokenize(text.strip()):
                temp = re.sub('-', ' ', line)
                parsed_line = re.sub('[^a-z ]', '', temp.lower())
                yield parsed_line.split()


class LabeledSentences: 
    def __init__(self):
        q = """ SELECT  articleID, txt 
                FROM    articleTXT      """
                #WHERE   articleID='fpsyg.2010.00030'"""  # Set for testing

        curr.execute(q)

        self.articles = curr.fetchall()
        self.sent_detector = nltk.data.load(
            'tokenizers\\punkt\\english.pickle')

    def __iter__(self):
        for article in self.articles:
            label = article[0]
            text = article[1]
            for line in self.sent_detector.tokenize(text.strip()):
                temp = re.sub('-', ' ', line)
                parsed_line = re.sub('[^a-z ]', '', temp.lower())
                yield LabeledSentence(words=parsed_line.split(), tags=[label])
