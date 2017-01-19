class BigramIterator: 
    def __init__(self, db="frontiers_corpus", labeled=False):
        """self.articles[0] must always be the ID, self.articles[1] must
        always be the text."""

        self.bigrams = Phraser(Phrases(RawIterator()))

        db_dir = "C:\\Users\\Andrew\\lab-project\\data"
        self.di = DatabaseInterface(os.path.join(db_dir,db))


        q = """ SELECT  articleID, txt 
                FROM    articleTXT      """
                #WHERE   articleID='fpsyg.2010.00030'"""  # Set for testing

        self.articles = self.di.execute_query(q)

        self.sent_detector = nltk.data.load(
            'tokenizers\\punkt\\english.pickle')

        self.labeled = labeled

    def __iter__(self):
        """To implement further parsing, change the yield."""
        if self.labeled:
            for article in self.articles:
                label = article[0]
                text = article[1]
                for line in self.sent_detector.tokenize(text.strip()):
                    temp = re.sub('-', ' ', line)
                    parsed_line = re.sub('[^a-z ]', '', temp.lower())
                    yield LabeledSentence(words=self.bigrams[parsed_line.split()], tags=[label])

        else:
            for article in self.articles:
                text = article[1]
                for line in self.sent_detector.tokenize(text.strip()):
                    temp = re.sub('-', ' ', line)
                    parsed_line = re.sub('[^a-z ]', '', temp.lower())
                    yield self.bigrams[parsed_line.split()]


class StemIterator: 
    def __init__(self, db="frontiers_corpus", labeled=False):
        """self.articles[0] must always be the ID, self.articles[1] must
        always be the text."""

        db_dir = "C:\\Users\\Andrew\\lab-project\\data"
        self.di = DatabaseInterface(os.path.join(db_dir,db))


        q = """ SELECT  articleID, txt 
                FROM    articleTXT      """
                #WHERE   articleID='fpsyg.2010.00030'"""  # Set for testing

        self.articles = self.di.execute_query(q)

        self.sent_detector = nltk.data.load(
            'tokenizers\\punkt\\english.pickle')

        self.labeled = labeled

        self.stemmer = PorterStemmer()

    def __iter__(self):
        """To implement further parsing, change the yield."""
        for article in self.articles:
            label = article[0]
            text = article[1]
            for line in self.sent_detector.tokenize(text.strip()):
                temp = re.sub('-', ' ', line)
                parsed_line = re.sub('[^a-z ]', '', temp.lower())
                stemmed_line = [self.stemmer.stem(word) for word in parsed_line.split()]
                yield LabeledSentence(words=stemmed_line, tags=[label])
