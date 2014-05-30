
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
