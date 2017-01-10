import settings
import sqlite3
import numpy as np
import os
from bs4 import BeautifulSoup
import re
import multiprocessing
import time

def process_article(file):
    with open(os.path.join(settings.xml, file)) as xml:
        soup = BeautifulSoup(xml, 'lxml')
        try:
            articleID = re.sub('10.3389/', '',
                               soup.find('article-id').get_text())

            if (''.join([i if ord(i) < 128 else '' for i 
                    in soup.find('abstract').get_text()])) != '':
                return 1
            else:
                return 0
        except AttributeError:
            return 0
        except sqlite3.IntegrityError:
            return 0

def find_articles():
    files = os.listdir(settings.xml)[0:1000]
    count = 0
    start = time.time()
    count = multiprocessing.Pool(8).map(process_article, files)
    print(time.time() - start)
    print(count)
    print(sum(count))

if __name__ == "__main__":
    def adapt_array(arr):
        out = io.BytesIO()
        np.save(out, arr)
        out.seek(0)
        return sqlite3.Binary(out.read())

    def convert_array(text):
        out = io.BytesIO(text)
        out.seek(0)
        return np.load(out)

    sqlite3.register_adapter(np.ndarray, adapt_array)
    sqlite3.register_converter("NUMPY", convert_array)

    conn = sqlite3.connect(settings.db, 
                detect_types=sqlite3.PARSE_DECLTYPES)

    curr = conn.cursor()

    find_articles()

