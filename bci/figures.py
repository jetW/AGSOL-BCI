
import pylab

def customized_bar_chart(coordinates, values, texts, barwidth, **kwargs):
	ax = pylab.axes()
	for i in range(len(coordinates)):

		# Bars
		x, y = coordinates[i]
		value = values[i]
		ax.broken_barh([(x - barwidth * 0.5, barwidth)], (y, value))
		ax.broken_barh([(x - barwidth, barwidth * 2)], (y, 0))

		# Texts
		text = texts[i]
		textx = kwargs.get('textx', 0)
		texty = kwargs.get('texty', 0)
		textha = kwargs.get('textha', 'center')
		textva = kwargs.get('textva', 'center')
		pylab.text(x + textx, y + texty, text, ha=textha, va=textva)

	pylab.axis('off')
