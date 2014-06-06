
import scipy.stats, numpy

def map(x, old_min, old_max, new_min, new_max):
	old_range = old_max - old_min
	new_range = new_max - new_min
	if old_range != 0:
		return float(x - old_min) / old_range * new_range + new_min
	else:
		return float(new_min + new_max) / 2

def rescale(array, new_min, new_max):
	old_max = max(array)
	old_min = min(array)
	return [map(x, old_min, old_max, new_min, new_max) for x in array]

def normalize(array):
	s = float(sum(array))
	return [e / s for e in array]

def ttests(matrix1, matrix2):
	# Each row is a sample; each column is a variable
	# T-tests are comparing means within pairs of variables from two matrices
	return scipy.stats.ttest_ind(matrix1, matrix2)

def anova(matrix):
	# Each row is a sample; each column is a variable
	# ANOVA is comparing variances across all variables
	tmatrix = numpy.transpose(matrix)
	return scipy.stats.f_oneway(*tmatrix)
