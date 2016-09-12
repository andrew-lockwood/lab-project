# Only needs to be ran once for creating a histogram of the data later on 
# Make sure the load path is correct at the top of binnedHistogram when used
root_dir =      '/media/removable/SD Card/frontiers_data/'
score_dir =     '/media/removable/SD Card/frontiers_data/models/word2vec_scores'
# if using doc2vec
#score_dir =    '/media/removable/SD Card/frontiers_data/models/doc2vec_scores'
article_dir =   '/media/removable/SD Card/frontiers_data/article_txt/'
data_dir =      '/media/removable/SD Card/frontiers_data/data'

# Beautiful soup is required for xml_to_txt to work. It parses xml files 
# rather nicely and makes getting text easy. Sentences has to also be 
# imported from runWord2Vec, as the histogram creator takes data from 
# that file as well. 
from runWord2Vec import Sentences

from bs4 import BeautifulSoup

from collections import Counter, defaultdict
import csv
import sys
import os
import re

reload(sys)
sys.setdefaultencoding('utf-8')

def time_this(original_function):      
    def new_function(*args,**kwargs):
        import datetime                 
        before = datetime.datetime.now()                     
        x = original_function(*args,**kwargs)                
        after = datetime.datetime.now()                      
        print "Elapsed Time = {0}".format(after-before)      
        return x                                             
    return new_function

class xmlFiles (object): 
    def __init__ (self, xml_folder = 'article_xml'): 
        self.path = os.path.join (root_dir, xml_folder)
        self.xml_dirs = []
        for xml_file in os.listdir(self.path): 
            self.xml_dirs.append(xml_file)

    def __iter__ (self): 
        for xml_file in self.xml_dirs:
            yield os.path.join(self.path, xml_file)

    def total_files (self): 
        return len(self.xml_dirs)

    def xml_dir (self): 
        return self.path

class txtFiles (object): 
    def __init__ (self, txt_folder = 'article_txt'): 
        path = os.path.join (root_dir, txt_folder)
        self.txt_dirs = []
        for txt_file in os.listdir(path): 
            self.txt_dirs.append(txt_file)

    def __iter__ (self): 
        for txt_file in self.txt_dirs:
            yield txt_file

    def total_files (self): 
        return len(self.txt_dirs)  

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
        save_path = os.path.join(data_dir, 'word_data', 'word_count.csv')
        with open(save_path, 'wb') as f: 
            w = csv.writer(f)
            for word, frequency in c.iteritems(): 
                frequency_file.writerow([word, frequency])

class KeywordProcessing (object):
    def __init__ (self): 
        self.xml_files = xmlFiles()

    def save_dict (self, d, fname):
        """Saves title and keyword dictionaries."""
        save_path = os.path.join(data_dir, 'kwd_data', fname) 
        with open(save_path, 'wb') as f:
            w = csv.writer(f)
            for key, value in d.iteritems():
                w.writerow([key, value])

    @time_this
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

    @time_this
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

    @time_this
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
        save_path = os.path.join(data_dir, 'kwd_data', 'kwd_counter.csv') 
        with open(save_path, 'wb') as f:
            w = csv.writer(f)
            for key, value in c.most_common():
                w.writerow([key, value])

kp = KeywordProcessing()
#kp.title_to_kwd()
#kp.kwd_to_title()
kp.kwd_counter()


def rm_broken_articles (root_dir = root_dir): 
    articles = []
    path = os.path.join(root_dir, 'broken_articles.txt')

    broken_articles = open(path, 'r')

    for article in broken_articles: 
        articles.append(article)

    for article in articles: 
        # clean up xml files 
        xmlfile = os.path.join(root_dir, article[:4], article[:10] + '.xml')
        os.remove(xmlfile)
        # clean up txt files 
        txtfile = os.path.join(root_dir, 'article_txt', article[:10] + '.txt')
        os.remove(txtfile)

base_url =      'http://journal.frontiersin.org/article/10.3389/fpsyg.'
import requests

reload(sys)
sys.setdefaultencoding('utf-8')

def retry_broken_articles (root_dir = root_dir): 
    articles = []
    path = os.path.join(root_dir, 'broken_articles.txt')

    broken_articles = open(path, 'r')

    for article in broken_articles: 
        articles.append(article[:10])

    i = 0
    for article in articles:
        xml = base_url + article[:4] + '.' + article[-5:] + '/xml'
        file = os.path.join(root_dir, 'broken_articles', article + '.xml')
        with open((file), 'w') as f: 
            r = requests.get(xml)
            f.write(r.content)
            i += 1
            sys.stdout.write('\rFiles Written: %s' % i)
            sys.stdout.flush()



def kwd_analysis (root_dir = root_dir): 
    i = 1
    titles = []
    c = Counter()

    for path, dirs, files in os.walk(root_dir):
        for file in files: 
            if '.xml' in file:
                if i % 10 == 0:
                    sys.stdout.write('\rFile Number: %s' % i)
                with open(os.path.join(path, file)) as xml: 
                    soup = BeautifulSoup(xml, 'lxml')
                    title = re.sub('.xml', '', file)
                    if len(soup.find_all('kwd')) == 0: 
                        c['NULL'] += 1
                        titles.append(title)
                        for s in soup.find_all('subject'): 
                            c[s] += 1
                i += 1
                sys.stdout.flush()

    print 'Saving keyword analysis'
    save_path = os.path.join(data_dir, 'kwd_data', 'kwd_analysis.csv') 
    w = csv.writer(open(save_path , 'w'))
    w.writerow([len(title)])
    for title in titles: 
        w.writerow([title])
    for key, value in c.iteritems():
        w.writerow([key, value])   

# Call these two methods once
#create_frequency_dict()
#xml_to_txt()
#title_to_kwd()
#kwd_analysis()
#rm_broken_articles()
#retry_broken_articles()
#find_kwdless_articles()

#move_articles()