import sys
import os 

#### ROOT ####
bd = 'C:\\Users\\Andrew\\Desktop'
rd = os.path.join(bd, 'frontiers_data')

#### Root Model Directory ####
md = os.path.join(rd, 'models')

# Word2Vec Model #
w2vM = os.path.join(rd, 'models', 'word2vec')
w2vS = os.path.join(rd, 'models', 'word2vec_scores')

# Do2Vec Model #
d2vM = os.path.join(rd, 'models', 'doc2vec')
d2vS = os.path.join(rd, 'models', 'doc2vec_scores')


ad = os.path.join(rd, 'article_txt')
ax = os.path.join(rd, 'article_xml')
pad = os.path.join(rd, 'parsed_article_txt')


#### Root Data Directory ####
dd = os.path.join(rd, 'data')

kwdd = os.path.join(dd, 'kwd_data')
wdd = os.path.join(dd, 'word_data')

fd = os.path.join(rd, 'featureTest')


def xml_dir():
	return ax

def data_dir():
	return dd

def kwd_dir():
	return kwdd

def word_dir():
	return wdd

def root_dir(): 
	return rd

def word2vec_models():
	return w2vM

def word2vec_scores():
	return w2vS

def doc2vec_models():
	return d2vM

def doc2vec_scores():
	return d2vS

def articles():
	return ad

def parsed_articles():
	return pad 

def feature_dir():
	return fd
