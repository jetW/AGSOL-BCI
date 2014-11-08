
import math, numpy

class WindowConfiguration:
	def __init__(self, start, stop, step, size):
		self.start = start
		self.stop = stop
		self.step = step
		self.size = size
		self.mode = 'absolute'
	def set_relative_mode(self, latency, relative_start, relative_stop):
		self.mode = 'relative'
		self.relative_start = relative_start
		self.relative_stop = relative_stop
		self.start = latency + relative_start
		self.stop = latency + relative_stop
	def get_windows(self, epoch):
		windows = []
		start, stop, step, size = self.start, self.stop, self.step, self.size
		for index, left in enumerate(numpy.arange(start, stop, step)):
			right = left + size
			# Due to the inaccuracy of float numbers
			if right <= stop + 0.001:
				window = Window(left, right, self, index)
				window.find_indices(epoch)
				windows.append(window)
		return windows

class Window:
	def __init__(self, left, right, configuration, index):
		self.left = left
		self.right = right
		self.configuration = configuration
		self.index = index
	def find_indices(self, epoch):
		start, frequency = epoch['start'], epoch['frequency']
		self.i = self._ceil_index(self.left, start, frequency)
		self.j = self._floor_index(self.right, start, frequency)
	def _ceil_index(self, time, start, frequency):
		return int(math.ceil((time - start) * frequency))
	def _floor_index(self, time, start, frequency):
		return int(math.floor((time - start) * frequency))
	def __str__(self):
		c = self.configuration
		if c.mode == 'absolute':
			return str((self.left, self.right, c.mode))
		elif c.mode == 'relative':
			left = c.relative_start + c.step * self.index
			right = left + c.size
			return str((left, right, c.mode))
		else:
			return None

def extract_mean(signal):
	return numpy.mean(signal)

def extract_means(signal, windows):
	return [extract_mean(signal[w.i:w.j]) for w in windows]

def extract_power(signal):
	# http://en.wikipedia.org/wiki/Parseval's_theorem
	return numpy.log(numpy.sum(numpy.square(signal)))

def extract_powers(signal, windows):
	return [extract_power(signal[w.i:w.j]) for w in windows]

def extract_latency(signal, time, threshold, epoch, reference=0):
	start = epoch['start']
	frequency = epoch['frequency']
	baseindex = (reference - start) * frequency
	baseline = signal[baseindex]
	remainder = signal[baseindex:]
	offset = next(i for i, v in enumerate(remainder)
		if abs(v - baseline) >= threshold)
	return time[baseindex + offset]

def extract_max_amplitude(signal, epoch, reference=0):
	start = epoch['start']
	frequency = epoch['frequency']
	baseindex = (reference - start) * frequency
	baseline = signal[baseindex]
	remainder = signal[baseindex:]
	positive_difference = abs(max(remainder) - baseline)
	negative_difference = abs(min(remainder) - baseline)
	return max(positive_difference, negative_difference)
