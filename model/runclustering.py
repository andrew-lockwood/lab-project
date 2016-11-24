from sklearn.cluster import AgglomerativeClustering
import gensim.models
import os

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
        ids = model_name + 'ClusterIDs.txt'
        self.id_file = os.path.join(model_dir, ids)
        meta = model_name + 'ClusterMetaData.txt'
        self.meta_data = os.path.join(model_dir, meta)

        print ('Loading %s vectors for clustering' % model_name)
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
        print ("Nuking all of your hard earned data in 30 seconds")
        print ("Close the terminal to abort.")

        time.sleep(30)      

        with open(self.meta_data, 'w') as f:    pass 
        with open(self.cluster_ids, 'w') as f:  pass 
        # Everything is gone
