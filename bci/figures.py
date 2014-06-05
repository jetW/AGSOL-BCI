
import pylab, numpy
import stats

def customized_bar_chart(coordinates, values, barwidth, colors=None):

	# Validate parameters
	values = [values] if not isinstance(values[0], list) else values
	colors = ['b'] * len(coordinates) if colors == None else colors

	ax = pylab.axes()
	for i, (x, y) in enumerate(coordinates):

		# Calculate and draw the base of bars
		basewidth = barwidth * (0.5 + 1.5 * len(values))
		baseleft = x - basewidth * 0.5
		ax.broken_barh([(baseleft, basewidth)], (y, 0))

		# Calculate and draw the body of bars
		for j, vs in enumerate(values):
			barleft = baseleft + barwidth * (0.5 + 1.5 * j)
			ax.broken_barh([(barleft, barwidth)], (y, vs[i]), facecolors=colors[i])

	pylab.axis('off')

def customized_scatter_plot(coordinates, sizes=None, scale=20, colors=None, grayscale=False):

	# Validate and rescale data
	if sizes == None:
		sizes = [1] * len(coordinates)
	else:
		sizes = stats.rescale(sizes, 0.01, 1)
	if colors == None:
		if grayscale:
			colors = ['0.75'] * len(coordinates)
		else:
			colors = ['b'] * len(coordinates)
	else:
		colors = stats.rescale(colors, 0.01, 1)

	# Map the data to coordinates, sizes, and colors
	xs = [x for (x, y) in coordinates]
	ys = [y for (x, y) in coordinates]
	ss = [s * scale for s in sizes]
	cs = [str(c) for c in colors] if grayscale else colors

	# Draw the scatter plot
	pylab.scatter(xs, ys, ss, cs)
	pylab.axis('off')

def draw_texts(coordinates, texts, textx=0, texty=0, textha='center', textva='center'):
	for i, (x, y) in enumerate(coordinates):
		pylab.text(x + textx, y + texty, texts[i], ha=textha, va=textva)

def grouped_bar_chart(values, errors=None, colors=None, labels=None, xticks=None):

	# Calculate implicit parameters
	ngroups = len(values)
	nbars = len(values[0])
	barwidth = 1.0 / (ngroups + 1)

	# Validate optional parameters
	errors = [None] * ngroups if errors == None else errors
	colors = [None] * ngroups if colors == None else colors
	labels = [''] * ngroups if labels == None else labels
	xticks = range(1, nbars + 1) if xticks == None else xticks

	for i in range(ngroups):

		# Calculate and draw bars
		groupleft = 1 + barwidth * (-ngroups / 2.0 + i)
		groupright = groupleft + nbars
		pylab.bar(numpy.arange(groupleft, groupright), values[i], yerr=errors[i],
			width=barwidth, color=colors[i], ecolor='k', label=labels[i])

		# Calculate and draw accessories
		pylab.xticks(range(1, len(xticks) + 1), xticks)
		pylab.xlim(0, len(xticks) + 1)
		if len(''.join(labels)) != 0:
			pylab.legend()
