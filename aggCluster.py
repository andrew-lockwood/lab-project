
#import logging
#logging.basicConfig(format='%(asctime)s : %(levelname)s : %(message)s', level=logging.INFO)
from tabulate import tabulate
from operator import itemgetter 

import gensim.models  
              
import csv         
import re 
import os
from collections import Counter, defaultdict
from random import shuffle
from sklearn.manifold import TSNE
from sklearn.cluster import AgglomerativeClustering
from sklearn.cluster import KMeans
from sklearn.neighbors import NearestCentroid 
from sklearn.metrics import silhouette_score
from sklearn.neighbors import NearestCentroid

import matplotlib.pyplot as P
import numpy as np

model_dir = '/media/removable/SD Card/frontiers_data/models/doc2vec/'
 
"""
Information about the algorithms pulled from sklearn
t-SNE (t-Distributed Stochastic Neighbor Embedding)--
An algorithm used for dimensionality reduction. Well suited for embedding 
high-dimensional data into two or three dimensions. Each point is modeled 
in such a way similar things are close together and disimilar things are 
farther apart.  
Involves two stages 1) constructs a probability distribution over pairs of
high dimensional objects 2) it defines a similar probability distribution 
over the points in a low dimensional map 

k-means clustering-- 
Aims to partition n observations into k clusters in which each observation
belongs to the cluster of the nearest mean. 

PCA (principal component analysis)--

"""

def time_this(original_function):      
    def new_function(*args,**kwargs):
        import datetime                 
        before = datetime.datetime.now()                     
        x = original_function(*args,**kwargs)                
        after = datetime.datetime.now()                      
        print "Elapsed Time = {0}".format(after-before)      
        return x                                             
    return new_function   

class tTransform (object): 
    def __init__ (self):
        self.file = os.path.join(model_dir, '300features_epochtrained_nokwds.doc2vec')
        self.cluster_ids = None
        self.cluster_set = None
        self.vectors = None

    def load_vectors (self):
        print 'loading vectors' 
        vectors = gensim.models.doc2vec.Doc2Vec.load(self.file)
        temp = []
        for vector in vectors.docvecs.doctag_syn0:
            temp.append(vector)

        self.X = np.array(temp)
        self.vectors = vectors

    def create_cluster_counter (self, fname = 'clusterCounters2.txt'):
        c = Counter()
        for cluster in self.cluster_ids: 
            c[cluster] += 1
        with open(fname, 'a') as f: 
            for k, v in c.most_common():
                f.write(str(v) + " ")
            f.write('\n')

    def load_n_cluster (self, n, fname = 'cluster.txt'): 
        self.cluster_ids = []
        print 'loading the %s cluster' % n
        with open(fname) as f:
            for i in xrange(n): f.next()
            for line in f:
                for c_id in line.split():
                    self.cluster_ids.append(int(c_id))
                break        

    @time_this
    def cluster_results (self, n, write): 
        load_path = '/media/removable/SD Card/frontiers_data/data/kwd_data/title_to_kwd.csv'

        self.load_n_cluster(n)

        # STEP 1: Create a dictionary, mapping titles to each cluster 
        #       For example, cluster_to_title[2] would return every title 
        #       within the cluster labeled 2
        print 'loading cluster_to_title dictionary'
        cluster_to_title = defaultdict(set)
        for i in range(len(self.X)):
            title = self.vectors.docvecs.index_to_doctag(i)
            cluster_to_title[self.cluster_ids[i]].add(title)

        # STEP 2: Load the dictionary that maps titles to each keyword
        #       For example, title_to_keyword['2012_00387'] would return 
        #       every keyword for that title
        print 'loading title_to_kwd dictionary'
        title_to_kwd = defaultdict(set)
        for key, values in csv.reader(open(load_path)):
            for value in re.findall(r"'(.*?)'", values, re.DOTALL):
                title_to_kwd[key].add(value)

        # STEP 3: Connect the two dictionaries, creating a list of 
        # keyword counters (with the array of the index corresponding 
        # to the cluster)
        print 'creating counters'
        counter_list = []
        kwd_totals = []
        for cluster, titles in cluster_to_title.iteritems():
            c = Counter()
            kwd_total = 0
            # Iterate through every title in the given cluster
            for title in titles: 
                # Iterate through every keyword in the title
                for kwd in title_to_kwd[title]:
                    c[kwd] += 1
                    kwd_total += 1
            counter_list.append(c) 
            kwd_totals.append(kwd_total)

        self.kwd_totals = kwd_totals  # Has the kwd count for each cluster

        if write == True: 
            # STEP 4: Write the counter to results.txt
            print 'writing results'
            with open('results_nokwd.txt', 'w') as f: 
                for counter in counter_list: 
                    for key, value in counter.most_common(): 
                        if value > 3: 
                            f.write(key + ': ' + str(value) + ', ')
                    f.write('\n')

    def cluster_keyword_information (self, n, orderby = 'id'): 

        self.load_vectors()                     # Set class vectors 
        self.cluster_results(n, write = False)  # Set kwd totals 

        # Get number of articles within each cluster 
        c = Counter()
        for c_id in self.cluster_ids: 
            c[int(c_id)] += 1

        # Create a table to display values 
        table = []
        for i in xrange(len(c)): 
            line = []
            # Cluster name 
            line.append(i+1)
            # Article count within the cluster
            line.append(c[i])
            # Keyword count within the cluster 
            line.append(self.kwd_totals[i])
            # Average keyword per article 
            line.append(self.kwd_totals[i]/float(c[i]))
            table.append(line)

        if orderby == 'id': 
            table = sorted(table, key = itemgetter(0))
        elif orderby == 'a_count':
            table = sorted(table, key = itemgetter(1))
        elif orderby == 'kwd_count':
            table = sorted(table, key = itemgetter(2))
        elif orderby == 'avg_kwds':
            table = sorted(table, key = itemgetter(3))
        else: 
            print orderby + ' not found'
            table = sorted(table, key = itemgetter(0))

        print tabulate(table, headers=['id', 'a_count', 'kwd_count', 'avg_kwds'], floatfmt=".3f")

    def score (self, n): 
        self.load_vectors()
        cluster_ids = []
        print 'loading cluster data'
        with open('cluster.txt') as f:
            for i in xrange(n - 1): f.next()
            for line in f:
                for c_id in line.split():
                    cluster_ids.append(int(c_id))
                break

        y = np.array(cluster_ids)

        s = silhouette_score(self.X, y, metric='cosine')

        print s

    ### CLUSTERING ALGORITHMS ###
    def agg_cluster (self, n): 
        print 'agglomerizing ' + str(n) + ' clusters'
        model = AgglomerativeClustering(n_clusters = n, \
                    affinity = "cosine", linkage = "average")
        self.cluster_ids = model.fit_predict(self.X)

    def kmeans_transform (self): 
        print 'performing kmeans...'
        model = KMeans(n_clusters=10, random_state=100)
        self.cluster_ids = model.fit_predict(self.X)

    ### I/O FOR CLUSTER IDS ###
    def save_cluster_ids (self, fname='cluster.txt'): 
        with open(fname, 'a') as f:
            for c_id in self.cluster_ids: 
                f.write(str(c_id) + ' ')
            f.write('\n')

    ### DIMENSIONALITY REDUCTION ###
    def tsne_transform (self): 
        print 'performing tsne...'
        model = TSNE(n_components=2, random_state=150)
        self.tsne_data = model.fit_transform(self.X) 

    ### GRAPHING ###
    def plot (self): 
        x = self.tsne_data[:, 0]
        y = self.tsne_data[:, 1]
        P.scatter(x, y, c=self.y_pred)
        P.show()


import datetime  
n_clusters = [1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, \
15, 16, 17, 18, 19, 20, 40, 60, 80, 100, 500]
# add 30, 10, 70, 90 

x = tTransform()
#x.load_vectors()

for n, i in enumerate(n_clusters): 
    x.load_n_cluster(n, fname = 'clusters2.txt')
    x.create_cluster_counter(fname = 'clusterCounter2.txt')
"""
for n in n_clusters:
    before = datetime.datetime.now()                     
    x.agg_cluster(n)
    x.save_cluster_ids(fname='clusters2.txt')
    after = datetime.datetime.now()                      
    print "Elapsed Time = {0}".format(after-before)
    print '--------------------------------------------'      
"""






