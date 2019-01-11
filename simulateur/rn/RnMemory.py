import random
import logging
import sys
sys.path.insert(0, '../')
import config

logging.basicConfig(filename=config.logFile,level=logging.DEBUG, format='%(asctime)s %(message)s')

# Class used to store Rn results and constitute batch  input data
class RnMemory:
    def __init__(self, max_memory):
        self._max_memory = max_memory
        self._samples = []

	# Add new item
    def add_sample(self, sample):
#       logging.debug("RnMemory nbItems="+str(len(self._samples)))
        self._samples.append(sample)
        if len(self._samples) > self._max_memory:
#            logging.debug("RnMemory pop first element...")
            self._samples.pop(0)

	# Return a randomly defined set of nb_samples items from memory
    def sample(self, nb_samples):
        if nb_samples > len(self._samples):
            sample = random.sample(self._samples, len(self._samples))
        else:
            sample = random.sample(self._samples, nb_samples)
        return sample