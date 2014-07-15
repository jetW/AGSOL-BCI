
import numpy, scipy.io
import bci.signal, bci.features
import wrappers
import weka.arff, weka.evaluate, weka.classify

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
	mclass='mclass', transpose=False, verbose=0):

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

		vmclass = [m.type for m in vmTot]

		scipy.io.savemat(destinations[i], {featmat: vfeatmat, mclass: vmclass})

def batch_combining(source_lists, destinations, variable, axis,
	passing_variables=[], verbose=0):

	for i, sources in enumerate(source_lists):
		if verbose >= 1:
			print '[%d/%d] Combining to %s' % (
				i+1, len(source_lists), destinations[i])

		matrix = wrappers.load_mat_variable(sources[0], variable)
		for source in sources[1:]:
			temp = wrappers.load_mat_variable(source, variable)
			matrix = numpy.concatenate((matrix, temp), axis=axis)

		dictionary = {variable: matrix}
		for pv in passing_variables:
			dictionary[pv] = wrappers.load_mat_variable(sources[0], pv)

		scipy.io.savemat(destinations[i], dictionary)

def batch_converting(sources, destinations, relations,
	featmat='featmat', mclass='mclass', verbose=0):

	for i, source in enumerate(sources):
		if verbose >= 1:
			print '[%d/%d] Converting %s' % (i+1, len(sources), source)

		vfeatmat = wrappers.load_mat_variable(source, featmat)
		vmclass = wrappers.load_mat_variable(source, mclass)

		relation = relations[i]
		attributes = [('BCI_%d' % (j+1), 'numeric')
			for j in range(len(vfeatmat[0]))]
		data = vfeatmat
		classes = ('class', '{4,5}')
		classifications = vmclass

		weka.arff.write_arff(destinations[i], relation, attributes, data,
			classes, classifications)

def batch_infogain_evaluating(paths, classpath, threshold=0, verbose=0):

	evaluation_lists = []

	for i, path in enumerate(paths):
		if verbose >= 1:
			print '[%d/%d] Evaluating %s' % (i+1, len(paths), path)

		output = weka.evaluate.evaluate_attribute(classpath,
			'InfoGainAttributeEval', 'Ranker -T %f' % threshold, path)
		evaluations = weka.evaluate.extract_evaluations(output)
		evaluation_lists.append(evaluations)

	return evaluation_lists

def batch_infogain_svm_classifying(trainings, tests, classpath, threshold=0, verbose=0):

	accuracies = []

	for i, training in enumerate(trainings):
		test = tests[i]
		if verbose >= 1:
			print '[%d/%d] Classifying %s' % (i+1, len(trainings), training)

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
