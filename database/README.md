#Database Schema


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
