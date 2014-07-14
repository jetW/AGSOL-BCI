
import numpy, scipy.io
import bci.signal, bci.features
import wrappers

def batch_bandpass_filtering(sources, destination_lists, bands, channels,
	frequency, mTot='mTot', transpose=False, verbose=0):

	for i, source in enumerate(sources):
		if verbose >= 1:
			print '[%d/%d] Filtering %s' % (i+1, len(sources), source)

		vmTot = wrappers.load_mat_variable(source, mTot)

		for j, band in enumerate(bands):
			if verbose >= 2:
				print '[%d/%d] For band %s' % (j+1, len(bands), band)

			for k, m in enumerate(vmTot):
				if verbose >= 3:
					print '[%d/%d] At movement %s' % (k+1, len(vmTot), m.trial)

				if transpose:
					matrix, mx = numpy.transpose(m.data), []
				else:
					matrix, mx = m.data, []

				for channel in channels:
					mx.append(
						bci.signal.butter_bandpass_filter(
							matrix[channel-1], frequency, band, 5))

				if transpose:
					m.data = numpy.transpose(mx)
				else:
					m.data = mx

			scipy.io.savemat(destination_lists[i][j], {mTot: vmTot})

def batch_extracting(sources, destinations, windows, channels,
	do_mean=False, do_power=False, mTot='mTot', featmat='featmat',
	transpose=False, verbose=0):

	for i, source in enumerate(sources):
		if verbose >= 1:
			print '[%d/%d] Extracting %s' % (i+1, len(sources), source)

		vmTot = wrappers.load_mat_variable(source, mTot)

		vfeatmat = []

		for j, m in enumerate(vmTot):
			if verbose >= 2:
				print '[%d/%d] At movement %s' % (j+1, len(vmTot), m.trial)

			if transpose:
				matrix, mx = numpy.transpose(m.data), []
			else:
				matrix, mx = m.data, []

			for channel in channels:
				if do_mean:
					mx.extend(
						bci.features.extract_means(
							matrix[channel-1], windows))
				if do_power:
					mx.extend(
						bci.features.extract_powers(
							matrix[channel-1], windows))

			vfeatmat.append(mx)

		scipy.io.savemat(destinations[i], {featmat: vfeatmat})

def batch_combining(source_lists, destinations, variable, axis, verbose=0):
	for i, sources in enumerate(source_lists):
		if verbose >= 1:
			print '[%d/%d] Combining to %s' % (
				i+1, len(source_lists), destinations[i])

		matrix = wrappers.load_mat_variable(sources[0], variable)
		for source in sources[1:]:
			temp = wrappers.load_mat_variable(source, variable)
			matrix = numpy.concatenate((matrix, temp), axis=axis)
		scipy.io.savemat(destinations[i], {variable: matrix})
