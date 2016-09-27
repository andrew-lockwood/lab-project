#
# This test involves creating models with 50, 100, 300, 500 features, 
# clustering the created vectors, and calculating the dissipation of 
# n-common keywords. 
#

from runDoc2Vec import Doc2VecModel
from clusterVectors import Cluster
import os

root_dir =      '/media/removable/SD Card/frontiers_data/'
test_title =    'featureTest'

training = True
clustering = False

# Number of features and clusters this test is looking at 
features = [50, 100, 300, 500]
n_clusters = [1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, \
              15, 16, 17, 18, 19, 20, 40, 60, 80, 100, 500]

# Step 1: Create path dictionary
feature_paths = {}
for i in xrange(len(features)):
    path = os.path.join(root_dir, test_title, str(features[i]))
    feature_paths[features[i]] = path
    if os.path.isdir(path):
        continue
    else:                       
        os.mkdir(path)

# Step 2: Create models if necessary 
if training:
    for i in xrange(len(features)):
        model_name = str(features[i]) + "model"
        model_dir = feature_paths[features[i]]
        model = Doc2VecModel(model_name, model_dir)
        model.create_build_train_model(features[i])

# Step 3: Cluster models 
if clustering: 
    for i in xrange(len(features)):
        model_name = str(features[i]) + "model"
        model_dir = feature_paths[features[i]]
        vec_cluster = Cluster(model_name, model_dir)
        for n in n_clusters:
            vec_cluster.agg_cluster(n)
