# Only needs to be ran once for creating a histogram of the data later on 
# Make sure the load path is correct at the top of binnedHistogram when used
root_dir =      '/media/removable/SD Card/frontiers_data/'
score_dir =     '/media/removable/SD Card/frontiers_data/models/word2vec_scores'
# if using doc2vec
#score_dir =    '/media/removable/SD Card/frontiers_data/models/doc2vec_scores'
article_dir =   '/media/removable/SD Card/frontiers_data/article_txt/'

# Beautiful soup is required for xml_to_txt to work. It parses xml files 
# rather nicely and makes getting text easy. Sentences has to also be 
# imported from runWord2Vec, as the histogram creator takes data from 
# that file as well. 
from runWord2Vec import Sentences

from bs4 import BeautifulSoup

from collections import Counter
import csv
import sys
import os
import re

reload(sys)
sys.setdefaultencoding('utf-8')

def create_frequency_dict (score_dir=score_dir, save='sentencesFrequency.csv'):
    """Creates and saves a frequency dictionary from Sentences()."""
    i = 1 
    print 'Creating frequency dictionary...'
    sentences = Sentences()
    word_count = Counter()
    for sentence in sentences: 
        for word in sentence: 
            if i % 10000 == 0:
                sys.stdout.write('\rAt word: %s ' % i)
            word_count[word] += 1
            i += 1
            sys.stdout.flush()
    sys.stdout.write('\n')
    print 'Total words counted: %s' % i
    print 'Saving frequency dictionary...'
    save_path = os.path.join(score_dir, save)
    frequency_file = csv.writer(open(save_path, 'w')) 
    for word, frequency in word_count.iteritems(): 
        frequency_file.writerow([word, frequency])


def xml_to_txt (root_dir = root_dir, article_dir = article_dir):
    """Finds all the text in .xml files in the root and saves them."""
    i = 1
    print 'Converting xml to txt...'
    for path, dirs, files in os.walk(root_dir):
        for file in files: 
            if '.xml' in file:
                sys.stdout.write('\rFile Title: %s File Number: %s' % (file,i))
                with open(os.path.join(path, file)) as xml: 
                    soup = BeautifulSoup(xml, 'lxml')
                    txt_title = re.sub('xml', 'txt', file)
                    txt_path = os.path.join(article_dir, txt_title)
                    with open(txt_path, 'w') as txt: 
                        for text in soup.find_all('p'): 
                            txt.write(text.get_text() + '\n')
                i += 1
                sys.stdout.flush()

# Call these two methods once
#create_frequency_dict()
#xml_to_txt()