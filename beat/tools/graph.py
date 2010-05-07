from matplotlib.backends.backend_agg import FigureCanvasAgg as FigureCanvas
from matplotlib.figure import Figure
from django.template import loader
from django.http import HttpResponse

"""
This function exports a matplotlib graph to a given format. Expects a FigureCanvasAgg object (a canvas) to print as a figure.
Returns a HttpResponse with of the specified mimetype.
@param canvas The FigureCanvasAgg object.
@param format The prefered export format. Choose from (png,pdf,ps,eps,svg).
@param title The title of the exported document.
"""

def export(canvas, title, format='png'):
	# Set the mimetype of the HttpResponse
	mimetype = ''
	if (format is 'png'):
		mimetype = 'image/png'
	elif (format is 'pdf'):
		mimetype = 'application/pdf'
	elif (format is ('ps' or 'eps')):
		mimetype = 'application/postscript'
	elif (format is 'svg'):
		mimetype = 'image/svg+xml'
	response = HttpResponse(content_type=mimetype)
	
	# Show the user a 'Save as..' dialogue if the graph is not PNG.
	if (format is not 'png'):
		response['Content-Disposition'] = 'attachment; filename=%s.%s' % (title, format)
	# Print to canvas with the right format
	canvas.print_figure(filename=response, format=format)
	return response