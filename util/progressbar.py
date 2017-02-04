"""Simple progress bar that displays on the command line."""
import sys


class ProgressBar(object): 
    def __init__ (self, total):
        self.total = total
        self.iteration = 0
        self.print_progress(self.iteration, self.total, prefix = 'Progress:', \
                        suffix = 'Complete', barLength = 50)

    def step (self):
        self.iteration += 1
        self.print_progress (self.iteration, self.total, prefix = 'Progress:', \
                        suffix = 'Complete', barLength = 50)

    def print_progress (self, iteration, total, prefix = '', suffix = '', decimals = 2, barLength = 100):
        """
            Call in a loop to create terminal progress bar
                iteration   - Required  : current iteration (Int)
                total       - Required  : total iterations (Int)
                prefix      - Optional  : prefix string (Str)
                suffix      - Optional  : suffix string (Str)
                decimals    - Optional  : number of decimals in percent complete (Int)
                barLength   - Optional  : character length of bar (Int)
        """
        filledLength    = int(round(barLength * iteration / float(total)))
        percents        = round(100.00 * (iteration / float(total)), decimals)
        bar             = '|' * filledLength + '-' * (barLength - filledLength)
        sys.stdout.write('\r%s |%s| %s%s %s' % (prefix, bar, percents, '%', suffix)),
        sys.stdout.flush()
        if iteration == total:
            sys.stdout.write('\n')
            sys.stdout.flush()



