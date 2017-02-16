
# Database
import sqlite3

# Time
import datetime
import time

# Text 
from bs4 import BeautifulSoup
import re

# System 
from multiprocessing import Pool, Manager
import sys
import os

# Project 
from context import settings


import urllib.request
import multiprocessing
import datetime


import operator
from nltk.stem.porter import *


def KeywordForms():
    q = """CREATE TABLE KeywordForms(
                keyword     TEXT,
                parse       TEXT,
                stem        TEXT,
                redirect    TEXT,
                FOREIGN KEY(keyword) 
                REFERENCES OriginalKeywords(keyword))       """

    curr.execute(q)
    conn.commit()

stemmer = PorterStemmer()

def process_kwd(args):
    """Returns """
    baseurl = 'https://en.wikipedia.org/wiki/'

    kwd, q = args
    parse_kwd = re.sub('[ -]', '_', kwd.lower())

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
        temp2.append(stemmer.stem(word))

    stem_kwd = " ".join(temp2)

    t = (kwd, parse_kwd, stem_kwd, redirect)
    q.put(t)
    return t


if __name__ == "__main__":
    conn = sqlite3.connect(settings.db)
    curr = conn.cursor()

    #KeywordForms()

    multi = True


    if multi: 
        p = Pool(4)
        m = Manager()
        q = m.Queue()

        curr.execute("""SELECT  DISTINCT keyword 
                        FROM    OriginalKeywords""")
        kwds = [(k[0], q) for k in curr.fetchall()]

        results = p.map_async(process_kwd, kwds[10:])

        while True:
            if results.ready():
                break
            else:
                size = q.qsize()
                sys.stdout.write("on keyword: %i \r"%size)
                time.sleep(0.3)
                sys.stdout.flush()


        output = results.get()

        for row in output: 
            try:
                curr.execute("""INSERT INTO KeywordForms 
                                VALUES (?, ?, ?, ?)""", row)
            except ValueError:
                continue 
            except sqlite3.IntegrityError:
                continue

        conn.commit()
