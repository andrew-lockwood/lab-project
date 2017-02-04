
import sqlite3 
from lab_project.util import directories




db = "C:\\Users\\Andrew\\lab_project\\data\\frontiers_corpus.db"

if __name__ == "__main__":
	print(directories.kwd_dir)
	conn = sqlite3.connect(db)
