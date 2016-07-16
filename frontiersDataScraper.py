##############################################################################
#
# This file has everything related to gathering and storing data from 
# the website frontiers in in science.  Both keywords and article 
# types are stored in counters that are written to the disk in a .csv 
# file.  This allows querying related to how many articles contain a 
# given keyword or are of a specific type.  This allows being able 
# to choose specific files when running machine learning software 
# or, more generally, gives information about the website as a whole. 
# 
##############################################################################

import config
from collections import defaultdict, Counter
from bs4 import BeautifulSoup
import requests
import sys
import csv
import os
import re

reload(sys)
sys.setdefaultencoding('utf-8')

###############################################################################
#	checkXML, checkURL, createXML, createURL, and createArticle
#
# All helper methods for the writeData method later on in the file.  
# The create methods concatenate the string that interfaces with the 
# website, the check methods check that the create method made something
# that exists, and finally, createArticle takes an integer value 
# and returns a string (useful for incrementing).  
#
##############################################################################

def checkExistence (url):
	r = requests.head(url)
	if r.status_code == 200: 	return url		# exists
	else: 						return None		# doesn't exist

def checkLength (year, article): 
	if len(year) != 4:
		raise ValueError('Year needs to be length 4')
	if len(article) != 5:
		raise ValueError('Article needs to be length 5')

def createXML (year, article): 
	checkLength(year, article)
	xml = config.url + year + '.' + article + '/xml'
	return checkExistence(xml)

def createURL (year, article):
	checkLength(year, article)
	url = config.url + year + '.' + article + '/full'
	return checkExistence(url)

def createArticle (article): 
	length = len(str(article))

	if length == 1: 			return '0000' + str(article)
	if length == 2:				return '000' + str(article)
	if length == 3:				return '00' + str(article)
	if length == 4: 			return '0' + str(article)
	if length == 5: 			return str(article)

##############################################################################
#
#	saveCounter, saveDictionary, loadCounter, loadDictionary, 
#		mergeCounters, and mergeDictionaries
#
# First four methods deal with data retrieval and storage on the disk. 
# The merge methods are for taking already made dictionaries, loading 
# them in memory into a larger dictionary, then storing them back on 
# the disk.  Those can also be access from the save/load methods. 
#
##############################################################################

def saveCounter (counter, fileName):
	c = os.path.join(config.dDir, fileName + '_c.csv')
	w = csv.writer(open(c , 'w'))
	for key, value in counter.iteritems(): 
		w.writerow([key, value])
	print 'Saved file "' + fileName + '_c.csv" in' + config.dDir

def saveDictionary (dictionary, fileName): 
	d = os.path.join(config.dDir, fileName + '_d.csv')
	w = csv.writer(open(d , 'w'))
	for key, value in dictionary.iteritems(): 
		w.writerow([key, value])
	print 'Saved file "' + fileName + '_d.csv" in' + config.dDir

def saveSet (output, fileName):
	d = os.path.join(config.oDir, fileName + '.csv')
	w = csv.writer(open(d , 'w'))
	for file in output:
		w.writerow([file])
	print 'Saved file "' + fileName + '.csv" in' + config.oDir

def loadCounter (fileName): 
	if '_c.csv' in fileName: 
		d = os.path.join(config.dDir, fileName)
	else: 	
		d = os.path.join(config.dDir, fileName + '_c.csv')
	counter = Counter()
	for key, value in csv.reader(open(d)):
		counter[key.decode('utf8')] = int(value)

	return counter

def loadDictionary (fileName):
	if '_d.csv' in fileName: 
		d = os.path.join(config.dDir, fileName)
	else: 	
		d = os.path.join(config.dDir, fileName + '_d.csv')
	dictionary = defaultdict(list)
	for key, values in csv.reader(open(d)):
		for value in re.sub("[^.0-9a-z_ ]", "", values).split():
			dictionary[key].append(value)

	return dictionary

def loadSet (fileName): 
	d = os.path.join(config.oDir, fileName + '.csv')
	output = set()
	for line in csv.reader(open(d)):
		output.add(line[0])

	return output

def mergeCounters (key): 
	# key can either be 'articles' or 'keywords'
	d = config.dDir
	counter = Counter()
	for file in os.listdir(d):
		if key in file: 
			if '_d' in file or 'merged' in file: 
				continue
			else: 
				counter += loadCounter(file)

	saveCounter(counter, 'merged_' + key)

def mergeDictionaries (key): 
	# key can either be 'articles' or 'keywords'
	d = config.dDir
	dictionary = defaultdict(list)
	for file in os.listdir(d):
		if key in file: 
			if '_c' in file or 'merged' in file: 
				continue
			else:
				addDict = loadDictionary(file)
				for word, file_list in addDict.iteritems():
					for file in file_list:
						dictionary[word].append(file)

	saveDictionary(dictionary, 'merged_' + key)

##############################################################################
#
#	getFileSize, getFileCount, and getTotalFileSize
#
# All three methods deal with grabbing information about files in the 
# project directory. getFileCount only cares about '.xml' files, as it 
# is used for the progress bar for the find methods below. 
#
##############################################################################

def getFileCount ():
	total = 0
	rd = config.rDir
	for path, dirs, files in os.walk(rd):
		for file in files:
			if '.xml' not in file:
				continue
			else:
				total += 1

	return total

def getTotalFileSize (): 
	total = 0
	rd = config.rDir
	for path, dirs, files in os.walk(rd):
		for file in files:
			file_name = os.path.join(path, file)
			total += os.path.getsize(file_name)

	return total

def getFileSize (xml):
	h = requests.head(xml)
	file_size = h.headers['content-length']
	return file_size

###############################################################################
#
#	getAvgAmountofKeywords, getMostCommonKeys, and getTitlesFromKeys
#
# getTitlesFromKeys is the most important as it can take a list of keys
# and return the titles associated with those keys.  It avoids double 
# counting by placing them in a set.  
#	NOTE: The value could change due to access to the counter (since 
#	it is inherently random from the merge methods). In order to be 
#	more consistent with title retrieval, it is better to request
#	keys greater than a value. 
#
##############################################################################

def getMostCommonKeys (name, x = None): 
	d = config.dDir
	flag = -1
	for files in os.listdir(d): 
		for file in files:
			if ('merged_' + name) in file:
		 		flag = 1 
	if flag > 0: 
		mergeCounters(name)

	c = loadCounter('merged_' + name)

	return c.most_common(x)

def getKeysGreaterThan (name, x = None):
	d = config.dDir
	flag = -1
	for files in os.listdir(d): 
		for file in files:
			if ('merged_' + name) in file:
		 		flag = 1 
	if flag > 0: 
		mergeCounters(name)

	c = loadCounter('merged_' + name)
	cnt = Counter()
	for title, count in c.iteritems(): 
		if count > x: 
			cnt[title] = count

	return cnt

def getTitlesFromKeys (name, x = None): 
	counter = getKeysGreaterThan(name, x)
	dictionary = loadDictionary('merged_' + name)
	titles = set()
	for title, count in counter.iteritems(): 
		for title in dictionary[title]:
			titles.add(title)

	print "There are " + str(len(titles)) + " articles among the " \
			+ str(x) + " most common keys"

	saveSet (titles, 'titleSetFrom' + str(x) + name)

##############################################################################
#
#	printMostCommonKeys, printInfo
#
# Prints information to the user based on the methods below. printInfo 
# is only a shortened call version of printProgress.
#
##############################################################################

def printInfo (iteration, total):
	printProgress (iteration, total, prefix = 'Progress:', \
					suffix = 'Complete', barLength = 50)

##############################################################################
# 
# Most important for interfacing with the website.  writeData takes a 
# year, grabs all the articles from that year, then saves them in XML 
# format to a disk.  Both the XML and URL of an article are checked 
# since some pages have a URL, but not an XML.  If there are 3 
# nullURLs in a row, the while loop is terminated and the 
# writeData function is done calling
#   
##############################################################################

def writeData (year):
	name = 378
	nullURL = 0

	file_total = getFileCount()
	file_size = getTotalFileSize()
	print 'Current usage in project directory: ' + str(file_size) + \
			' bytes in ' + str(file_total) + ' files' 

	i = 0
	while True: 
		url = createURL(year, createArticle(name))
		xml = createXML(year, createArticle(name))
		if url == None: 
			nullURL += 1
			if nullURL > 3: 
				break 
		if xml == None: 
			name += 1
			continue
		else: 						# write the XML to the disk 
			nullURL = 0
			title = year + '_' + createArticle(name) + '.xml'
			file = os.path.join(config.rDir, year, title)
			with open((file), 'w') as f: 
				r = requests.get(xml)
				f.write(r.content)
				i += 1
				name += 1
				sys.stdout.write('\rFiles Written: %s' % i)
				sys.stdout.flush()

	print '\n'
	newFile_size = getTotalFileSize() - file_size
	newFile_total = getFileCount() - file_total
	print 'Added to project directory: ' + str(newFile_size) + \
			' bytes in ' + str(newFile_total) + ' files'

##############################################################################
# 
#	findKeyWords and findTypes
# 
# These two functions grab information in within a given year directory.  
# Year could be modified to change with file nomenclature, but the 
# basic structure stays the same.  These two functions work in a similar
# manner, creating a counter of words found within an XML file saved 
# on the disk
#
##############################################################################

def findKeyWords (year): 
	counter = Counter()
	dictionary = defaultdict(list)
	d = os.path.join(config.rDir, year)

	i = 0
	l = len(os.listdir(d))
	print year + ": Finding keywords from " + str(l) + " articles"
	printInfo(i, l)

	for file_name in os.listdir(d):
		xml_data = open(os.path.join(d, file_name), 'r')
		soup = BeautifulSoup(xml_data, 'lxml')
		for keyword in soup.find_all('kwd'):
			counter[keyword.text.lower()] += 1
			dictionary[keyword.text.lower()].append(file_name)

		i += 1
		printInfo(i, l)

	saveCounter(counter, year + '_keywords')
	saveDictionary(dictionary, year + '_keywords')

def findTypes (year): 
	counter = Counter()
	dictionary = defaultdict(list)
	d = os.path.join(config.rDir, year)

	i = 0
	l = len(os.listdir(d))
	print year + ": Finding article types from " + str(l) + " articles"
	printInfo(i, l)

	for file_name in os.listdir(d):
		xml_data = open(os.path.join(d, file_name), 'r')
		soup = BeautifulSoup(xml_data, 'lxml')
		for subject in soup.find_all('subject'):
			counter[subject.text.lower()] += 1
			dictionary[subject.text.lower()].append(file_name)
		i += 1
		printInfo(i, l)

	saveCounter(counter, year + '_articles')
	saveDictionary(dictionary, year + '_articles')

##############################################################################
#
# Provides a nice progress bar within the terminal. printInfo is a 
# helper method that shortens the declaration in the methods above 
# (prefix/suffix/barLength never change).
#	NOTE: adapted from Vladimir Ignatyev's code found on stackoverflow
#
##############################################################################

def printProgress (iteration, total, prefix = '', suffix = '', \
					decimals = 2, barLength = 100):
    """
	    Call in a loop to create terminal progress bar
	        iteration   - Required  : current iteration (Int)
	        total       - Required  : total iterations (Int)
	        prefix      - Optional  : prefix string (Str)
	        suffix      - Optional  : suffix string (Str)
	        decimals    - Optional  : number of decimals in percent complete (Int)
	        barLength   - Optional  : character length of bar (Int)
    """
    filledLength    = int(round(barLength * iteration / float(total)))
    percents        = round(100.00 * (iteration / float(total)), decimals)
    bar             = '|' * filledLength + '-' * (barLength - filledLength)
    sys.stdout.write('\r%s |%s| %s%s %s' % (prefix, bar, percents, '%', suffix)),
    sys.stdout.flush()
    if iteration == total:
        sys.stdout.write('\n')
        sys.stdout.flush()

def runTests ():
	# 2010 Initialization Tests
	# writeData('2010')
	# findKeyWords('2010')
	# findTypes('2010')
	# findTypes('2011')
	# findTypes('2012')

	writeData('2013')

	# Merge Tests
	# mergeCounters('articles')
	# mergeCounters('keywords')
	# mergeDictionaries('articles')	
	# mergeDictionaries('keywords')

	# Key Querying Tests
	# getTitlesFromKeys('articles', 10)
	# print common 
	# count = getKeysGreaterThan('articles', 2)
	# print count
	# loadOutput('titleSetFrom2articles')

	# t = getTotalFileSize()
	# print t

runTests()