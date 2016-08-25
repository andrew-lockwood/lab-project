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

root_dir =      '/media/removable/SD Card/frontiers_data/'
result_dir =    '/media/removable/SD Card/frontiers_data/results'
data_dir =      '/media/removable/SD Card/frontiers_data/data/'
base_url =      'http://journal.frontiersin.org/article/10.3389/fpsyg.'

import util 
from collections import defaultdict, Counter
from bs4 import BeautifulSoup

import requests
import time
import sys
import csv
import os
import re

reload(sys)
sys.setdefaultencoding('utf-8')

###############################################################################
#
#   checkXML, checkURL, createXML, createURL, and createArticle
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
    if r.status_code == 200:    return url      # exists
    else:                       return None     # doesn't exist

def checkLength (year, article): 
    if len(year) != 4:
        raise ValueError('Year needs to be length 4')
    if len(article) != 5:
        raise ValueError('Article needs to be length 5')

def createXML (year, article): 
    checkLength(year, article)
    xml = base_url + year + '.' + article + '/xml'
    return checkExistence(xml)

def createURL (year, article):
    checkLength(year, article)
    url = base_url + year + '.' + article + '/full'
    return checkExistence(url)

def createArticle (article): 
    length = len(str(article))

    if length == 1:             return '0000' + str(article)
    if length == 2:             return '000' + str(article)
    if length == 3:             return '00' + str(article)
    if length == 4:             return '0' + str(article)
    if length == 5:             return str(article)

##############################################################################
#
#   saveCounter, saveDictionary, loadCounter, loadDictionary, 
#       mergeCounters, and mergeDictionaries
#
# First four methods deal with data retrieval and storage on the disk. 
# The merge methods are for taking already made dictionaries, loading 
# them in memory into a larger dictionary, then storing them back on 
# the disk.  Those can also be access from the save/load methods. 
#
##############################################################################

def saveCounter (counter, fileName, saveDir):
    c = os.path.join(data_dir, saveDir, fileName + '_c.csv')
    w = csv.writer(open(c , 'w'))
    for key, value in counter.iteritems(): 
        w.writerow([key, value])
    print 'Saved file "' + fileName + '_c.csv" in' + data_dir + saveDir

def saveDictionary (dictionary, fileName, saveDir): 
    d = os.path.join(data_dir, saveDir, fileName + '_d.csv')
    w = csv.writer(open(d , 'w'))
    for key, value in dictionary.iteritems(): 
        w.writerow([key, value])
    print 'Saved file "' + fileName + '_d.csv" in' + data_dir + saveDir

def saveSet (output, fileName):
    d = os.path.join(result_dir, fileName + '.csv')
    w = csv.writer(open(d , 'w'))
    for file in output:
        w.writerow([file])
    print 'Saved file "' + fileName + '.csv" in' + result_dir

def loadCounter (fileName, saveDir): 
    if '_c.csv' in fileName: 
        d = os.path.join(data_dir, saveDir, fileName)
    else:   
        d = os.path.join(data_dir, saveDir, fileName + '_c.csv')
    counter = Counter()
    for key, value in csv.reader(open(d)):
        counter[key.decode('utf8')] = int(value)

    return counter

def loadDictionary (fileName, saveDir):
    if '_d.csv' in fileName: 
        d = os.path.join(data_dir, saveDir, fileName)
    else:   
        d = os.path.join(data_dir, saveDir, fileName + '_d.csv')
    dictionary = defaultdict(list)
    for key, values in csv.reader(open(d)):
        for value in re.sub("[^.0-9a-z_ ]", "", values).split():
            dictionary[key].append(value)

    return dictionary

def loadSet (fileName): 
    d = os.path.join(result_dir, fileName + '.csv')
    output = set()
    for line in csv.reader(open(d)):
        output.add(line[0])

    return output

def mergeCounters (key, saveDir): 
    # key can either be 'articles' or 'keywords'
    d = os.path.join(data_dir, saveDir)
    counter = Counter()
    for file in os.listdir(d):
        if key in file: 
            if '_d' in file or 'merged' in file: 
                continue
            else: 
                counter += loadCounter(file, saveDir)

    saveCounter(counter, 'merged_' + key, saveDir)

def mergeDictionaries (key, saveDir): 
    # key can either be 'articles' or 'keywords'
    d = os.path.join(data_dir, saveDir)
    dictionary = defaultdict(list)
    for file in os.listdir(d):
        if key in file: 
            if '_c' in file or 'merged' in file: 
                continue
            else:
                addDict = loadDictionary(file, saveDir)
                for word, file_list in addDict.iteritems():
                    for file in file_list:
                        dictionary[word].append(file)

    saveDictionary(dictionary, 'merged_' + key, saveDir)

def merge (key, saveDir = None): 
    if key == 'keywords': 
        saveDir = 'kwd_data'
    if key == 'types': 
        saveDir = 'type_data'
    mergeCounters(key, saveDir)
    mergeDictionaries(key, saveDir)

##############################################################################
#
#   getFileSize, getFileCount, and getTotalFileSize
#
# All three methods deal with grabbing information about files in the 
# project directory. getFileCount only cares about '.xml' files, as it 
# is used for the progress bar for the find methods below. 
#
##############################################################################

def getFileCount ():
    total = 0
    for path, dirs, files in os.walk(root_dir):
        for file in files:
            if '.xml' not in file:
                continue
            else:
                total += 1

    return total

def getTotalFileSize (): 
    total = 0.0
    for path, dirs, files in os.walk(root_dir):
        for file in files:
            file_name = os.path.join(path, file)
            total += os.path.getsize(file_name)

    return float(total / 1000000)

def getFileSize (xml):
    h = requests.head(xml)
    file_size = h.headers['content-length']
    return file_size

###############################################################################
#
#   and getTitlesFromKeys
#
# getTitlesFromKeys is the most important as it can take a list of keys
# and return the titles associated with those keys.  It avoids double 
# counting by placing them in a set.  
#   NOTE: The value could change due to access to the counter (since 
#   it is inherently random from the merge methods). In order to be 
#   more consistent with title retrieval, it is better to request
#   keys greater than a value. 
#
##############################################################################

def getKeysGreaterThan (key, saveDir, x = None):
    d = data_dir
    flag = -1
    for files in os.listdir(d): 
        for file in files:
            if ('merged_' + key) in file:
                flag = 1 
    if flag > 0: 
        mergeCounters(key)

    c = loadCounter('merged_' + key, saveDir)
    cnt = Counter()
    for title, count in c.iteritems(): 
        if count > x: 
            cnt[title] = count

    return cnt

def getTitlesFromKeys (key, saveDir, x = None): 
    counter = getKeysGreaterThan(key, saveDir, x)
    dictionary = loadDictionary('merged_' + key, saveDir)
    titles = set()
    for title, count in counter.iteritems(): 
        for title in dictionary[title]:
            titles.add(title)

    saveSet (titles, 'titleSetFrom' + str(x) + key)

    return str(len(titles))

##############################################################################
#
#   printMostCommonKeys, util.printInfo
#
# Prints information to the user based on the methods below. util.printInfo 
# is only a shortened call version of printProgress.
#
##############################################################################

def printKeysGreaterThan (key, x = None): 
    if key == 'keywords': 
        saveDir = 'kwd_data'
    if key == 'types': 
        saveDir = 'type_data'

    if x == None: 
        x = 0

    d = getKeysGreaterThan(key, saveDir, x)
    f = getFileCount()
    t = getTitlesFromKeys(key, saveDir, x)
    dL = len(d)

    print "Among " + str(f) + " articles, there are " + str(dL) + \
            " " + key + " mentioned over " + str(x) + " times"
    print "These " + str(dL) + " " + key + " appear in " + t + " articles"

    print"--------------------------------------"
    lim = 30    # Controls the number of keys output by this function
                # Default value is 10
    if dL > lim: 
        print "The " + str(lim) + " most common " + key + " are..."
        i = 0
        for key, value in d.most_common():
            sys.stdout.write(key + " (" + str(value) + ")")
            i += 1
            if i > lim:
                sys.stdout.write("\n")
                sys.stdout.flush()
                break
            else: 
                sys.stdout.write(", ")

    else:
        print "The keywords are..."
        i = 0
        for key, value in d.most_common(): 
            sys.stdout.write(key + " (" + str(value) + ")")
            i += 1
            if i == dL:
                sys.stdout.write("\n")
                sys.stdout.flush()
                break
            else: 
                sys.stdout.write(", ")

    print"--------------------------------------"

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
    name = 0
    nullURL = 0

    file_total = getFileCount()
    file_size = getTotalFileSize()
    print   'Current usage in project directory: ' + \
            str(round(file_size, 2)) + \
            ' bytes in ' + str(file_total) + ' files' 

    i = 0
    while True: 
        title = createArticle(name)
        url = createURL(year, title)
        xml = createXML(year, title)
        if url == None: 
            nullURL += 1
            if nullURL > 3: 
                break 
        if xml == None: 
            name += 1
            continue
        else:                       # write the XML to the disk 
            nullURL = 0
            file_name = year + '_' + title + '.xml'
            file = os.path.join(root_dir, year, file_name)
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
    print 'Added to project directory: ' + str(round(newFile_size, 2)) + \
            ' bytes in ' + str(newFile_total) + ' files'

def writeAll ():
    years = ['2010', '2011', '2012', '2013', '2014', '2015', '2016']
    for year in years: 
        writeData(year)

##############################################################################
# 
#   findKeyWords and findTypes
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
    d = os.path.join(root_dir, year)

    i = 0
    l = len(os.listdir(d))
    print year + ": Finding keywords from " + str(l) + " articles"
    util.printInfo(i, l)

    for file_name in os.listdir(d):
        xml_data = open(os.path.join(d, file_name), 'r')
        soup = BeautifulSoup(xml_data, 'lxml')
        for keyword in soup.find_all('kwd'):
            counter[keyword.text.lower()] += 1
            dictionary[keyword.text.lower()].append(file_name)

        i += 1
        util.printInfo(i, l)

    saveCounter(counter, year + '_keywords', 'kwd_data')
    saveDictionary(dictionary, year + '_keywords', 'kwd_data')

def findTypes (year): 
    counter = Counter()
    dictionary = defaultdict(list)
    d = os.path.join(root_dir, year)

    i = 0
    l = len(os.listdir(d))
    print year + ": Finding types from " + str(l) + " articles"
    util.printInfo(i, l)

    for file_name in os.listdir(d):
        xml_data = open(os.path.join(d, file_name), 'r')
        soup = BeautifulSoup(xml_data, 'lxml')
        for subject in soup.find_all('subject'):
            counter[subject.text.lower()] += 1
            dictionary[subject.text.lower()].append(file_name)
        i += 1
        util.printInfo(i, l)

    saveCounter(counter, year + '_types', 'type_data')
    saveDictionary(dictionary, year + '_types', 'type_data')

def findAll (key):
    start_time = time.time()
    years = ['2010', '2011', '2012', '2013', '2014', '2015', '2016']   
    if key == 'keywords':
        saveDir = 'kwd_data'
        for year in years: 
            findKeyWords(year)
    if key == 'types': 
        saveDir = 'type_data'
        for year in years:
            findTypes(year)
    merge(key)
    seconds = time.time() - start_time
    m, s = divmod(seconds, 60)
    h, m = divmod(m, 60)
    print "Took a total of %d:%02d:%02d to find and merge" % (h, m, s) 

def run ():
    """
    Data collecting functions: 
        writeAll - 
            This method grabs data from frontiers in science and saves 
            each article as a local XML file to later be analyzed. The 
            first time it is called it will take a while, but since it 
            is saved locally it only needs to be called once. 
        findAll - 
            Takes either 'keywords' or 'types' as an argument and 
            creates and saves a counter and dictionary for each year, 
            then merges them.  The counter keeps track of the 
            occurence of each keyword or article type, while the 
            dictionary keeps track of the opposite, which titles 
            are associated with which keyword or type.
        NOTE:   Both of these functions can be called for an individual
                year using the respective writeData, findType, or 
                findKeyword function with the desired year as the argument
    Data querying functions:
        printKeysGreaterThan - 
            Also takes 'types' or 'keywords' as well as an optional 
            integer.  The integer tells the function the minimum number 
            of key occurence for it to be printed.  If left empty, it gets 
            them all. If there are more than 10 keys, it will only print 
            out the 10 most common.  
        NOTE:   It can print out more or less than the 10 most common 
                by modifying the value 'lim' in printKeysGreaterThan

    """
    # Once the root directory, save directory, and output directory are set
    # calling these three functions will do all the work

    # writeData('2010')
    # findAll('types')
    # findAll('keywords')

run()