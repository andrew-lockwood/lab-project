
# Building a Better Keyword Classifier

### The Database

**ArticleInformation**

name | type | description
--- | --- | ---
articleID | text | Unique identifier of the form "journal.year.number" (primary key)
title | text | Title of the article
received | date| When the article was recieved by frontiers
type | text | Broad category the article falls under

**ArticleTXT**

name | type | description
--- | --- | ---
articleID | text | Foreign key referencing ArticleInformation.articleID
txt | text | Full text of the article (only if the paper has a keyword assigned)
wordcount | integer | Total number of words in txt 
linecount | integer | Total number of lines found during XML parsing

**OriginalKeywords**

name | type | description
--- | --- | ---
articleID | text | Foreign key referencing ArticleInformation.articleID
keyword | text | Assignment found during XML parsing

**KeywordForms**

name | type | description
--- | --- | ---
keyword | text | Foreign key referencing OriginalKeywords.keyword
parse | text | Keyword in lower case, with spaces replaced with underscores
stem | text | Root of the keyword found using an NLTK stemmer (Porter)
redirect | text | Title of the Wikipedia article the keyword redirects to


ArticleInformation holds all the information related to data scraped from xml file and holds the primary key articleID. ArticleTXT holds full text of files IF they contain a keyword in OriginalKeywords, the table storing keywords assigned by authors.  Finally, KeywordForms contains three alternate, but algorithmic, ways of modifying original keywords.  

### The Corpus 
#### Meaning of Type

In the ArticleInformation table, there are 4 fields.  The only one requiring an explanation is type. In the XML file, there is a field that describes the broadest possible category an article falls under. 

There are 13 possible types, ranging from original research, to book reviews to brief reports.  The most popular one by far is original research with just under 5000 assignments. This information can be used to further refine which papers looked at when training models or analyzing results.  

#### By the Numbers

The corpus contains **6561** articles from 2010-01-15 until 2016-06-23.  More articles have been put out since then and could be incorporated later.  

Of these articles, **6360** have keywords assigned to them.  Since the main area of interest are rules to assigning keywords, the 201 keywordless articles are ignored. 

Among articles with keywords assigned, the min and max assignments are **1** and **14** with the average being **5.75**. Therefore, any classifier that assigns between 4 and 7 is on the right track (since the variance of those assignments is **1.5**).
