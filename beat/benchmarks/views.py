from django.http import HttpResponse, HttpResponseRedirect
from django.contrib.auth.decorators import login_required
from django.template import RequestContext, loader
from django.shortcuts import render_to_response, redirect, get_list_or_404
import datetime
from filereader import FileReader
from beat.benchmarks.models import Benchmark, Comparison
from forms import *
from django.core.paginator import Paginator, InvalidPage, EmptyPage

# Log upload
from beat.benchmarks.log_upload import handle_uploaded_file

# Log upload
def upload_log(request):
	if request.method == 'POST':
		form = UploadLogForm(request.POST, request.FILES)
		if form.is_valid():
			title = form.cleaned_data['title']
			handle_uploaded_file(request.FILES['file'], title)
			try:
				FileReader.main(FileReader(), ['C:\Vakken\OWP\\beat\site_media\upload\logs\\' + "%s"%(request.FILES['file'])], 2)
			except:
				return HttpResponse('error')
			else:
				return HttpResponse('ok')
	else:
		form = UploadLogForm()
	return render_to_response('upload_log.html', {'form': form}, context_instance=RequestContext(request))

def simple(request, id):
	
	import numpy
	# General library stuff
	from matplotlib.backends.backend_agg import FigureCanvasAgg as FigureCanvas
	from matplotlib.figure import Figure
	fig=Figure(facecolor='w')
	ax=fig.add_subplot(211)
	
	# DB stuff
	benchmark_IDs = Comparison.objects.get(pk=id)
	benchmarks = Benchmark.objects.filter(pk__in=benchmark_IDs.benchmarks.split(','))
	states = [b.states_count for b in benchmarks]
	elapsed_time = [b.elapsed_time for b in benchmarks]
	memory_vsize = [b.memory_VSIZE for b in benchmarks]
	
	# Plot data
	width = 0.4
	numBench = benchmarks.count()
	ax.bar(numpy.arange(numBench), states, width, align='center')
	ax.set_xticks(numpy.arange(benchmarks.count()))
	ax.set_xticklabels(benchmarks, size='small')
	ax.set_ylabel('States')
	#ax.figure.set_figheight(2)
	ax.grid(True)
	
	# Output
	ax=fig.add_subplot(212)
	ax.plot(elapsed_time, memory_vsize, 'ro')
	ax.set_xlabel('Elapsed Time')
	ax.set_ylabel('Memory VSIZE')
	
	#fig.set_size_inches(4,8)
	canvas = FigureCanvas(fig)
	response = HttpResponse(content_type='image/png')
	canvas.print_png(response)
	return response

def graph_model(request, models=None, type='states', options=None):
	# General library stuff
	import numpy as np
	from matplotlib.backends.backend_agg import FigureCanvasAgg as FigureCanvas
	from matplotlib.lines import Line2D
	from matplotlib.figure import Figure
	
	#DB stuff
	from django.db.models import Count
	from beat.benchmarks.models import Model

	fig=Figure(facecolor='w')
	ax=fig.add_subplot(111)
	
	colors = ('b', 'g', 'r', 'c', 'm', 'y', 'k')
	styles = ['-', '--', ':']
	markers = ['+','o','x']

	# Plot data
	axisNum = 0
	modelNames = Model.objects.values('name').annotate(num_models=Count('name'))
	for m in modelNames:
		axisNum += 1
		style = styles[axisNum % len(styles) ]
		color = colors[axisNum % len(colors) ]
		marker = markers[axisNum % len(markers) ]
		
		benchmarks = Benchmark.objects.filter(model__name__exact = m['name'])
		if models is not None:
			benchmarks = benchmarks.filter(model__name in models)
		types = {
			'transitions': [b.transition_count for b in benchmarks],
			'states': [b.states_count for b in benchmarks],
			'vsize': [b.memory_VSIZE for b in benchmarks],
			'rss': [b.memory_RSS for b in benchmarks],
		}[type]
		lines = ax.plot(
			[b.model.version for b in benchmarks], 
			types, 
			marker + style + color,
			label = m['name'])

	#Mark-up
	ax.set_title(type + ' vs Version')
	leg = ax.legend()
	for t in leg.get_texts():
		t.set_fontsize('small')
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
	return render_to_response('base.html', context_instance=RequestContext(request))

@login_required
def benchmarks(request, numResults=25):
	benches = Benchmark.objects.all()
	paginator = Paginator(benches, numResults, orphans=10)
	
	# Make sure page request is an int. If not, deliver first page.
	try:
		page = int(request.GET.get('page', '1'))
	except ValueError:
		page = 1

	# If page request (9999) is out of range, deliver last page of results.
	try:
		benches = paginator.page(page)
	except (EmptyPage, InvalidPage):
		benches = paginator.page(paginator.num_pages)

	return render_to_response('benchmarks.html', { 'benchmarks' : benches }, context_instance=RequestContext(request))

@login_required()
def compare(request):
	if request.method == 'POST': # If the form has been submitted...
		form = CompareForm(request.POST) # A form bound to the POST data
		if (form.is_valid()):
			# Process the data in form.cleaned_data
			b = form.cleaned_data['benchmarks']
			comparison, created = Comparison.objects.get_or_create(user=request.user, benchmarks=(",".join([str(bench.id) for bench in b])))
			return render_to_response('compare.html', { 'id' : comparison.id }, context_instance=RequestContext(request))
	else:
		return redirect(benchmarks.views.benchmarks)

def compare_detail(request, id):
	return render_to_response('compare.html', { 'id' : id }, context_instance=RequestContext(request))
	
@login_required()
def user_comparisons(request):
	c = get_list_or_404(Comparison, user=request.user.id)
	return render_to_response('user_compare.html', { 'comparisons' : c }, context_instance=RequestContext(request))
	
def user_comparison_delete(request, id):
	c = Comparison.objects.get(pk=id)
	c.delete()
	return redirect('/user/compare/')
	
def compare_model(request):
	if request.method == 'POST': # If the form has been submitted...
		form = CompareModelsForm(request.POST) # A form bound to the POST data
		if form.is_valid(): # All validation rules pass
			type = form.cleaned_data['type']
			return render_to_response('compare_models.html', { 'type' : type }, context_instance=RequestContext(request))
	else:
		form = CompareModelsForm() # An unbound form
		
	return render_to_response('compare_models_form.html', {
		'form': form, 
	}, context_instance=RequestContext(request))