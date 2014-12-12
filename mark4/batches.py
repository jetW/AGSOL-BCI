
import numpy, scipy.io
import bci.signal, bci.features
import weka.arff, weka.evaluate, weka.classify

def _loadmat(path):
	return scipy.io.loadmat(path, struct_as_record=False, squeeze_me=True)

def batch_mdata_transpose(sources, destinations):
	for i, source in enumerate(sources):
		mTot = _loadmat(source)['mTot']
		for j, m in enumerate(mTot):
			m.data = numpy.transpose(m.data)
		scipy.io.savemat(destinations[i], {'mTot': mTot}, oned_as='row')

def batch_bandpass_filtering(sources, destination_lists,
	bands, channels, frequency, verbose=0):

	for i, source in enumerate(sources):
		if verbose >= 1:
			print '[%d/%d] Filtering %s' % (i+1, len(sources), source)

		mTot = _loadmat(source)['mTot']
		for j, band in enumerate(bands):
			if verbose >= 2:
				print '[%d/%d] For band %s' % (j+1, len(bands), band)

			for k, m in enumerate(mTot):
				if verbose >= 3:
					print '[%d/%d] At movement %s' % (k+1, len(mTot), m.trial)

				for channel in channels:
					m.data[channel-1] = bci.signal.butter_bandpass_filter(
						m.data[channel-1], frequency, band, 5)

			scipy.io.savemat(destination_lists[i][j], {'mTot': mTot}, oned_as='row')

def batch_extracting_latencies(sources, epoch, chair):
	threshold = chair['threshold'] * chair['constant']
	channel = chair['channel']

	latency_lists = []
	for i, source in enumerate(sources):
		mTot = _loadmat(source)['mTot']

		latencies = []
		for j, m in enumerate(mTot):
			latency = bci.features.extract_latency(
				m.data[channel-1], m.time, threshold, epoch)
			latencies.append(latency)

		latency_lists.append(latencies)
	return latency_lists

def batch_extracting_difference_latencies(sources, ksources, epoch, eye):
	channel, channel1, channel2 = eye['channel'], eye['channel1'], eye['channel2']

	latency_lists = []
	for i, source in enumerate(sources):
		ksource = ksources[i]

		mTot = _loadmat(source)['mTot']
		cal_k = _loadmat(ksource)['cal_k']
		threshold = eye['threshold'] * numpy.abs(cal_k)

		latencies = []
		for j, m in enumerate(mTot):
			m.data[channel-1] = m.data[channel1-1] - m.data[channel2-1]
			m.data[channel-1] = bci.signal.butter_lowpass_filter(
				m.data[channel-1], epoch['frequency'], 5, 5)
			latency = bci.features.extract_latency(
				m.data[channel-1], m.time, threshold, epoch)
			latencies.append(latency)

		latency_lists.append(latencies)
	return latency_lists

def batch_configure_windows(configurations, epoch, nsources, nmovements,
	latency_lists=None, start_offset=0, stop_offset=0):

	windows_lists = []
	for i in range(nsources):

		windows_list = []
		for j in range(nmovements):

			windows = []
			if latency_lists == None:
				for c in configurations:
					windows.extend(c.get_windows(epoch))
			else:
				latency = latency_lists[i][j]
				for c in configurations:
					c.set_relative_mode(latency, start_offset, stop_offset)
					windows.extend(c.get_windows(epoch))

			windows_list.append(windows)

		windows_lists.append(windows_list)
	return windows_lists

def batch_extracting_features(sources, destinations,
	channels, windows_lists, do_mean=False, do_power=False):

	for i, source in enumerate(sources):
		destination = destinations[i]

		mTot = _loadmat(source)['mTot']

		featmat = []
		for j, m in enumerate(mTot):
			windows = windows_lists[i][j]

			row = []
			if do_mean:
				for channel in channels:
					row.extend(bci.features.extract_means(m.data[channel-1], windows))
			if do_power:
				for channel in channels:
					row.extend(bci.features.extract_powers(m.data[channel-1], windows))

			featmat.append(row)

		mclass = [m.type for m in mTot]

		scipy.io.savemat(destination, {'featmat': featmat, 'mclass': mclass}, oned_as='row')

def batch_combining(source_lists, destinations):
	for i, sources in enumerate(source_lists):
		destination = destinations[i]

		mat = _loadmat(sources[0])
		featmat = mat['featmat']
		mclass = mat['mclass']

		for source in sources[1:]:
			featmat2 = _loadmat(source)['featmat']
			featmat = numpy.concatenate((featmat, featmat2), axis=1)

		dictionary = {'featmat': featmat, 'mclass': mclass}
		scipy.io.savemat(destination, dictionary, oned_as='row')

def batch_converting(sources, destinations, relations):
	for i, source in enumerate(sources):
		destination = destinations[i]

		mat = _loadmat(source)
		featmat = mat['featmat']
		mclass = mat['mclass']

		relation = relations[i]
		attributes = [('BCI_%d' % (j+1), 'numeric')
			for j in range(len(featmat[0]))]
		data = featmat
		classes = ('class', '{4,5}')
		classifications = mclass

		weka.arff.write_arff(destination, relation, attributes, data,
			classes, classifications)

def batch_infogain_evaluating(paths, classpath, threshold=0):
	evaluation_lists = []
	for i, path in enumerate(paths):
		output = weka.evaluate.evaluate_attribute(classpath,
			'InfoGainAttributeEval', 'Ranker -T %f' % threshold, path)
		evaluations = weka.evaluate.extract_evaluations(output)
		evaluation_lists.append(evaluations)
	return evaluation_lists

def batch_infogain_svm_classifying(trainings, tests, classpath, threshold=0):
	accuracies = []
	for i, training in enumerate(trainings):
		test = tests[i]
		output = weka.classify.classify_data(classpath,
			'weka.classifiers.meta.FilteredClassifier ' +
			'-F "weka.filters.supervised.attribute.AttributeSelection ' +
			'-E \\"weka.attributeSelection.InfoGainAttributeEval\\" ' +
			'-S \\"weka.attributeSelection.Ranker -T %f\\"" ' % threshold +
			'-W weka.classifiers.functions.SMO',
			training, '-T "' + test + '"')
		accuracy = weka.classify.extract_test_accuracy(output)
		accuracies.append(accuracy)
	return accuracies
