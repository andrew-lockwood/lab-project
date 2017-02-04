# Database
import sqlite3

# Time
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


def OriginalKeywords():
    q = """CREATE TABLE OriginalKeywords(
                articleID   TEXT,
                keyword     TEXT,
                FOREIGN KEY(articleID) 
                REFERENCES ArticleInformation(articleID))   """

    curr.execute(q)
    conn.commit()


def process_file(args):
    file, q = args
    with open(os.path.join(settings.xml, file)) as xml:
        soup = BeautifulSoup(xml, 'lxml')
        kwds = soup.find_all('kwd')

        if len(kwds) != 0:
            try:
                articleID = re.sub('10.3389/', '',
                                   soup.find('article-id').get_text())
                data = []
                for kwd in kwds:
                    keyword = ''.join(i if ord(i) < 128 else '' 
                                        for i in kwd.get_text())
                    data.append((articleID, keyword))
                q.put(data)
                return data

            except AttributeError:
                return


if __name__ == "__main__":
    conn = sqlite3.connect(settings.db)
    curr = conn.cursor()

    #OriginalKeywords()

    multi = True

    if multi: 
        p = Pool(4)
        m = Manager()
        q = m.Queue()

        files = [(f, q) for f in os.listdir(settings.xml)]

        results = p.map_async(process_file, files[1000:])

        while True:
            if results.ready():
                break
            else:
                size = q.qsize()
                sys.stdout.write("on file: %i \r"%size)
                time.sleep(0.3)
                sys.stdout.flush()


        output = results.get()

        for row in output: 
            if row != None: 
                for t in row:
                    try:
                        curr.execute("""INSERT INTO OriginalKeywords 
                                        VALUES (?, ?)""", t)
                    except ValueError:
                        continue 
                    except sqlite3.IntegrityError:
                        continue

        conn.commit()
