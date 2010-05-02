from django.http import HttpResponse, HttpResponseRedirect
from django.contrib.auth.decorators import login_required
from django.template import RequestContext, loader
from django.shortcuts import render_to_response, redirect, get_list_or_404
import datetime
from filereader import FileReader
from beat.benchmarks.models import *
from forms import *
from django.core.paginator import Paginator, InvalidPage, EmptyPage

# MatPlotLib
import numpy as np

"""Page for batch job generation
"""
@login_required
def jobgen(request):
	#fetch tool/algorithms
	#t = Tool.objects.all()
	#a = Algorithm.objects.all()
	#fetch models
	#m = Model.objects.all()
	#display page
	form = JobGenForm()
	return render_to_response('jobgen.html', {'form':form}, context_instance=RequestContext(request))

"""Generate batch job
"""
@login_required
def jobgen_create(request):
	if request.method == 'POST': # If the form has been submitted...	
		print request.POST
		form = JobGenForm(request.POST) # A form bound to the POST data
		print "hai"
		if (form.is_valid()):
			print "valid"
			# Process the data in form.cleaned_data
			t = form.cleaned_data['tool']
			a = form.cleaned_data['algorithm']
			m = form.cleaned_data['models']
			from beat.jobs.jobs import *
			j = JobGenerator()
			jobs = []
			for x in m:
				jobs.append(j.pbsgen("name","1","memtime %s%s %s"%(t.name,a.name,x.name)))
			return render_to_response('jobgen_create.html', { 'job':jobs }, context_instance=RequestContext(request))
		else:
			print "invalid"
			return redirect('benchmarks.views.jobgen')
	else:
		return redirect('benchmarks.views.jobgen')



"""
Produces a scatterplot from a set of benchmarks.
TODO:
@param id Comparison id to retrieve a set of Benchmark id's from the db (currently takes the whole dataset - no id yet)
""" 
def scatterplot(request):
	# General library stuff
	from matplotlib.backends.backend_agg import FigureCanvasAgg as FigureCanvas
	from matplotlib.figure import Figure
	# Colorconverter to make red and blue dots in the plot
	from matplotlib.colors import ColorConverter
	cc=ColorConverter()

	import math
	fig=Figure(facecolor='w')
	
	# Make a subplot for the Elapsed Time data of a benchmark set
	ax=fig.add_subplot(211)
	
	# @TODO
	# Take the two data sets from the db and intersect on model id
	b1 = Benchmark.objects.filter(tool__name__exact='etf').filter(tool__version__exact='2')
	b2 = Benchmark.objects.filter(tool__name__exact='etf').filter(model__in=[b.model.pk for b in b1]).filter(tool__version__exact='3')
	b1 = b1.filter(model__in=[b.model.pk for b in b2])
	
	# Make new arrays with only the elapsed time
	t1 = [b.elapsed_time for b in b1]
	t2 = [b.elapsed_time for b in b2]
	
	# Color mask: if t[i] < t[2] --> blue dot in graph; else red dot
	mask = []
	for index in range(len(t1)):
		if t1[index] < t2[index]:
			mask.append(cc.to_rgb('blue'))
		else:
			mask.append(cc.to_rgb('red'))
	
	# Draw a linear function from .001 until the first power of 10 greater than max_value
	max_value_t = max(max(b1.values('elapsed_time')),max(b2.values('elapsed_time')))['elapsed_time']
	max_value_t = math.pow(10,math.ceil(math.log10(max_value_t)))
	ax.plot(np.arange(0,max_value_t,step=.001),np.arange(0,max_value_t,step=.001),'k-')
	
	# Plot data
	ax.scatter(t1, t2, s=10, color=mask, marker='o')
	
	# Axes mark-up
	ax.set_xscale('log')
	ax.set_yscale('log')
	ax.set_xlabel('lpo', color='red')
	ax.set_ylabel('nips', color='blue')
	ax.set_title('Runtime (s)', size='small')
	ax.set_axis_bgcolor('#eeeeee')
	ax.grid(True)
		
	# -------- Plotting memory data starts here in a new subplot ---------
	ax=fig.add_subplot(212)
	m1 = [b.memory_VSIZE for b in b1]
	m2 = [b.memory_VSIZE for b in b2]
	
	# Color mask again
	mask = []
	for index in range(len(t1)):
		if m1[index] < m2[index]:
			mask.append(cc.to_rgb('blue'))
		else:
			mask.append(cc.to_rgb('red'))
	
	# Plot linear function again
	max_value_m = max(max(b1.values('memory_VSIZE')),max(b2.values('memory_VSIZE')))['memory_VSIZE']
	max_value_m = math.pow(10,math.ceil(math.log10(max_value_m)))
	ax.plot(np.arange(0,max_value_m),np.arange(0,max_value_m),'k-')
	
	# Axes mark-up
	ax.set_xscale('log')
	ax.set_yscale('log')
	ax.set_xlabel('lpo', color='red')
	ax.set_ylabel('nips', color='blue')
	ax.set_axis_bgcolor('#eeeeee')
	ax.grid(True)
	
	# Plot data
	ax.scatter(m1,m2,s=10,color=mask,marker='o')
	ax.set_title('Memory VSIZE (kb)', size='small')
	
	# Output graph
	fig.set_size_inches(5,10)
	canvas = FigureCanvas(fig)
	response = HttpResponse(content_type='image/png')
	canvas.print_png(response)
	return response

"""
Old graph function to plot a histogram with benchmark data from db
"""
def simple(request, id):
	
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
	ax.bar(np.arange(numBench), states, width, align='center')
	ax.set_xticks(np.arange(benchmarks.count()))
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

"""
Output a graph for model comparison.
So each seperate model has one line; the data for this line is determined by benchmarks that are filtered from the db.
@param id ModelComparison ID from the database, used filter the benchmark data from the db.
"""
def graph_model(request, id):
	# General library stuff
	from matplotlib.backends.backend_agg import FigureCanvasAgg as FigureCanvas
	from matplotlib.lines import Line2D
	from matplotlib.figure import Figure
	
	# DB stuff
	from django.db.models import Count
	from beat.benchmarks.models import Model, ModelComparison
	
	# Take the ModelComparison from db and filter data
	comparison = ModelComparison.objects.get(pk=id)
	c_tool = comparison.tool
	c_algo = comparison.algorithm
	c_type = comparison.type
	c_option = comparison.optionvalue
	
	fig=Figure(facecolor='w')
	ax=fig.add_subplot(111)
	
	# Lists of colors, styles and markers to get a nice unique style for each line
	colors = ('b', 'g', 'r', 'c', 'm', 'y', 'k')
	styles = ['-', '--', ':']
	markers = ['+','o','x']

	# Plot data
	axisNum = 0 # Counts the number of lines (to produce a unique style for each line)
	
	modelNames = Model.objects.values('name').annotate(num_models=Count('name'))
	
	# Plot a line for each model
	for m in modelNames:
		axisNum += 1
		style = styles[axisNum % len(styles) ]
		color = colors[axisNum % len(colors) ]
		marker = markers[axisNum % len(markers) ]
		
		benchmarks = Benchmark.objects.filter(model__name__exact = m['name'])
		# Filter benchmarks based on the ModelComparison data
		benchmarks = benchmarks.filter(algorithm = c_algo).filter(tool = c_tool)
		
		# Filter options if specified
		if c_option is not None:
			benchmarks = benchmarks.filter(optionvalue=c_option)
		
		# Static data types to plot in the graph
		types = {
			'transitions': [b.transition_count for b in benchmarks],
			'states': [b.states_count for b in benchmarks],
			'vsize': [b.memory_VSIZE for b in benchmarks],
			'rss': [b.memory_RSS for b in benchmarks],
		}[c_type] # c_type: datatype from ModelComparison object
		
		# Plot data
		lines = ax.plot(
			[b.model.version for b in benchmarks], 
			types, 
			marker + style + color,
			label = m['name'])

	#Mark-up
	title = '' + c_type + ' (' + c_tool.name + ', ' + c_algo.name
	if c_option is not None:
		title = title + ' [' + c_option + ']'
	title = title + ')'
	
	ax.set_title(title)
	leg = ax.legend()
	for t in leg.get_texts():
		t.set_fontsize('small')
	ax.set_ylabel(c_type)
	ax.set_xlabel('version')
	
	# Output
	canvas = FigureCanvas(fig)
	#fig.savefig('benchmark.pdf')
	response = HttpResponse(content_type='image/png')
	canvas.print_png(response)
	return response

	#@login_required(redirect_field_name='next')
def index(request):
	return render_to_response('base.html', context_instance=RequestContext(request))


"""
Show the list of benchmarks with pagination
"""
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

"""
CompareForm handler.
Take all selected benchmarks and redirect to compare page or show empty form
"""	
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

"""
Shows the comparison graph that is saved by a user.
@param id Comparison id if model=False; else ModelComparison id
"""		
def compare_detail(request, id, model=False):
	if model:
		return render_to_response('compare_models.html', { 'id' : id }, context_instance=RequestContext(request))
	else:
		return render_to_response('compare.html', { 'id' : id }, context_instance=RequestContext(request))

"""
Shows a list of all Comparisons and ModelComparisons
"""		
@login_required()
def user_comparisons(request):
	b_comparisons = list(Comparison.objects.filter(user=request.user.id))
	m_comparisons = list(ModelComparison.objects.filter(user=request.user.id))
	return render_to_response('user_compare.html', { 'b_comparisons' : b_comparisons, 'm_comparisons' : m_comparisons }, context_instance=RequestContext(request))

"""
Deletes a Comparison if model=False; else deletes a ModelComparison
@param id The id of the (Model)Comparison that needs to be deleted
@TODO user authorisation
"""	
def user_comparison_delete(request, id, model=False):
	if model:
		c = ModelComparison.objects.get(pk=id)
	else:
		c = Comparison.objects.get(pk=id)
	c.delete()
	return redirect('/user/compare/')

"""
ModelCompareForm handler
"""	
def compare_model(request):
	print Tool.objects.all()
	return render_to_response('compare_models_form.html', { 'tools' : Tool.objects.all() }, context_instance=RequestContext(request))
	"""
	if request.method == 'POST': # If the form has been submitted...
		form = CompareModelsForm(request.POST) # A form bound to the POST data
		if form.is_valid(): # All validation rules pass
			comparison, created = ModelComparison.objects.get_or_create(
				user = request.user, 
				algorithm = form.cleaned_data['algorithm'],
				tool = form.cleaned_data['tool'],
				optionvalue = form.cleaned_data['option'],
				type = form.cleaned_data['type']
			)
			#return render_to_response('compare_models.html', { 'id' : comparison.id }, context_instance=RequestContext(request))
			return redirect('detail_model', id=comparison.id)
	else:
		form = CompareModelsForm() # An unbound form
	
	return render_to_response('compare_models_form.html', {
		'form': form, 
	}, context_instance=RequestContext(request))
	"""
