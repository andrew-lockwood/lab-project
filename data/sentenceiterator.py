
import os
from gensim.models.doc2vec import LabeledSentence
import nltk.data

from dbinterface import DatabaseInterface


class Sentences:
    """Sentences come from the internal database and require tokenization.

    Attributes:
        db: A string identifying the database being queried
    """

    def __init__(self, db="frontiers_corpus"):
        """self.articles[0] must always be the ID, self.articles[1] must
        always be the text."""
        db_dir = "C:\\Users\\Andrew\\Desktop\\lab-project\\data"
        self.di = DatabaseInterface(os.path.join(db_dir,db))


        q = """ SELECT  articleID, txt 
                FROM    articleTXT      """
                #WHERE   articleID='fpsyg.2010.00030'"""  # Set for testing

        self.articles = self.di.execute_query(q)

        self.sent_detector = nltk.data.load(
            'tokenizers\\punkt\\english.pickle')


class UnlabeledSentences(Sentences):
    """Yields a list of lists (sentences and words)."""

    def __init__(self):
        Sentences.__init__(self)

    def __iter__(self):
        """To implement further parsing, change the yield."""
        for article in self.articles:
            text = article[1]
            for line in self.sent_detector.tokenize(text.strip()):
                yield line.split()


class LabeledSentences(Sentences):
    """Yields a LabeledSentence object gensim understands during training.

    Label is simply the articleID
    """

    def __init__(self):
        Sentences.__init__(self)

    def __iter__(self):
        """To implement further parsing, change the words assigned in 
        LabeledSentences."""
        for article in self.articles:
            label = article[0]
            text = article[1]
            for line in self.sent_detector.tokenize(text.strip()):
                yield LabeledSentence(words=line.split(), tags=[label])
