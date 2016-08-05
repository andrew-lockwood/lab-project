
from bs4 import BeautifulSoup
import config 
import util
import csv
import sys
import re
import os

reload(sys)
sys.setdefaultencoding('utf-8')

##############################################################################
# 
# Goes through all the articles in the title set, grabs the text from each 
# XML file, and appends it to a new text file. create_corpus actually creates 
# the file 'mycorpus', while process_corpus parses that file however the user 
# likes
# 
##############################################################################

class CreateCorpus (object): 
    def __init__ (self, numkeys, keytype = 'keywords', \
            file_title = 'mycorpus'):
        self.file_title = file_title
        self.corpus = os.path.join(config.cDir, self.file_title + '.txt')
        self.numkeys = str(numkeys)
        self.keytype = keytype

        f = 'titleSetFrom' + self.numkeys + self.keytype + '.csv'
        d = os.path.join(config.oDir, f)
        self.total_articles = 0
        for line in csv.reader(open(d)):
            self.total_articles += 1

    def create_corpus (self):
        def load_title_file (self): 
            self.file_list = []
            f = 'titleSetFrom' + self.numkeys + self.keytype + '.csv'
            d = os.path.join(config.oDir, f)
            for line in csv.reader(open(d)):
                self.file_list.append(line[0])
            self.total_articles = len(self.file_list)   
         
        load_title_file(self)

        i = 0
        l = self.total_articles
        util.printInfo(i, l)

        with open(self.corpus, 'w') as f:
            for file in self.file_list:
                year = ''
                for x in range(4): year += file[x] 
                file_dir = os.path.join(config.rDir, year, file)
                xml_data = open(file_dir, 'r')
                soup = BeautifulSoup(xml_data, 'lxml')
                for text in soup.find_all('p'):
                    f.write(text.get_text() + '\n')
                i += 1
                util.printInfo(i, l) 

    def __iter__ (self): 
        with open(self.corpus) as f: 
            for line in f.readlines():
                yield line

    def print_corpus_info (self): 
        print   self.file_title + " currently contains " + \
                str(self.total_articles) + " articles"

    def process_corpus (self): 
        current_size = os.path.getsize(self.corpus)

        print   'current size of corpus is ' + \
                str(round(current_size/1000000.0, 2)) + ' MB'
        print 'processing corpus...'

        file_name = os.path.join(config.cDir, 'parsed_' + \
                    self.file_title + '.txt')

        with open(self.corpus) as f: 
            with open(file_name, 'w') as new_f:
                for line in f.readlines():
                    # The parsing can be changed here
                    # Currently it makes everything lowercase and removes 
                    # punctuation -- any of irregularies are ignored by 
                    # the word2vec min_count argument 
                    line = line.lower()
                    new_f.write(re.sub("[^a-z \n]","", line))

        new_size = os.path.getsize(file_name)
        x = (new_size/float(current_size)) * 100

        print 'finished processing!'
        print   'new size of the processed corpus is ' + \
                str(round(new_size/1000000.0, 2)) + ' MB (' + \
                str(round(x, 1)) + '% of original)'
