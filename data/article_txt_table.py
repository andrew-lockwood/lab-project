
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


def ArticleTXT():
    q = """CREATE TABLE ArticleTXT(
                articleID   TEXT,
                txt         TEXT,
                wordcount   INTEGER, 
                linecount   INTEGER,
                FOREIGN KEY(articleID) 
                REFERENCES ArticleInformation(articleID))   """

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

            t = (articleID, txt, wordcount, linecount)
            q.put(t)
            return t

        except AttributeError:
            return
        except sqlite3.IntegrityError:
            return 


if __name__ == "__main__":
    conn = sqlite3.connect(settings.db)
    curr = conn.cursor()

    #ArticleTXT()

    multi = True

    if multi: 
        p = Pool(4)
        m = Manager()
        q = m.Queue()

        files = [(f, q) for f in os.listdir(settings.xml)]

        results = p.map_async(process_file, files[10:])

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
                curr.execute("""INSERT INTO ArticleTXT 
                                VALUES (?, ?, ?, ?)""", row)
            except ValueError:
                continue 
            except sqlite3.IntegrityError:
                continue

        conn.commit()


