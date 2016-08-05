
import requests
import config

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
    xml = config.url + year + '.' + article + '/xml'
    return checkExistence(xml)

def createURL (year, article):
    checkLength(year, article)
    url = config.url + year + '.' + article + '/full'
    return checkExistence(url)

def createArticle (article): 
    length = len(str(article))

    if length == 1:             return '0000' + str(article)
    if length == 2:             return '000' + str(article)
    if length == 3:             return '00' + str(article)
    if length == 4:             return '0' + str(article)
    if length == 5:             return str(article)