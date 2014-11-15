
import numpy, scipy.io
import bci.signal, bci.features
import wrappers
import weka.arff

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

			scipy.io.savemat(destination_lists[i][j], {mTot: vmTot}, oned_as='row')

def batch_extracting_latencies(sources, chair, epoch,
	transpose=False, mTot='mTot', verbose=False):

	latency_lists = []

	for i, source in enumerate(sources):
		if verbose:
			print '[%d/%d] Extracting %s' % (i+1, len(sources), source)

		vmTot = wrappers.load_mat_variable(source, mTot)
		channel = chair['channel']
		threshold = chair['threshold'] * chair['constant']

		latencies = []

		for j, m in enumerate(vmTot):

			if transpose:
				m.data = numpy.transpose(m.data)

			latency = bci.features.extract_latency(
				m.data[channel-1], m.time, threshold, epoch)
			latencies.append(latency)

		latency_lists.append(latencies)

	return latency_lists

def batch_extracting_difference_latencies(sources, eye, epoch, coefficients,
	transpose=False, mTot='mTot', verbose=False):

	latency_lists = []

	for i, source in enumerate(sources):
		if verbose:
			print '[%d/%d] Extracting %s' % (i+1, len(sources), source)

		vmTot = wrappers.load_mat_variable(source, mTot)
		channel, channel1, channel2 = eye['channel'], eye['channel1'], eye['channel2']
		threshold = eye['threshold'] * numpy.abs(coefficients[i])

		latencies = []

		for j, m in enumerate(vmTot):

			if transpose:
				m.data = numpy.transpose(m.data)

			m.data[channel-1] = m.data[channel1-1] - m.data[channel2-1]
			m.data[channel-1] = bci.signal.butter_lowpass_filter(
				m.data[channel-1], epoch['frequency'], 5, 5)
			latency = bci.features.extract_latency(
				m.data[channel-1], m.time, threshold, epoch)
			latencies.append(latency)

		latency_lists.append(latencies)

	return latency_lists

def batch_extracting_features(sources, destinations,
	channels, configurations, epoch,
	latency_lists=None, start_offset=0, stop_offset=0,
	do_mean=False, do_power=False, transpose=False,
	mTot='mTot', featmat='featmat', mclass='mclass',
	verbose=False):

	for i, source in enumerate(sources):
		destination = destinations[i]

		if verbose:
			print '[%d/%d] Extracting %s' % (i+1, len(sources), source)

		vmTot = wrappers.load_mat_variable(source, mTot)

		vfeatmat = []

		for j, m in enumerate(vmTot):
			windows = []
			if latency_lists == None:
				for c in configurations:
					windows.extend(c.get_windows(epoch))
			else:
				latency = latency_lists[i][j]
				for c in configurations:
					c.set_relative_mode(latency, start_offset, stop_offset)
					windows.extend(c.get_windows(epoch))

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

		vmclass = [m.type for m in vmTot]

		scipy.io.savemat(destination, {featmat: vfeatmat, mclass: vmclass}, oned_as='row')

def batch_combining(source_lists, destinations, variable, axis,
	passing_variables=[], verbose=False):

	for i, sources in enumerate(source_lists):
		destination = destinations[i]

		if verbose:
			print '[%d/%d] Combining to %s' % (
				i+1, len(source_lists), destinations[i])

		wrappers.combine_mat_matrices(
			sources, destination, variable, axis, passing_variables)

def batch_converting(sources, destinations, relations,
	featmat='featmat', mclass='mclass', verbose=False):

	for i, source in enumerate(sources):
		destination = destinations[i]

		if verbose:
			print '[%d/%d] Converting %s' % (i+1, len(sources), source)

		vfeatmat = wrappers.load_mat_variable(source, featmat)
		vmclass = wrappers.load_mat_variable(source, mclass)

		relation = relations[i]
		attributes = [('BCI_%d' % (j+1), 'numeric')
			for j in range(len(vfeatmat[0]))]
		data = vfeatmat
		classes = ('class', '{4,5}')
		classifications = vmclass

		weka.arff.write_arff(destination, relation, attributes, data,
			classes, classifications)

def batch_infogain_evaluating(paths, classpath, threshold=0, verbose=False):

	evaluation_lists = []

	for i, path in enumerate(paths):
		if verbose:
			print '[%d/%d] Evaluating %s' % (i+1, len(paths), path)

		evaluation_lists.append(
			wrappers.evaluate_with_infogain(classpath, path, threshold))

	return evaluation_lists

def batch_infogain_svm_classifying(trainings, tests, classpath,
	threshold=0, verbose=False):

	accuracies = []

	for i, training in enumerate(trainings):
		test = tests[i]

		if verbose:
			print '[%d/%d] Classifying %s' % (i+1, len(trainings), training)

		accuracies.append(
			wrappers.classify_with_infogain_svm(
				classpath, training, test, threshold))

	return accuracies
