
# import numpy, scipy.io, sklearn.svm
import numpy, scipy.io
import bci.features
import weka.evaluate, weka.classify

def load_mat_variable(path, variable):
	mat = scipy.io.loadmat(path, struct_as_record=False, squeeze_me=True)
	return mat[variable]

def combine_mat_matrices(sources, destination, variable, axis, extra_variables):
	matrix = load_mat_variable(sources[0], variable)
	for source in sources[1:]:
		temp = load_mat_variable(source, variable)
		matrix = numpy.concatenate((matrix, temp), axis=axis)
	dictionary = {variable: matrix}
	for ev in extra_variables:
		dictionary[ev] = load_mat_variable(sources[0], ev)
	scipy.io.savemat(destination, dictionary)

def extract_latency(m, channel, threshold, epoch, latency_offset, verbose=False):
	try:
		return bci.features.extract_latency(
			m.data[channel-1], m.time, threshold, epoch)
	except StopIteration:
		latency = m.time[-1 - epoch['frequency'] * latency_offset]
		if verbose:
			message = '[Channel %d] No movement detected at Trial %d, using %f'
			print message % (channel, m.trial, latency)
		return latency

# def classify_with_svm(trainingX, trainingY, testX, testY):
# 	svc = sklearn.svm.SVC(kernel='linear')
# 	svc.fit(trainingX, trainingY)
# 	return svc.score(testX, testY)

def evaluate_with_infogain(classpath, datafile, threshold):
	output = weka.evaluate.evaluate_attribute(classpath,
		'InfoGainAttributeEval', 'Ranker -T %f' % threshold, datafile)
	return weka.evaluate.extract_evaluations(output)

def classify_with_infogain_svm(classpath, training, test, threshold):
	output = weka.classify.classify_data(classpath,
		'weka.classifiers.meta.FilteredClassifier ' +
		'-F "weka.filters.supervised.attribute.AttributeSelection ' +
		'-E \\"weka.attributeSelection.InfoGainAttributeEval\\" ' +
		'-S \\"weka.attributeSelection.Ranker -T %f\\"" ' % threshold +
		'-W weka.classifiers.functions.SMO',
		training, '-T "' + test + '"')
	return weka.classify.extract_test_accuracy(output)
