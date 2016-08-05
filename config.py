
import sys
import os 

# Data directory, output directory, root directory
#   NOTE:   root is the place where data, output, and 
#           XML files are organized by year 

rDir = '/media/removable/SD Card/frontiers_data/'
dDir = os.path.join(rDir, 'data')
oDir = os.path.join(rDir, 'results')
mDir = os.path.join(rDir, 'models')
cDir = os.path.join(rDir, 'corpus')

url = 'http://journal.frontiersin.org/article/10.3389/fpsyg.'

yearList = ['2010', '2011', '2012', '2013', '2014', '2015', '2016']



