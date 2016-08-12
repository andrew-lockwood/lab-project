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


import webInterface
import osInterface
import config

import util 
from collections import defaultdict, Counter
from bs4 import BeautifulSoup

import time
import sys
import csv
import os
import re

reload(sys)
sys.setdefaultencoding('utf-8')

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
    d = config.dDir
    flag = -1
    for files in os.listdir(d): 
        for file in files:
            if ('merged_' + key) in file:
                flag = 1 
    if flag > 0: 
        mergeCounters(key)

    c = osInterface.loadCounter('merged_' + key, saveDir)
    cnt = Counter()
    for title, count in c.iteritems(): 
        if count > x: 
            cnt[title] = count

    return cnt

def getTitlesFromKeys (key, saveDir, x = None): 
    counter = getKeysGreaterThan(key, saveDir, x)
    dictionary = osInterface.loadDictionary('merged_' + key, saveDir)
    titles = set()
    for title, count in counter.iteritems(): 
        for title in dictionary[title]:
            titles.add(title)

    osInterface.saveSet (titles, 'titleSetFrom' + str(x) + key)

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
    f = osInterface.getFileCount()
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

    file_total = osInterface.getFileCount()
    file_size = osInterface.getTotalFileSize()
    print   'Current usage in project directory: ' + \
            str(round(file_size, 2)) + \
            ' bytes in ' + str(file_total) + ' files' 

    i = 0
    while True: 
        title = webInterface.createArticle(name)
        url = webInterface.createURL(year, title)
        xml = webInterface.createXML(year, title)
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
            file = os.path.join(config.rDir, year, file_name)
            with open((file), 'w') as f: 
                r = requests.get(xml)
                f.write(r.content)
                i += 1
                name += 1
                sys.stdout.write('\rFiles Written: %s' % i)
                sys.stdout.flush()

    print '\n'
    newFile_size = osInterface.getTotalFileSize() - file_size
    newFile_total = osInterface.getFileCount() - file_total
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
    d = os.path.join(config.rDir, year)

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

    osInterface.saveCounter(counter, year + '_keywords', 'kwd_data')
    osInterface.saveDictionary(dictionary, year + '_keywords', 'kwd_data')

def findTypes (year): 
    counter = Counter()
    dictionary = defaultdict(list)
    d = os.path.join(config.rDir, year)

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

    osInterface.saveCounter(counter, year + '_types', 'type_data')
    osInterface.saveDictionary(dictionary, year + '_types', 'type_data')

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