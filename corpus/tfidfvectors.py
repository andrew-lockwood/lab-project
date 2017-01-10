
from sklearn.feature_extraction.text import TfidfVectorizer 
import settings
import sqlite3
import numpy as np

def get_text():
    q = """ SELECT      txt
            FROM        articleTXT
            WHERE       articleID IN
                       (SELECT      articleID
                        FROM        OriginalKeywords    
                        ORDER BY RANDOM() LIMIT 3)"""

    title = curr.execute(q).fetchall()
    #print(title[0][0])
    docs = [title[0][0], title[1][0], title[2][0]]
    tfv = TfidfVectorizer()
    tfv.fit_transform(docs)
    
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

    get_text()

