
import gensim.models  
from collections import Counter
from util import time_this 
import os
import numpy as np
import csv
from sklearn.cluster import AgglomerativeClustering
from sklearn.metrics import silhouette_score

cluster_dir =   '/media/removable/SD Card/frontiers_data/clusters/'
kwd_dir =       '/media/removable/SD Card/frontiers_data/data/kwd_data/'

class Cluster (object): 
    def __init__ (self, model_name, model_dir):
        self.model = os.path.join(model_dir, model_name)
        self.load_vectors()

        self.id_file = os.path.join(model_dir, model_name + 'ClusterIDs.csv')
        self.meta_data = os.path.join(model_dir, model_name + 'ClusterMetaData.csv')
        with open(self.meta_data, 'a') as f: 
            w = csv.writer(f, delimiter = ':')
            w.writerow(['total', 'count'])  # Write the header


    def load_vectors (self): 
        self.vectors = gensim.models.doc2vec.Doc2Vec.load(self.model)
        self.np_vectors = np.array(self.vectors.docvecs.doctag_syn0)

    def save_ids (self): 
        ids = ''
        for id in self.cluster_ids:
            ids += str(ids) + ' '

        with open(self.meta_data, 'a') as f: 
            w = csv.writer(f)
            w.writerow([ids])

    def save_meta_data (self, n): 
        c = Counter()
        for cluster in self.cluster_ids:
            c[cluster] += 1
        
        count = ''
        for k, v in c.most_common(): 
            count += str(v) + ' '

        with open(self.meta_data, 'a') as f: 
            w = csv.writer(f, delimiter = ':')
            w.writerow([str(n), count])

    def agg_cluster (self, n): 
        cluster = AgglomerativeClustering(n_clusters = n, \
                    affinity = "cosine", linkage = "average")
        self.cluster_ids = cluster.fit_predict(self.np_vectors)
        self.save_meta_data(n)
        self.save_ids()

    def score (self):
        """Needs work"""
        y = np.array(self.cluster_ids)

        score = silhouette_score(self.np_vectors, y, metric="cosine")

        self.score = score(n)


class AnalyzeCluster (object): 
    def __init__ (self): 
        print 'cluster'

