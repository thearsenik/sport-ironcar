# Class used to store Rn results and constitute batch  input data
class RnMemory:
    def __init__(self, max_memory):
        self._max_memory = max_memory
        self._samples = []

	# Add new item
    def add_sample(self, sample):
        self._samples.append(sample)
        if len(self._samples) > self._max_memory:
            self._samples.pop(0)

	# Return a randomly defined set of nb_samples items from memory
    def sample(self, nb_samples):
        if nb_samples > len(self._samples):
            return random.sample(self._samples, len(self._samples))
        else:
            return random.sample(self._samples, nb_samples)
