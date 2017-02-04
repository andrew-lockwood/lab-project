import sqlite3
import numpy as np
import io
from context import settings 

from bs4 import BeautifulSoup
import urllib.request
import multiprocessing
import datetime

import re
import os
import operator
from nltk.stem.porter import *


def adapt_np(arr):
    out = io.BytesIO()
    np.save(out, arr)
    out.seek(0)
    return sqlite3.Binary(out.read())


def convert_np(text):
    out = io.BytesIO(text)
    out.seek(0)
    return np.load(out)


sqlite3.register_adapter(np.ndarray, adapt_np)
sqlite3.register_converter("NUMPY", convert_np)


def ArticleInformation():
    data = []
    files = os.listdir(settings.xml)
    #pb = ProgressBar(len(files))

    for file in files:
        #pb.step()
        with open(os.path.join(settings.xml, file)) as xml:
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
                data.append((articleID, date, article_type, title))

            except AttributeError:
                continue
            except sqlite3.IntegrityError:
                continue

    for row in data: 
        curr.execute("""INSERT INTO ArticleInformation 
                        VALUES (?, ?, ?, ?)""", row)

    conn.commit()


def OriginalKeywords():
    data = []
    files = os.listdir(settings.xml)
    #pb = ProgressBar(len(files))

    for file in files:
        #pb.step()
        with open(os.path.join(settings.xml, file)) as xml:
            soup = BeautifulSoup(xml, 'lxml')
            kwds = soup.find_all('kwd')

            if len(kwds) != 0:
                try:
                    articleID = re.sub('10.3389/', '',
                                       soup.find('article-id').get_text())
                    for kwd in kwds:
                        keyword = ''.join(i if ord(i) < 128 else '' 
                                            for i in kwd.get_text())
                        #print((articleID, keyword))
                        data.append((articleID, kwd.get_text()))
                except AttributeError:
                    continue

    for row in data: 
        curr.execute("""INSERT INTO ArticleInformation 
                        VALUES (?, ?)""", row)

    conn.commit()


def KeywordForms():
    baseurl = 'https://en.wikipedia.org/wiki/'
    stemmer = PorterStemmer()

    def process_kwd(kwd):
        parse_kwd = re.sub('[ -]', '_', temp)

        try:
            with urllib.request.urlopen(baseurl+parse_kwd) as response:
                # Read the html of the url that was found
                html = response.read()
                soup = BeautifulSoup(html, 'html.parser')

                # Every title has the format "title - Wikipedia"
                redirect = re.sub(' - Wikipedia', '',
                                  soup.title.get_text()).lower()

        except urllib.error.URLError as e:
            redirect = kwd
        except urllib.error.HTTPError as e:
            redirect = kwd

        temp2 = []
        for word in parse_kwd.split("_"):
            temp2.append(self.stemmer.stem(word))

        stem_kwd = " ".join(temp2)

        return((kwd, parse_kwd, redirect, stem_kwd))

    def find_kwd_forms():
        q = "SELECT DISTINCT keyword FROM OriginalKeywords"

        kwds = []
        for kwd in curr.execute(q).fetchall():
            kwds.append(kwd[0])

        #results = multiprocessing.Pool(8).map(process_kwd, kwds)

        for row in results: 
            curr.execute("""INSERT INTO KeywordForms 
                            VALUES (?, ?, ?, ?)""", row)

        conn.commit()

    find_kwd_forms()


if __name__ == "__main__":
    conn = sqlite3.connect(settings.db)
    curr = conn.cursor()
    #KeywordForms()
