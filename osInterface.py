
from collections import defaultdict, Counter
import config 
import csv
import os

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
    c = os.path.join(config.dDir, saveDir, fileName + '_c.csv')
    w = csv.writer(open(c , 'w'))
    for key, value in counter.iteritems(): 
        w.writerow([key, value])
    print 'Saved file "' + fileName + '_c.csv" in' + config.dDir + saveDir

def saveDictionary (dictionary, fileName, saveDir): 
    d = os.path.join(config.dDir, saveDir, fileName + '_d.csv')
    w = csv.writer(open(d , 'w'))
    for key, value in dictionary.iteritems(): 
        w.writerow([key, value])
    print 'Saved file "' + fileName + '_d.csv" in' + config.dDir + saveDir

def saveSet (output, fileName):
    d = os.path.join(config.oDir, fileName + '.csv')
    w = csv.writer(open(d , 'w'))
    for file in output:
        w.writerow([file])
    print 'Saved file "' + fileName + '.csv" in' + config.oDir

def loadCounter (fileName, saveDir): 
    if '_c.csv' in fileName: 
        d = os.path.join(config.dDir, saveDir, fileName)
    else:   
        d = os.path.join(config.dDir, saveDir, fileName + '_c.csv')
    counter = Counter()
    for key, value in csv.reader(open(d)):
        counter[key.decode('utf8')] = int(value)

    return counter

def loadDictionary (fileName, saveDir):
    if '_d.csv' in fileName: 
        d = os.path.join(config.dDir, saveDir, fileName)
    else:   
        d = os.path.join(config.dDir, saveDir, fileName + '_d.csv')
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

def mergeCounters (key, saveDir): 
    # key can either be 'articles' or 'keywords'
    d = os.path.join(config.dDir, saveDir)
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
    d = os.path.join(config.dDir, saveDir)
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
    rd = config.rDir
    for path, dirs, files in os.walk(rd):
        for file in files:
            if '.xml' not in file:
                continue
            else:
                total += 1

    return total

def getTotalFileSize (): 
    total = 0.0
    for path, dirs, files in os.walk(config.rDir):
        for file in files:
            file_name = os.path.join(path, file)
            total += os.path.getsize(file_name)

    return float(total / 1000000)

def getFileSize (xml):
    h = requests.head(xml)
    file_size = h.headers['content-length']
    return file_size