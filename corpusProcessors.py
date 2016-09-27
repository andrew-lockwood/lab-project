# Only needs to be ran once for creating a histogram of the data later on 
# Make sure the load path is correct at the top of binnedHistogram when used
root_dir =      '/media/removable/SD Card/frontiers_data/'
data_dir =      '/media/removable/SD Card/frontiers_data/data'
kwd_dir =       '/media/removable/SD Card/frontiers_data/data/kwd_data'
word_dir =      '/media/removable/SD Card/frontiers_data/data/word_data'

# Beautiful soup is required for xml_to_txt to work. It parses xml files 
# rather nicely and makes getting text easy. Sentences has to also be 
# imported from runWord2Vec, as the histogram creator takes data from 
# that file as well. 

from bs4 import BeautifulSoup

from runWord2Vec import Sentences
from util import time_this

from collections import Counter, defaultdict
import csv
import sys
import os
import re

reload(sys)
sys.setdefaultencoding('utf-8')

class wordProcessor (object):
    def frequency_dictionary (self): 
        i = 1 
        print 'creating word frequency counter'
        sentences = Sentences()
        c = Counter()
        for sentence in sentences: 
            for word in sentence: 
                if i % 10000 == 0:
                    sys.stdout.write('\rAt word: %s ' % i)
                c[word] += 1
                i += 1
                sys.stdout.flush()
        sys.stdout.write('\n')
        print 'total words counted: %s' % i
        
        print 'saving word frequency counter'
        save_path = os.path.join(word_dir, 'word_count.csv')
        with open(save_path, 'wb') as f: 
            w = csv.writer(f)
            for word, frequency in c.iteritems(): 
                frequency_file.writerow([word, frequency])

class txtFiles (object): 
    def __init__ (self, txt_folder = 'article_txt'): 
        self.path = os.path.join (root_dir, txt_folder)
        self.txt_dirs = []
        for txt_file in os.listdir(self.path): 
            self.txt_dirs.append(txt_file)

    def __len__ (self): 
        return len(self.txt_dirs)  

    def __iter__ (self): 
        for txt_file in self.txt_dirs:
            yield txt_file
    
    def title_set (self):
        titles = set()
        for root, dir, files in os.walk(self.path): 
            for file in files: 
                titles.add(re.sub('.txt', '', str(file)))
        return titles

class xmlFiles (object): 
    """Iterates through every XML file in the XML directory."""
    def __init__ (self, xml_folder = 'article_xml'): 
        """Creates a list of XML files on the disk."""
        self.path = os.path.join (root_dir, xml_folder)
        self.xml_dirs = []
        for xml_file in os.listdir(self.path): 
            self.xml_dirs.append(xml_file)

    def __len__ (self): 
        """Returns the number of XML files in the directory."""
        return len(self.xml_dirs)

    def __iter__ (self): 
        """Returns entire paths."""
        for xml_file in self.xml_dirs:
            yield os.path.join(self.path, xml_file)
        
class KeywordProcessor (object):
    """Creates three dictionaries."""
    def __init__ (self): 
        """Creates an XML file object variable."""
        self.txt_files = txtFiles()
        self.title_set = txt_files.title_set()
        self.xml_files = xmlFiles()

    def save_dict (self, d, fname):
        """Saves title and keyword dictionaries."""
        save_path = os.path.join(kwd_dir, fname) 
        with open(save_path, 'wb') as f:
            w = csv.writer(f)
            for key, value in d.iteritems():
                w.writerow([key, value])

    def title_to_kwd (self): 
        """Maps titles to keywords.""" 
        i = 0
        d = defaultdict(list)

        print 'creating title to keyword dictionary'
        for file in self.xml_files:
            i += 1
            if i % 10 == 0:
                sys.stdout.write('\rFile Number: %s' % i)
            with open(file) as xml: 
                soup = BeautifulSoup(xml, 'lxml')
                title =  os.path.basename(os.path.normpath(re.sub('.xml', '', file)))
                if len(soup.find_all('kwd')) == 0: 
                    d[title].append("NULL")
                else:
                    for kwd in soup.find_all('kwd'):
                        d[title].append(kwd.text.lower())
            sys.stdout.flush()
        sys.stdout.write('\n')

        print 'saving title to keyword dictionary'
        self.save_dict(d, 'title_to_kwd.csv')

    def kwd_to_title (self):
        """Maps keywords to titles.""" 
        i = 0
        d = defaultdict(list)

        print 'creating keyword to title dictionary'
        for file in self.xml_files:
            i += 1
            if i % 10 == 0:
                sys.stdout.write('\rFile Number: %s' % i)
            with open(file) as xml: 
                soup = BeautifulSoup(xml, 'lxml')
                title =  os.path.basename(os.path.normpath(re.sub('.xml', '', file)))
                if len(soup.find_all('kwd')) == 0: 
                    d["NULL"].append(title)
                else:
                    for kwd in soup.find_all('kwd'):
                        d[kwd.text.lower()].append(title)
            sys.stdout.flush()
        sys.stdout.write('\n')

        print 'saving keyword to title dictionary'
        self.save_dict(d, 'kwd_to_title.csv')

    def kwd_counter (self): 
        """Creates a keyword counter from every XML file."""
        i = 0
        c = Counter()

        print 'creating keyword counter'
        for file in self.xml_files:
            i += 1
            if i % 10 == 0:
                sys.stdout.write('\rFile Number: %s' % i)
            with open(file) as xml: 
                soup = BeautifulSoup(xml, 'lxml')
                title = os.path.basename(os.path.normpath(re.sub('.xml', '', file)))
                if len(soup.find_all('kwd')) == 0: 
                    c["NULL"] += 1
                else:
                    for kwd in soup.find_all('kwd'):
                        c[kwd.text.lower()] += 1
            sys.stdout.flush()
        sys.stdout.write('\n')

        print 'saving keyword counter'
        save_path = os.path.join(kwd_dir, 'kwd_counter.csv') 
        with open(save_path, 'wb') as f:
            w = csv.writer(f)
            for key, value in c.most_common():
                w.writerow([key, value])

def runKeywordProcessor(): 
    kp = KeywordProcessor()
    kp.title_to_kwd()
    kp.kwd_to_title()
    kp.kwd_counter()

#runKeywordProcessor()
