
from sklearn.cluster import AgglomerativeClustering
from sklearn.metrics import silhouette_score
from tabulate import tabulate
from operator import itemgetter 

from collections import Counter, defaultdict
import re
from util import time_this 
import gensim.models
import os
import numpy as np
import csv
import sys

cluster_dir = '/media/removable/SD Card/frontiers_data/clusters/'
kwd_dir =     '/media/removable/SD Card/frontiers_data/data/kwd_data/'

class Cluster (object): 
    def __init__ (self,n_clusters):
        """
        Creates the cluster models directory, the ID file and 
        meta data file directory.
        """
        self.n_clusters = n_clusters

    def trial_cluster(self, model_name, model_dir):
        """
        Performs agglomerative clustering for each 
        n within n_clusters. Appends the results of clustering 
        to the ID and meta data file.
        """
        self.model = os.path.join(model_dir, model_name)
        self.id_file = os.path.join(model_dir, \
                        model_name + 'ClusterIDs.txt')
        self.meta_data = os.path.join(model_dir, \
                        model_name + 'ClusterMetaData.txt')

        print 'Loading %s vectors for clustering' % model_name
        self.load_vectors()
        with open(self.meta_data, 'a') as f: 
            f.write('total: count\n')

        for n in self.n_clusters: 
            sys.stdout.write("\rCurrent cluster size: %i" % n)
            sys.stdout.flush()
            self.agg_cluster(n)
            self.save_ids()
            self.save_meta_data(n)
        sys.stdout.write('\n')

    def load_vectors (self): 
        """Loads the vectors used for clustering once."""
        self.vectors = gensim.models.doc2vec.Doc2Vec.load(self.model)
        self.np_vectors = np.array(self.vectors.docvecs.doctag_syn0)

    def agg_cluster (self, n):
        """
        Performs agglomerative clustering of size n on the 
        loaded model. In testing took upwards of ~2 minutes 
        per clustering. 
        """ 
        cluster = AgglomerativeClustering(n_clusters = n, \
                    affinity = "cosine", linkage = "average")
        self.cluster_ids = cluster.fit_predict(self.np_vectors)


    def save_ids (self): 
        with open(self.id_file, 'a') as f: 
            for c_id in self.cluster_ids: 
                f.write(str(c_id) + ' ')
            f.write('\n')

    def save_meta_data (self, n): 
        c = Counter()
        for cluster in self.cluster_ids:
            c[cluster] += 1
        
        with open(self.meta_data, 'a') as f: 
            f.write(str(n) + ": ")
            for k, v in c.most_common():
                f.write(str(v) + " ")
            f.write('\n')

    def clear_data (self): 
        """
        WARNING: Calling this method with erase everything in the ID
        and meta data file. This cannot be undone once called. 
        Appending is used throughout this file for backup purposes.
        """
        import time
        print "Nuking all of your hard earned data in 30 seconds"
        print "Close the terminal to abort."

        time.sleep(30)      

        with open(self.meta_data, 'w') as f:    pass 
        with open(self.cluster_ids, 'w') as f:  pass 
        # Everything is gone

class DissipationSpread (object): 
    def __init__ (self, min_kwd_count, n_clusters):
        self.titledictdir = os.path.join(kwd_dir, 'title_to_kwd.csv')
        self.kwddictdir = os.path.join(kwd_dir, 'kwd_to_title.csv')
        self.kwdcountdir = os.path.join(kwd_dir, 'kwd_counter.csv')

        self.loadkwddata(min_kwd_count)    
        self.n_clusters = n_clusters   
        self.display = display 

    def trial_score (self, model_name, model_dir):
        print 'Loading %s vectors for scoring' % model_name

        self.model = os.path.join(model_dir, model_name)
        self.load_vectors()

        self.dissipationdir = os.path.join(model_dir, model_name + \
                                'Dissipation.txt')
        self.spreaddir = os.path.join(model_dir, model_name + \
                                'Spread.txt')
        self.id_file = os.path.join(model_dir, \
                        model_name + 'ClusterIDs.txt')

        self.dissipation_data = defaultdict(list)
        self.spread_data = defaultdict(list)

        for n in self.n_clusters:
            sys.stdout.write("\rScoring cluster: %i" % n)
            sys.stdout.flush()
            self.score_cluster(n)
        sys.stdout.write("\n")

    def load_vectors (self): 
        """Loads the vectors used for clustering."""
        self.vectors = gensim.models.doc2vec.Doc2Vec.load(self.model)
        self.np_vectors = np.array(self.vectors.docvecs.doctag_syn0)

    def save_data (self):
        with open(self.spreaddir, 'w') as f: 
            for kwd, scores in self.spread_data.iteritems():
                f.write(kwd + " ")
                for score in scores: 
                    f.write(str(score) + " ")
                f.write("\n")

        with open(self.dissipationdir, 'w') as f: 
            for kwd, scores in self.dissipation_data.iteritems():
                f.write(kwd + " ")
                for score in scores: 
                    f.write(str(score) + " ")
                f.write("\n")

    def record_result (self, dissipation, spread):
        for kwd, score in dissipation.iteritems(): 
            self.dissipation_data[kwd].append(score)

        for kwd, score in spread.iteritems(): 
            self.spread_data[kwd].append(score)

    def load_cluster_ids (self, n): 
        for i in xrange(len(self.n_clusters)): 
            if n == self.n_clusters[i]:
                break

        self.cluster_ids = []
        with open(self.id_file) as f:
            for i in xrange(i): f.next()
            for line in f:
                for c_id in line.split():
                    self.cluster_ids.append(int(c_id))
                break   

    def score_cluster (self, n): 
        self.load_cluster_ids(n)
        # Create a dictionary of size n, where n corresponds to the 
        # cluster
        cluster_to_title = defaultdict(set)
        for i in range(len(self.np_vectors)):
            title = self.vectors.docvecs.index_to_doctag(i)
            cluster_to_title[self.cluster_ids[i]].add(title)

        # Create a keyword counter for each cluster
        counter_list = []      
        for cluster, titles in cluster_to_title.iteritems():
            kwd_count = Counter()
            for title in titles: 
                for kwd in self.titledict[title]:
                    if kwd in self.kwdlist:
                        kwd_count[kwd] += 1
            counter_list.append(kwd_count) 

        # Find the dissipation of the keyword in that cluster 
        # Take the number of keywords in a specific cluster, divided
        # by the total occurence of that keyword
        for c in counter_list: 
            for kwd, count in c.iteritems():
                if kwd in self.kwdlist:     # TODO: Test if necessary 
                    c[kwd] = count/float(self.kwdcount[kwd])

        # Create a dictionary {keyword:dissipation}
        d = defaultdict(list)
        for c in counter_list:
            for kwd, dissipation in c.iteritems(): 
                d[kwd].append(dissipation)

        # Sort each entry from top down (largest value first)
        for kwd, scores in d.iteritems():
            d[kwd] = sorted(d[kwd], reverse = True)

        # Record dissipation
        dissipation = {}
        for kwd, scores in d.iteritems():
            dissipation[kwd] = scores[0]

        # Record spread 
        spread = {}
        for kwd, scores in d.iteritems():
            spread[kwd] = len(scores)

        self.record_result(dissipation, spread)

    def loadkwddata (self, numkwds):
        """
        Sets three object variables that are the same per cluster-
        1) A counter of the n most common keywords
        2) A list of those common keywords 
        3) A dictionary mapping each of those keywords to a set of 
           titles
        Only needs to be called once per set of trials 
        """

        # look at the count of keywords
        self.kwdcount = {}
        self.kwdlist = []
        with open(self.kwdcountdir) as f: 
            r = csv.reader(f)
            for kwd, count in r: 
                if int(count) > numkwds: 
                    if kwd != 'NULL':  
                        self.kwdcount[kwd] = int(count)
                        self.kwdlist.append(kwd)

        # look at the dictionary of {kwd:titles}
        self.kwddict = defaultdict(set)
        #self.titledict = defaultdict(set)
        with open(self.kwddictdir) as f:
            r = csv.reader(f)
            for kwd, titles in r:
                if kwd in self.kwdlist:
                    for title in re.findall(r"'(.*?)'", titles, \
                                    re.DOTALL):
                        self.kwddict[kwd].add(title)
                        #self.titledict[title].add(kwd)

        # look at the dictionary of {title:kwds}
        self.titledict = defaultdict(set)
        with open(self.titledictdir) as f:
            r = csv.reader(f)
            for title, kwds in r: 
                for kwd in re.findall(r"'(.*?)'", kwds, re.DOTALL):
                    if kwd in self.kwdlist:                        
                        self.titledict[title].add(kwd)

class DisplayTestScore: 
    def __init__ (self, model_name, model_dir, n_clusters, \
                    display_clusters):
        self.dissipationdir = os.path.join(model_dir, \
                                model_name + 'Dissipation.txt')
        self.spreaddir = os.path.join(model_dir, \
                                model_name + 'Spread.txt')
        self.kwdcountdir = os.path.join(kwd_dir, 'kwd_counter.csv')

        self.model_dir = model_dir
        self.model_name = model_name

        self.indices = []
        for i in xrange(len(n_clusters)): 
            if n_clusters[i] in display_clusters:
                self.indices.append(i)

        self.display_clusters = display_clusters

    def spread (self):
        table = []
        h = ['kwds']
        for n in self.display_clusters: 
            h.append(n)
        with open(self.spreaddir) as f: 
            for line in f.readlines():
                row = []
                values = line.split()
                kwd = ""
                for n, value in enumerate(values): 
                    if self.isnumber(value):
                        break
                    else:
                        kwd += value + " "
                row.append(kwd)
                for i in self.indices: 
                    row.append(values[i + n])
                table.append(row)
        return tabulate(table, headers = h)


    def dissipation (self):
        table = []
        h = ['kwds', 'var']
        for n in self.display_clusters: 
            h.append(n)
        with open(self.dissipationdir) as f: 
            for line in f.readlines():
                row = []
                values = line.split()
                kwd = ""
                for n, value in enumerate(values): 
                    if self.isnumber(value):
                        break
                    else:
                        kwd += value + " "
                row.append(kwd)
                nums = []
                for i in self.indices: 
                    nums.append(float(values[i + n]))
                row.append(np.var(np.array(nums)))
                for n in nums:
                    row.append(n)
                table.append(row)
        return tabulate(table, headers = h, floatfmt=".3f")

    def isnumber (self, s):
        try:
            float(s)
            return True 
        except ValueError:
            return False

    def savetables (self):
        print 'saving %s tables' % self.model_name
        dissipationtable = os.path.join(self.model_dir, \
                        self.model_name + 'DissipationTable.txt')
        with open(dissipationtable, 'wb') as f: 
            f.write(self.dissipation())

        spreadtable = os.path.join(self.model_dir, \
                        self.model_name + 'SpreadTable.txt')
        with open(spreadtable, 'wb') as f: 
            f.write(self.spread())

class MetaScore (object): 
    def score (self, model_name, model_dir, \
                        n_clusters, scored_clusters): 

        dissipationdir = os.path.join(model_dir, \
                                model_name + 'Dissipation.txt')

        indices = []
        for i in xrange(len(n_clusters)): 
            if n_clusters[i] in scored_clusters:
                indices.append(i)
        totalindices = len(indices)
        varlist = []
        for index in xrange(len(indices)):
            totalvar = []
            with open(dissipationdir) as f: 
                for line in f.readlines():
                    values = line.split()
                    for n, value in enumerate(values): 
                        if self.isnumber(value):
                            break
                    nums = []
                    for j, i in enumerate(indices): 
                        nums.append(float(values[i + n]))
                        if j == index: 
                            break
                    totalvar.append(np.var(np.array(nums)))
            varlist.append(np.average(np.array(totalvar)))
        return varlist

    def isnumber (self, s):
        try:
            float(s)
            return True 
        except ValueError:
            return False
