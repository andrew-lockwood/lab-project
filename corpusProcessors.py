# Only needs to be ran once for creating a histogram of the data later on 
# Make sure the load path is correct at the top of binnedHistogram when used
class FrequencyDict (object): 
    def __init__ (self, score_dir = score_dir):
        """Creates and saves a frequency dictionary from Sentences().""" 
        sentences = Sentences()

        word_count = Counter()
        for sentence in sentences: 
            for word in sentence: 
                word_count[word] += 1

        save_path = os.path.join(score_dir, save)
        frequency_file = csv.writer(open(save_path, 'w')) 
        for word, frequency in word_count.iteritems(): 
            frequency_file.writerow([word, frequency])