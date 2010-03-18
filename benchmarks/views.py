from django.http import HttpResponse, HttpResponseRedirect
from django.contrib.auth.decorators import login_required
from django.template import RequestContext, loader
from django.shortcuts import render_to_response, redirect
import datetime
from beat.benchmarks.models import Benchmark
from forms import *

# Log upload
from beat.benchmarks.log_upload import handle_uploaded_file

# Log upload
def upload_log(request):
	if request.method == 'POST':
		form = UploadLogForm(request.POST, request.FILES)
		if form.is_valid():
			title = form.cleaned_data['title']
			handle_uploaded_file(request.FILES['file'], title)
			return HttpResponseRedirect('/')
	else:
		form = UploadLogForm()
	return render_to_response('upload_log.html', {'form': form}, context_instance=RequestContext(request))

def simple(request, id):
	
	import numpy
	# General library stuff
	from matplotlib.backends.backend_agg import FigureCanvasAgg as FigureCanvas
	from matplotlib.figure import Figure
	fig=Figure(facecolor='w')
	ax=fig.add_subplot(111)
	
	# DB stuff
	benchmark_IDs = id.split('+')
	benchmarks = Benchmark.objects.filter(pk__in=benchmark_IDs)
	states = [b.states_count for b in benchmarks]
	# Plot data
	width = 0.4
	ax.bar(numpy.arange(benchmarks.count()), states, width, align='center')
	ax.set_xticks(numpy.arange(benchmarks.count()))
	ax.set_xticklabels(benchmarks, size='small')
	ax.set_ylabel('States')
	ax.set_xlabel('Benchmark')
	#ax.figure.set_figheight(2)
	ax.grid(True)
	# Output
	fig.set_size_inches(6,6)
	canvas = FigureCanvas(fig)
	response = HttpResponse(content_type='image/png')
	canvas.print_png(response)
	return response

def graph_model(request, models=None, type='States count', options=None):
	import numpy as np
	# General library stuff
	from matplotlib.backends.backend_agg import FigureCanvasAgg as FigureCanvas
	from matplotlib.lines import Line2D
	from matplotlib.figure import Figure
	
	#DB stuff
	from django.db.models import Count
	from beat.benchmarks.models import Model

	fig=Figure(facecolor='w')
	ax=fig.add_subplot(111)
	
	colors = ('b', 'g', 'r', 'c', 'm', 'y', 'k')
	styles = ['_', '-', '--', ':']
	markers = ['+','o','x']

	#states = [b.states_count for b in benchmarks]
	# Plot data
	axisNum = 0
	modelNames = Model.objects.values('name').annotate(num_models=Count('name'))
	for m in modelNames:
		axisNum += 1
		style = styles[axisNum % len(styles) ]
		color = colors[axisNum % len(colors) ]
		marker = markers[axisNum % len(markers) ]
		
		benchmarks = Benchmark.objects.filter(model_ID__name__exact = m['name'])
		if models is not None:
			benchmarks = benchmarks.filter(model_ID__name in models)
		types = {
			'Transition count': [b.transition_count for b in benchmarks],
			'States count': [b.states_count for b in benchmarks],
			'Memory VSIZE': [b.memory_VSIZE for b in benchmarks],
			'Memory RSS': [b.memory_RSS for b in benchmarks],
		}[type]
		lines = ax.plot(
			[b.model_ID.version for b in benchmarks], 
			types, 
			marker + style + color,
			label = m['name'])

	#Mark-up
	ax.set_title(type + ' vs Version')
	ax.legend()
	ax.set_ylabel(type)
	ax.set_xlabel('Version')
	# Output
	canvas = FigureCanvas(fig)
	#fig.savefig('benchmark.pdf')
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

def compare_model(request):
	if request.method == 'POST': # If the form has been submitted...
		form = CompareModelsForm(request.POST) # A form bound to the POST data
		if form.is_valid(): # All validation rules pass
			return render_to_response('compare_models.html', context_instance=RequestContext(request)) # Redirect after POST
	else:
		form = CompareModelsForm() # An unbound form
		
	return render_to_response('compare_models_form.html', {
		'form': form, 
	}, context_instance=RequestContext(request))

	
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