
from sklearn.cluster import AgglomerativeClustering
from sklearn.metrics import silhouette_score

from collections import Counter
from util import time_this 
import gensim.models  
import os
import numpy as np
import csv
import sys

cluster_dir =   '/media/removable/SD Card/frontiers_data/clusters/'
kwd_dir =       '/media/removable/SD Card/frontiers_data/data/kwd_data/'

class Cluster (object): 
    def __init__ (self, model_name, model_dir):
        """
        Creates the cluster models directory, the ID file and 
        meta data file directory.
        """
        self.model = os.path.join(model_dir, model_name)
        self.id_file = os.path.join(model_dir, \
                        model_name + 'ClusterIDs.txt')
        self.meta_data = os.path.join(model_dir, \
                        model_name + 'ClusterMetaData.txt')

    @time_this
    def trial_cluster(self, n_clusters):
        """
        Performs agglomerative clustering for each 
        n within n_clusters. Appends the results of clustering 
        to the ID and meta data file.
        """
        print 'Loading vectors for trial clustering'
        self.load_vectors()
        with open(self.meta_data, 'a') as f: 
            f.write('total: count\n')

        for n in n_clusters: 
            sys.stdout.write("\rCurrent cluster size: %i" % n)
            sys.stdout.flush()
            self.agg_cluster(n)
            self.save_ids()
            self.save_meta_data(n)
        sys.stoud.write('\n')

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
        a = raw_input()

    def score (self):
        """Needs work"""
        y = np.array(self.cluster_ids)

        score = silhouette_score(self.np_vectors, y, metric="cosine")

        self.score = score(n)


class AnalyzeCluster (object): 
    def __init__ (self): 
        print 'cluster'

