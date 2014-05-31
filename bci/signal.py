
import scipy.signal

def butter_bandpass_filter(signal, frequency, band, order):
	# http://en.wikipedia.org/wiki/Nyquist-Shannon_sampling_theorem
	nyquist = float(frequency) / 2
	lower_cutoff, upper_cutoff = band
	Wn = [lower_cutoff / nyquist, upper_cutoff / nyquist]
	b, a = scipy.signal.butter(order, Wn, btype='bandpass')
	return scipy.signal.filtfilt(b, a, signal)
