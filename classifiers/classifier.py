from sklearn.preprocessing import MultiLabelBinarizer
from sklearn.multiclass import OneVsRestClassifier
import os

kwd_dir = '/media/removable/SD Card/frontiers_data/data/kwd_data/'
import csv
from collections import Counter, defaultdict
import re


from sklearn.pipeline import Pipeline
from sklearn.svm import SVC

from corpusProcessors import DataLoader 



class Classifier (object):
    def load_kwds (self, n): 
        kwdcount = os.path.join(kwd_dir, 'kwd_counter.csv')
        k_count = Counter()
        for kwd, count in csv.reader(open(kwdcount)):
            if kwd != 'NULL':
                k_count[kwd] = float(count)  
        self.kwd_count = Counter()
        for kwd, count in k_count.most_common(n):
            self.kwd_count[kwd] = count
        kwd_list = []
        for kwd, count in self.kwd_count.iteritems(): 
            kwd_list.append(kwd)
        self.kwd_list = kwd_list

    def load_title_to_kwd(self):
        titledict = os.path.join(kwd_dir, 'title_to_kwd.csv')
        print 'loading title_to_kwd dictionary'
        title_to_kwd = defaultdict(set)
        for key, values in csv.reader(open(titledict)):
            for value in re.findall(r"'(.*?)'", values, re.DOTALL):
                if value in self.kwd_list:
                    title_to_kwd[key].add(value)

        self.title_to_kwd = title_to_kwd
        print self.title_to_kwd

    def multilabel (self):
        labels = []
        for title, kwds in self.title_to_kwd.iteritems():
            labels.append(kwds)

        mlb = MultiLabelBinarizer()
        l = mlb.fit_transform(labels)
        print len(l)


c = Classifier()
c.load_kwds(2)
c.load_title_to_kwd()
c.multilabel()