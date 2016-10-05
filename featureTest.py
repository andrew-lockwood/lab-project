#
# This test involves creating models with 50, 100, 300, 500 features, 
# clustering the created vectors, and calculating the dissipation of 
# n-common keywords. 
#

from clusterVectors import Cluster, DissipationSpread, \
                            DisplayTestScore, MetaScore
from RunDoc2Vec import Doc2VecModel
from tabulate import tabulate
import numpy as np
import matplotlib.pyplot as plt
from sklearn.preprocessing import normalize

import os

root_dir =      '/media/removable/SD Card/frontiers_data/'
test_title =    'featureTest'

# What this test is going to do. Once the data is trained and 
# clustered it doesn't need to be done again.
training =      False
clustering =    False
scoring =       False
displaying =    False
saveresults =   False
metascoring =   True
normplot =      False
# Number of features, clusters, and keywords with a minimum count 
# this test is 
min_kwd_count = 80
features = [50, 100, 300, 500]
n_clusters = [1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, \
              15, 16, 17, 18, 19, 20, 40, 60, 80, 100, 500]

# Step 1: Create paths
feature_paths = {}
for i in xrange(len(features)):
    path = os.path.join(root_dir, test_title, str(features[i]))
    feature_paths[features[i]] = path
    if os.path.isdir(path):
        continue
    else:                       
        os.mkdir(path)

# Step 2: Train models (Slowest)
if training:
    for i in xrange(len(features)):
        model_name = str(features[i]) + "model"
        model_dir = feature_paths[features[i]]
        model = Doc2VecModel(model_name, model_dir)
        model.create_build_train_model(features[i])

# Step 3: Cluster models (Slow)
if clustering: 
    vec_cluster = Cluster(n_clusters)
    for i in xrange(len(features)):
        model_name = str(features[i]) + "model"
        model_dir = feature_paths[features[i]]
        vec_cluster.trial_cluster(model_name, model_dir)

# Step 4: Score models (Extremely Fast)
if scoring: 
    dissipation_spread = DissipationSpread(min_kwd_count, n_clusters)
    for i in xrange(len(features)): 
        model_name = str(features[i]) + "model"
        model_dir = feature_paths[features[i]]
        dissipation_spread.trial_score(model_name, model_dir)

# Step 5: Display 
if displaying: 
    display_clusters = [2, 3, 4, 5, 6, 7, 8, 9]
    display_feature = 500
    model_name = str(display_feature) + "model"
    model_dir = feature_paths[display_feature]

    display = DisplayTestScore(model_name, model_dir, \
                                n_clusters, display_clusters)
    display.dissipation()
    #display.spread()

if saveresults: 
    for i in xrange(len(features)): 
        model_name = str(features[i]) + "model"
        model_dir = feature_paths[features[i]]
        results = DisplayTestScore(model_name, model_dir, \
                                n_clusters, n_clusters)
        results.savetables()

if metascoring: 
    scored_clusters = [2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, \
              15, 16, 17, 18, 19, 20, 40, 60, 80, 100, 500]

    table = []
    for i in xrange(len(features)): 
        model_name = str(features[i]) + "model"
        model_dir = feature_paths[features[i]]
        row = [model_name]
        meta_score = MetaScore().score(model_name, model_dir, \
                            n_clusters, scored_clusters)
        for score in meta_score: 
            row.append(score)
        table.append(row)

    table = np.matrix(table).transpose()

    h = []
    for i in xrange(len(features)):
        h.append(table.item((0, i)))

    x = np.delete(table, (0), axis=0)
    x = np.delete(x, (0), axis=0)
    x = np.array(x).astype(np.float)

    if normplot: 
        x_normed = x / x.max(axis=0)
        for i in xrange(len(features)):
            plt.plot(x_normed[:,i], label=str(features[i])+'model')
        plt.legend(loc='upper left')
        my_xticks = []
        #print tabulate(x_normed, headers=h, floatfmt=".3f")

        for score in reversed(scored_clusters):
            my_xticks.append(str(score))
        plt.xticks(np.arange(len(scored_clusters)), my_xticks)

        #plt.show()

    else: 
        for i in xrange(len(features)):
            plt.plot(x[:,i], label=str(features[i])+'model')
        plt.legend(loc='upper left')
        my_xticks = []
        iterscores = iter(scored_clusters)
        next(iterscores)
        for score in iterscores:
            my_xticks.append(str(score))
        plt.xticks(np.arange(len(scored_clusters)), my_xticks)
        print tabulate(x, headers=h, floatfmt=".3f")

        plt.show()



def normalize(n):
    high = 1.0
    low = 0.0
    mins = np.min(n, axis=0)
    maxs = np.max(n, axis=0)
    rng = maxs - mins

    scaled_points = high - (((high - low) * (maxs - n)) / rng)

    return scaled_points

