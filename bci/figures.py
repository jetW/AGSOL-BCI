
import pylab

def customized_bar_chart(coordinates, values, barwidth, **kwargs):
	if not isinstance(values[0], list):
		values = [values]
	colors = kwargs.get('colors', [None] * len(coordinates))
	texts = kwargs.get('texts', [''] * len(coordinates))

	ax = pylab.axes()
	for i in range(len(coordinates)):

		# Bars
		x, y = coordinates[i]
		color = colors[i]
		basewidth = barwidth * (0.5 + 1.5 * len(values))
		baseleft = x - basewidth * 0.5
		for j in range(len(values)):
			value = values[j][i]
			barleft = baseleft + barwidth * (0.5 + 1.5 * j)
			ax.broken_barh([(barleft, barwidth)], (y, value), facecolors=color)
		ax.broken_barh([(baseleft, basewidth)], (y, 0))

		# Texts
		text = texts[i]
		textx = kwargs.get('textx', 0)
		texty = kwargs.get('texty', 0)
		textha = kwargs.get('textha', 'center')
		textva = kwargs.get('textva', 'center')
		pylab.text(x + textx, y + texty, text, ha=textha, va=textva)

	pylab.axis('off')
