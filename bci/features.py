
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
	return [(_ceil_index(a, s, f), _floor_index(b, s, f))
		for (a, b) in windows]

def _ceil_index(time, start, frequency):
	return int(math.ceil((time - start) * frequency))

def _floor_index(time, start, frequency):
	return int(math.floor((time - start) * frequency))
