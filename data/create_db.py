import sqlite3
import settings


def ArticleInformation():
    q = """CREATE TABLE ArticleInformation(
                articleID   TEXT PRIMARY KEY,
                title       TEXT,
                received    DATE, 
                type        TEXT)                           """

    curr.execute(q)
    conn.commit()


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


def OriginalKeywords():
    q = """CREATE TABLE OriginalKeywords(
                articleID   TEXT,
                keyword     TEXT,
                FOREIGN KEY(articleID) 
                REFERENCES ArticleInformation(articleID))   """

    curr.execute(q)
    conn.commit()


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


def ArticleVectors():
    q = """CREATE TABLE ArticleVectors(
                articleID   TEXT,
                vector      NUMPY,
                FOREIGN KEY(articleID) 
                REFERENCES ArticleInformation(articleID))   """

    curr.execute(q)
    conn.commit()


if __name__ == "__main__":
    conn = sqlite3.connect(settings.db)
    curr = conn.cursor()

    ArticleInformation()
    ArticleTXT()
    OriginalKeywords()
    KeywordForms()
    ArticleVectors()
