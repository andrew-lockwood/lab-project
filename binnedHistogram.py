#######################################################################
#
# These variables set up the path for the csv files used below. The 
# first is strictly a word count of the corpus, and the second is a 
# score of two models from another file. 
#   NOTE: the second file has the header 
#          "word, union, intersection, jaccard index, jaccard distance"
#
#######################################################################

frequency_load_path = \
'/media/removable/SD Card/frontiers_data/corpus/parsed_frequency_counts.csv'
jaccard_load_path = \
'/media/removable/SD Card/frontiers_data/models/every_score50and300N25.csv'

#######################################################################
#
# File dependencies: The first two need to be installed, the second 
# four are all native to python. P
#   NOTE: Pylab >>> numpy in size, if only numpy is installed the 
#           code will still work, you just can't display the histogram
#
#######################################################################

import numpy as np
import pylab as P

from collections import defaultdict
from random import shuffle
import math
import csv
import sys

#######################################################################
#
# Creates several dictionaries and arrays with the ultimate goal of 
# binning the Jaccard distances in the correct way. 
# It basically does this by mapping 'word --> frequencies' then 
# 'frequencies --> Jaccard Distances', and finally combining the 
# two in the order of a sorted frequency array. It works. 
#
#######################################################################

class BinnedFrequencyData (object): 
    def __init__ (self, min_count = 5, \
                        f_load_path = frequency_load_path, \
                        j_load_path = jaccard_load_path, \
                        bin_num = 40):
        """Manually bins frequency data given to it."""
        # STEP 1: Create a frequency dictionary and array 
        #       The array needs to be sorted for binning later on
        d = {}
        a = []
        self.total_words = 0
        for word, frequency in csv.reader(open(f_load_path)): 
            if int(frequency) >= min_count:
                d[word] = int(frequency) 
                a.append(int(frequency))
                self.total_words += 1

        frequency_array = np.array(a)
        frequency_array[::-1].sort()

        # STEP 2: Create a dictionary of lists 
        dic = defaultdict(list)

        with open(j_load_path) as f: 
            reader = csv.reader(f)
            reader.next()
            for word, u, i, index, distance in reader:
                frequency = d[word]
                dic[frequency].append(index)

        for frequency in dic: 
            shuffle(dic[frequency])     # Shuffle each list 

        # STEP 3: Create a list of lists 
        binned_list = []
        current_bin = []

        i = 1
        data_size = len(frequency_array)
        # Always round up the bin size
        bin_size = math.ceil(data_size / float(bin_num))  

        for value in frequency_array: 
            if i == bin_size:
                current_bin.append(value)
                binned_list.append(current_bin)
                # Reset the bin values 
                i = 1
                current_bin = []
            else: 
                current_bin.append(value)
                i += 1

        binned_list.append(current_bin)     # Append the last bin

        # STEP 4: Turn frequency bins in the last step into Jaccard bins
        #   by popping values off the dictionary of lists  
        jaccard_bins = []
        for b in binned_list: 
            jaccard_array = []
            for frequency in b: 
                jaccard_array.append(float(dic[frequency].pop()))
            jaccard_bins.append(jaccard_array)

        # STEP 5: Create an array of NP arrays for statistical analysis
        np_jaccard_bins = []
        for b in jaccard_bins: 
            np_jaccard_bins.append(np.array(b))

        # STEP 6: Set class variables
        self.bin_num = bin_num
        self.jaccard_bins = jaccard_bins
        self.np_jaccard_bins = np_jaccard_bins

        # STEP 7: Calculate frequency averages
        self.frequency_averages = []
        for x in binned_list: 
            y = np.array(x)
            f_mean = np.mean(y)
            self.frequency_averages.append(f_mean)


    def graph_data (self, n): 
        first_n_bins = []
        i = 0
        for x in self.jaccard_bins: 
            if i < n:
                first_n_bins.append(x)
                i += 1
            else: 
                break
        return first_n_bins

    def display_bin_summary (self, n):
        """Displays bin data to the terminal."""
        print '             |          \033[4mbox plot summary\033[0m         | '
        print 'bin |  mean  | min   1st q  median  3rd q   max  |    sum   | size | f_avg'
        i = 0
        bin_total_words = 0
        for x in self.np_jaccard_bins: 
            if i < n:
                # Calculate statistics 
                x_total = x.sum()
                x_mean = np.mean(x)
                x_min = x.min()
                x_first_q = np.percentile(x, 25)
                x_second_q = np.percentile(x, 50)
                x_third_q = np.percentile(x, 75)
                x_max = x.max()
                x_size = len(x)
                frequency_mean = self.frequency_averages[i]

                # Write bin line to terminal
                sys.stdout.write('%3i | %.04f | ' \
                                % (i+1, x_mean))
                sys.stdout.write('%.03f %.03f  %.04f  %.03f  %.03f | ' \
                                % (x_min, x_first_q, x_second_q, x_third_q, x_max))
                sys.stdout.write('%.04f | %i | %0.2f \n' \
                                % (x_total, x_size, frequency_mean))

                bin_total_words += x_size
                i += 1
            else: 
                break
        sys.stdout.write('Word percent of original: %i/%i = %0.4f \n' % \
                        (bin_total_words, self.total_words, \
                        bin_total_words/float(self.total_words)))


# If bin_num <= n, every bin will be represented.
# For n < bin_num, only the largest n bins will be represented.
def display_boxplot (bin_num = 30, n = 40): 
    """Prints a boxplot in a seperate window and the bin summary in the terminal."""
    fd = BinnedFrequencyData(bin_num = bin_num)
    fd.display_bin_summary(n)
    P.boxplot(fd.graph_data(n), notch = False, showmeans = True, showfliers = False)
    P.title('50 by 300 features with 25 similar words')
    P.ylabel('Jaccard Distance')
    P.xlabel('bins')
    P.show()


# If pylab is not installed, run this: 
#fd = BinnedFrequencyData(bin_num = bin_num)
#fd.display_bin_summary()

# If pylab is installed, this method will still display the above, 
# but also print out the histogram
display_boxplot()




