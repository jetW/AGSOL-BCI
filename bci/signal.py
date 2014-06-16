
import scipy.signal, numpy

def butter_bandpass_filter(signal, frequency, band, order):
	# http://en.wikipedia.org/wiki/Nyquist-Shannon_sampling_theorem
	nyquist = float(frequency) / 2
	lower_cutoff, upper_cutoff = band
	Wn = [lower_cutoff / nyquist, upper_cutoff / nyquist]
	b, a = scipy.signal.butter(order, Wn, btype='bandpass')
	return scipy.signal.filtfilt(b, a, signal)

def laplacian_filter(signal_matrix, laplacian_matrix):
	# In the signal matrix:
	# Each row is a sampling point; each column is a channel
	# In the Laplacian matrix:
	# Each row is an output channel; each column is an input channel
	filtered_signal_matrix = []
	for signal in signal_matrix:
		filtered_signal = numpy.inner(signal, laplacian_matrix)
		filtered_signal_matrix.append(filtered_signal)
	return filtered_signal_matrix
