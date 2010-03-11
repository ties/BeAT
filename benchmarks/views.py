from django.http import HttpResponse, HttpResponseRedirect
from django.contrib.auth.decorators import login_required
from django.template import RequestContext, loader
from django.shortcuts import render_to_response, redirect
import datetime

from beat.benchmarks.models import Benchmark
from forms import CompareForm

def simple(request, id):
	
	import numpy
	# General library stuff
	from matplotlib.backends.backend_agg import FigureCanvasAgg as FigureCanvas
	from matplotlib.figure import Figure
	from matplotlib.dates import DateFormatter
	fig=Figure()
	ax=fig.add_subplot(111)
	
	# DB stuff
	benchmark_IDs = id.split('+')
	benchmarks = Benchmark.objects.filter(pk__in=benchmark_IDs)
	states = [b.states_count for b in benchmarks]
	
	# Plot data
	width = 0.2
	ax.bar(numpy.arange(benchmarks.count()), states, width, align='center')
	ax.set_xticks(numpy.arange(2))
	ax.set_ylabel('States')
	ax.set_xlabel('Benchmark')
	
	# Output
	canvas = FigureCanvas(fig)
	response = HttpResponse(content_type='image/png')
	canvas.print_png(response)
	return response

#@login_required(redirect_field_name='next')
def index(request):
	
	t = loader.get_template('base.html')
	c = RequestContext(request, {
	})
	return HttpResponse(t.render(c));

def tables(request):
	t = loader.get_template('index_tables.html')
	c = RequestContext(request, {})
	return HttpResponse(t.render(c));

def benchmarks(request):
	benches = Benchmark.objects.all()
	t = loader.get_template('benchmarks.html')
	c = RequestContext(request, {
		'benchmarks' : benches
	})
	return HttpResponse(t.render(c))

def compare_post(request):
	if request.method == 'POST': # If the form has been submitted...
		form = CompareForm(request.POST) # A form bound to the POST data
		if form.is_valid(): # All validation rules pass
			# Process the data in form.cleaned_data
			b = form.cleaned_data['benchmarks']
			return HttpResponseRedirect('/compare/' + "+".join([str(bench.id) for bench in b]) + '/') # Redirect after POST
	else:
		return redirect(benchmarks.views.benchmarks)

def compare(request, id):
	t = loader.get_template('compare.html')
	b = id.split('+')
	c = RequestContext(request, {
		'benchmarks' : b
	})
	return HttpResponse(t.render(c)) # Redirect after POST

#@login_required()
#def mudkip(request):

#def index(request):
#	return HttpResponse('Hello world.')