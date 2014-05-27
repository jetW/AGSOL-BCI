
import csv, math, cmath

def load_channel_locations(path):
	electrodes = []
	with open(path) as f:
		csv_reader = csv.reader(f, delimiter=' ')
		for row in csv_reader:
			electrode = {
				'channel': int(row[0]),
				'phi': float(row[1]),
				'r': float(row[2]),
				'name': row[3].split('.')[0]
			}
			z = cmath.rect(electrode['r'], math.radians(electrode['phi']))
			electrode['x'] = z.real
			electrode['y'] = z.imag
			electrodes.append(electrode)
	return electrodes
