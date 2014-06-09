
import scipy.io, sklearn.svm
import bci.features

def import_mTot(path, mTot='mTot'):
	mat = scipy.io.loadmat(path, struct_as_record = False, squeeze_me = True)
	return mat[mTot]

def extract_latency(m, channel, threshold, epoch, verbose=False):
	try:
		return bci.features.extract_latency(
			m.data[channel - 1], m.time, epoch, threshold)
	except StopIteration:
		if verbose:
			message = '[Channel %d] No movement detected at Trial %d'
			print message % (channel, m.trial)
		return m.time[-1]

def classify_with_svm(trainingX, trainingY, testX, testY):
	svc = sklearn.svm.SVC(kernel='linear')
	svc.fit(trainingX, trainingY)
	return svc.score(testX, testY)
