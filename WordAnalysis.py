

# Files that need to be in this folder 
from corpusProcessors import wordProcessor, txtFiles, KeywordProcessor
from util import time_this


from operator import itemgetter 
from tabulate import tabulate
import sys
import csv
import os 
import re

root_dir =      '/media/removable/SD Card/frontiers_data/'
article_dir =   os.path.join(root_dir,'article_txt')
word_dir =      os.path.join(root_dir,'data','word_data',\
                    'word_count.csv')

class KeywordCount (object): 
    def __init__ (self, n):
        self.keywords = KeywordProcessor().get_kwds_greater_than(n)
        self.articles = txtFiles()
        self.run()

    def run (self):
        table = []
        h = ['keyword', 'total', 'in text', 'avg', 'complement']
        for kwd, count in self.keywords.iteritems():
            row = []
            row.append(kwd)
            row.append(count)
            x = self.assigned_count(kwd)[0]
            row.append(x)
            row.append(x/float(count))
            row.append(self.total_count() - x)
            table.append(row)

        table = reversed(sorted(table, key = itemgetter(1)))
        print tabulate(table, headers=h, floatfmt=".3f")


    def assigned_count (self, kwd): 
        """Counts a keyword in papers when it is assigned."""
        positive = self.articles.kwd_title_set(kwd)
        self.kwd = kwd

        count = 0
        null_count = 0
        for title in positive: 
            title_dir = os.path.join(article_dir, title + '.txt')
            with open(title_dir) as file: 
                prevcount = count 
                # Parse line in the same manner when training models
                for line in file.readlines():
                    parsed_line = (re.sub("[^a-z ]","", line.lower()\
                        )).split()
                    for word in parsed_line: 
                        if word == self.kwd: 
                            count += 1
                if count == prevcount: 
                    null_count += 1
                    print title
        print kwd + ": " + str(null_count)
        return [count, null_count]

    def total_count (self): 
        """Loads the total count of a keyword from the disk."""
        x = 0
        with open(word_dir) as f: 
            r = csv.reader(f)
            for word, count in r: 
                if word == self.kwd: 
                    x = int(count)
        return x


KeywordCount(200)
 
"""kwds = ['emotion', 'attention']

for kwd in kwds:
    kc = KeywordCount(kwd)
    kc.countintext()"""