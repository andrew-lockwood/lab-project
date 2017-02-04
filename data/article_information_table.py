
import sqlite3
from context import settings, ProgressBar


from bs4 import BeautifulSoup
import urllib.request
import multiprocessing
import datetime

import re
import os
import operator
from nltk.stem.porter import *

def ArticleInformation():
    data = []
    files = os.listdir(settings.xml)
    pb = ProgressBar(len(files))

    for file in files:
        pb.step()
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


if __name__ == "__main__":
    conn = sqlite3.connect(settings.db)
    curr = conn.cursor()
    ArticleInformation()