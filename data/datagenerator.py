from bs4 import BeautifulSoup

import urllib.request
import multiprocessing
import datetime

from dbinterface import DatabaseInterface

import re
import os
import operator
from nltk.stem.porter import *

xml = "C:\\Users\\Andrew\\Desktop\\frontiers_data\\article_xml"

class Article (object):
    """Holds data about tables related to Articles.

    Allows for quick swapping of database/primary table names without going
    into classes that handle actually extracting the information.

    Attributes:
        di: A DatabaseInterface object handling I/O
        tn: the name of the main table holding the primary key. Each table 
            related to articles will reference this key.

    """

    def __init__(self, database="frontiers_corpus"):
        self.di = DatabaseInterface(database)
        self.tn = "ArticleInformation"

    def schema(self):
        """Displays the schema on the command line."""
        self.di.print_schema()

    def query(self, q):

        return self.di.execute_query(q)

    def create_article_table(self):
        """Tuple Signature:
            ArticleInformation(articleID, date, type, title)
        """
        self.di.add_primary_table(self.tn, "articleID", "TEXT")

        self.di.add_column(self.tn, 'date', 'TEXT')
        self.di.add_column(self.tn, 'type', 'TEXT')
        self.di.add_column(self.tn, 'title', 'TEXT')

    def insert_article_data(self):
        """Pulls data from already downloaded XML files."""
        #files = xmlFiles()
        files = []
        pb = ProgressBar(len(files))

        for file in files:
            pb.step()
            with open(file) as xml:
                soup = BeautifulSoup(xml, 'lxml')
                try:
                    articleID = re.sub('10.3389/', '',
                                       soup.find('article-id').get_text())

                    # Can be either accepted or received
                    #d = soup.find(attrs={"date-type":"accepted"})
                    d = soup.find(attrs={"date-type": "received"})
                    day = d.find('day').get_text()
                    month = d.find('month').get_text()
                    year = d.find('year').get_text()

                    # Standardizes the date format to "YYYY-MM-DD"
                    # Confirms days/months have a leading zero
                    if len(day) == 1:
                        day = '0' + day
                    if len(month) == 1:
                        month = '0' + month
                    if len(year) == 2:
                        year = '20' + year

                    date = '%s-%s-%s' % (year, month, day)

                    article_type = re.sub('-', ' ', soup.find('article')
                                          .get('article-type'))

                    # Removes all non-ascii characters/spaces greater
                    # than 1 from the title
                    title = ''.join([i if ord(i) < 128 else ' ' for i in
                                     soup.find('article-title').get_text()])
                    title = re.sub(' +', ' ', title)

                    # Assembles the tuple
                    t = (articleID, date, article_type, title)
                    self.di.insert_row(self.tn, t)

                except AttributeError:
                    continue
                except sqlite3.IntegrityError:
                    continue


class OriginalKeywords (Article):

    def __init__(self):
        Article.__init__(self)
        self.ft = "OriginalKeywords"

    def create_keyword_table(self):
        self.di.add_related_table(self.ft, "articleID", "TEXT", self.tn)
        self.di.add_column(self.ft, "keyword", "TEXT")

    def insert_keyword_data(self):
        files = xmlFiles()
        pb = ProgressBar(len(files))
        for file in files:
            pb.step()
            with open(file) as xml:
                soup = BeautifulSoup(xml, 'lxml')
                kwds = soup.find_all('kwd')

                if len(kwds) != 0:
                    try:
                        articleID = re.sub('10.3389/', '',
                                           soup.find('article-id').get_text())
                        for kwd in kwds:
                            t = (articleID, kwd.get_text())
                            self.di.insert_row(self.ft, t)
                    except AttributeError:
                        continue
                    except UnicodeEncodeError:
                        print('unicode error')
                    except sqlite3.IntegrityError:
                        print('kwd err: ' + file)


class KeywordForms (Article):

    def __init__(self):
        Article.__init__(self)
        self.primary = "OriginalKeywords"
        self.reference = "KeywordForms"

    def create_form_table(self):
        self.di.add_related_table(self.reference, "keyword", "TEXT", 
                                  self.primary)

        self.di.add_column(self.reference, "parse", "TEXT")
        self.di.add_column(self.reference, "redirect", "TEXT")
        self.di.add_column(self.reference, "stem", "TEXT")

    def process_kwd(self, kwd):
        temp1 = ''.join(i if ord(i) < 128 else ' ' for i in kwd.lower())
        parse_kwd = re.sub('[ -]', '_', temp1)

        try:
            with urllib.request.urlopen(self.baseurl + parse_kwd) as response:
                # Read the html of the url that was found
                html = response.read()
                soup = BeautifulSoup(html, 'html.parser')

                # Every title has the format "title - Wikipedia"
                redirect = re.sub(' - Wikipedia', '',
                                  soup.title.get_text()).lower()

        except urllib.error.URLError as e:
            redirect = "NULL"
        except urllib.error.HTTPError as e:
            redirect = "NULL"

        temp2 = []
        for word in parse_kwd.split("_"):
            temp2.append(self.stemmer.stem(word))

        stem_kwd = " ".join(temp2)

        t = (kwd, parse_kwd, redirect, stem_kwd)
        return t

    def find_kwd_forms(self):
        q = "SELECT  DISTINCT keyword FROM OriginalKeywords"
        self.baseurl = 'https://en.wikipedia.org/wiki/'
        self.stemmer = PorterStemmer()
        kwds = []
        for kwd in self.di.execute_query(q):
            kwds.append(kwd[0])
        before = datetime.datetime.now()
        results = multiprocessing.Pool(8).map(self.process_kwd, kwds)
        after = datetime.datetime.now()
        print("Elapsed Time = {0}".format(after - before))

        before = datetime.datetime.now()
        self.di.bulk_insert_row(self.reference, results)
        after = datetime.datetime.now()
        print("Elapsed Time = {0}".format(after - before))


    def faulty_redirects(self):
        q = """ SELECT  count(redirect) 
                FROM    KeywordForms 
                WHERE   redirect='NULL'"""
        print (self.di.execute_query(q))

    def distint_counts(self):
        q = """ SELECT      redirect, count(DISTINCT articleID)
                FROM        OriginalKeywords NATURAL JOIN KeywordForms
                GROUP BY    redirect
                HAVING      count(DISTINCT articleID) >= 30"""

        for t in self.di.execute_query(q):
            temp = ''.join(i if ord(i) < 128 else ' ' for i in t[0].lower())
            q2 = """SELECT count(articleID) 
                    FROM OriginalKeywords
                    WHERE keyword = '{red}' """.format(red=t[0])
            count = self.di.execute_query(q2)[0][0]
            if count != t[1]:
                print ("%s, %s, %s"%(temp, t[1], count))

        """
        for t in self.di.execute_query(q):
            temp1 = ''.join(i if ord(i) < 128 else ' ' for i in t[0])
            print ("%s, %s, %s" % (temp1, t[1], t[2]))
        """


class ArticleTXT (Article): 

    def __init__ (self):
        Article.__init__(self)
        self.primary = "ArticleInformation"
        self.reference = "ArticleTXT"


    def create_text_table(self):
        self.di.add_related_table(self.reference, "articleID", "TEXT", 
                                  self.primary)

        self.di.add_column(self.reference, "wordcount", "INTEGER")
        self.di.add_column(self.reference, "linecount", "INTEGER")
        self.di.add_column(self.reference, "txt", "TEXT")

    def process_article(self, articleID):
        year = articleID[6:10]
        num = articleID[11:16]
        article = os.path.join(self.basepath, year+'_'+num+'.xml')

        with open(article) as xml: 
            soup = BeautifulSoup(xml, 'lxml')
            wordcount = 0
            linecount = 0
            lines = []
            for line in soup.find_all('p'):
                temp = ''.join(i if ord(i) < 128 else '' for i in line.get_text())
                lines.append(temp)
                linecount += 1
                for word in temp.split():
                    wordcount += 1

            txt = " ".join(lines)

        t = (articleID, wordcount, linecount, txt)
        return t

    def find_full_text(self):
        q = "SELECT  DISTINCT articleID FROM OriginalKeywords"
        self.basepath = "C:\\Users\\Andrew\\Desktop\\frontiers_data\\article_xml"
        articles = []
        for articleID in self.di.execute_query(q):
            articles.append(articleID[0])

        before = datetime.datetime.now()
        results = multiprocessing.Pool(8).map(self.process_article, articles)
        after = datetime.datetime.now()
        print("Elapsed Time = {0}".format(after - before))

        before = datetime.datetime.now()
        self.di.bulk_insert_row_txt(results)
        after = datetime.datetime.now()
        print("Elapsed Time = {0}".format(after - before))


    def get_text(self):
        q = "SELECT  articleID, wordcount, linecount FROM ArticleTXT"

        a = self.di.execute_query(q)
        a.sort(key=operator.itemgetter(1))

        for row in a:
            print (row)








timing = False


if __name__ == "__main__":
    pass