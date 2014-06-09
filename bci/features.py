
import math, numpy

def generate_sliding_window(configurations, epoch):
	windows = list_windows(configurations)
	indices = index_windows(windows, epoch)
	return indices

def list_windows(configurations):
	if not isinstance(configurations, list):
		configurations = [configurations]
	windows = []
	for c in configurations:
		start = c['start']
		stop = c['stop']
		step = c['step']
		size = c['size']
		windows.extend([(s, s + size)
			for s in numpy.arange(start, stop, step)
			if s + size <= stop])
	return windows

def index_windows(windows, epoch):
	s = epoch['start']
	f = epoch['frequency']
	return [(_ceil_index(a, s, f), _floor_index(b, s, f) + 1)
		for (a, b) in windows]

def _ceil_index(time, start, frequency):
	return int(math.ceil((time - start) * frequency))

def _floor_index(time, start, frequency):
	return int(math.floor((time - start) * frequency))

def extract_mean(signal):
	return numpy.mean(signal)

def extract_means(signal, windows):
	return [extract_mean(signal[a:b]) for (a, b) in windows]

def extract_power(signal):
	# http://en.wikipedia.org/wiki/Parseval's_theorem
	return numpy.log(numpy.sum(numpy.square(signal)))

def extract_powers(signal, windows):
	return [extract_power(signal[a:b]) for (a, b) in windows]

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
