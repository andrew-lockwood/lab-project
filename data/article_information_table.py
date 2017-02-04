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


def ArticleInformation():
    q = """CREATE TABLE ArticleInformation(
                articleID   TEXT PRIMARY KEY,
                title       TEXT,
                received    DATE, 
                type        TEXT)"""

    curr.execute(q)
    conn.commit()


def process_file(args):
    """Returns """
    file, q = args
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
            t = (articleID, title, date, article_type)
            q.put(t)
            return t

        except AttributeError:
            return
        except sqlite3.IntegrityError:
            return 


if __name__ == "__main__":
    conn = sqlite3.connect(settings.db)
    curr = conn.cursor()

    #ArticleInformation()

    multi = True

    if multi: 
        p = Pool(4)
        m = Manager()
        q = m.Queue()

        files = [(f, q) for f in os.listdir(settings.xml)]

        results = p.map_async(process_file, files)

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
            try:
                curr.execute("""INSERT INTO ArticleInformation 
                                VALUES (?, ?, ?, ?)""", row)
            except ValueError:
                continue 
            except sqlite3.IntegrityError:
                continue

        conn.commit()
