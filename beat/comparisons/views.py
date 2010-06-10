from django.http import HttpResponse, HttpResponseForbidden
from django.shortcuts import render_to_response, redirect, get_object_or_404, get_list_or_404
from django.contrib.auth.decorators import login_required
from django.template import RequestContext
from forms import *
from beat.tools import graph
from django.views.decorators.cache import cache_page
from decimal import Decimal

# MatPlotLib
import numpy as np

"""
Produces a scatterplot from a set of benchmarks.
TODO:
@param id Comparison id to retrieve a set of Benchmark id's from the db (currently takes the whole dataset - no id yet)
""" 
@cache_page(60 * 15)
def scatterplot(request, id, format='png'):
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
	c = get_object_or_404(Comparison,id=id)
	at_a = c.algorithm_tool_a
	at_b = c.algorithm_tool_b
	b1 = Benchmark.objects.filter(algorithm_tool=at_a)
	b2 = Benchmark.objects.filter(algorithm_tool=at_b)
	b1 = b1.filter(model__in=[b.model.pk for b in b2])
	
	# Make new arrays with only the elapsed time
	t1 = [(float(b.elapsed_time)) for b in b1]
	t2 = [(float(b.elapsed_time)) for b in b2]
	
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
	ax.set_xlabel(str(at_a), color='red')
	ax.set_ylabel(str(at_b), color='blue')
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
	ax.set_xlabel(str(at_a), color='red')
	ax.set_ylabel(str(at_b), color='blue')
	ax.set_axis_bgcolor('#eeeeee')
	ax.grid(True)
	
	# Plot data
	ax.scatter(m1,m2,s=10,color=mask,marker='o')
	ax.set_title('Memory VSIZE (kb)', size='small')
	
	# Output graph
	fig.set_size_inches(5,10)
	canvas = FigureCanvas(fig)
	response = graph.export(canvas, c.name, format)
	return response

"""
Output a graph for model comparison.
So each seperate model has one line; the data for this line is determined by benchmarks that are filtered from the db.
@param id ModelComparison ID from the database, used filter the benchmark data from the db.
"""
@cache_page(60 * 15)
def graph_model(request, id, format='png'):
	# General library stuff
	from matplotlib.backends.backend_agg import FigureCanvasAgg as FigureCanvas
	from matplotlib.lines import Line2D
	from matplotlib.figure import Figure
	import matplotlib
	import matplotlib.pyplot as plt
	
	# DB stuff
	from django.db.models import Count
	
	# Take the ModelComparison from db and filter data
	comparison = ModelComparison.objects.get(pk=id)
	c_tool = comparison.tool
	c_algo = comparison.algorithm
	c_type = comparison.type
	c_option = comparison.optionvalue
	
	fig=Figure(facecolor='w')
	#fig = plt.figure(facecolor='w')
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
		benchmarks = benchmarks.filter(algorithm_tool__algorithm = c_algo, algorithm_tool__tool = c_tool).order_by('algorithm_tool__date')
		
		if (len(benchmarks) != 0):
			# Filter options if specified
			if c_option is not None:
				benchmarks = benchmarks.filter(optionvalue=c_option)
			
			# Static data types to plot in the graph
			types = []
			if (c_type == ModelComparison.TRANSITIONS):
				types = [b.transition_count for b in benchmarks]
			elif (c_type == ModelComparison.STATES):
				types = [b.states_count for b in benchmarks]
			elif (c_type == ModelComparison.VSIZE):
				types = [b.memory_VSIZE for b in benchmarks]
			elif (c_type == ModelComparison.RSS):
				types = [b.memory_RSS for b in benchmarks]
			elif (c_type == ModelComparison.ELAPSED_TIME):
				types = [b.elapsed_time for b in benchmarks]
			elif (c_type == ModelComparison.TOTAL_TIME):
				types = [b.total_time for b in benchmarks]
			
			# Plot data
			lines = ax.plot(
				[b.algorithm_tool.date for b in benchmarks], 
				types, 
				marker + style + color,
				label = m['name'])

	#Mark-up
	title = c_tool.name + c_algo.name
	if c_option is not None:
		title = title + ' [' + str(c_option) + ']'
	
	ax.set_title(title)
	leg = ax.legend(fancybox=True, loc='upper left',bbox_to_anchor = (1,1.15), markerscale=5)
	for t in leg.get_texts():
		t.set_fontsize('xx-small')
	
	y_label = c_type
	for l in ModelComparison.DATA_TYPES:
		a,b = l
		if a == c_type:
			y_label = b
	ax.set_ylabel(y_label)
	ax.set_xlabel('Revision date')
	fig.autofmt_xdate()
	
	fig.subplots_adjust(right=0.7)

	# Output
	canvas = FigureCanvas(fig)
	#fig.savefig('benchmark.pdf')
	response = graph.export(canvas, comparison.name, format)
	return response

@login_required()
def export_graph(request, id, model=False):
	if request.method == 'POST': # If the form has been submitted...
		form = ExportGraphForm(request.POST) # A form bound to the POST data
		if form.is_valid(): # All validation rules pass
			format = form.cleaned_data['format']
			if model:
				return graph_model(request, id, format)
			else:
				return scatterplot(request, id, format)
	else:
		form = ExportGraphForm() # An unbound form

	return render_to_response('comparisons/compare.html', {
		'comparison' : Comparison.objects.get(pk=id), 'form': form,
	}, context_instance=RequestContext(request))
	
"""
Deletes a Comparison if model=False; else deletes a ModelComparison
@param id The id of the (Model)Comparison that needs to be deleted
@TODO user authorisation
"""	
@login_required()
def comparison_delete(request, id, model=False):
	if model:
		c = ModelComparison.objects.get(pk=id)
	else:
		c = Comparison.objects.get(pk=id)
	c.delete()
	return redirect('/user/compare/')

"""
Shows the comparison graph that is saved by a user.
@param id Comparison id if model=False; else ModelComparison id
"""		
def compare_detail(request, id, model=False):
	# Check if the comparison is a ModelComparison or Comparison
	# Then retrieve the correct object and make a response object with it
	if model:
		c = get_object_or_404(ModelComparison,pk=id)
		
		#models = Model.objects.values('id').annotate(num_models=Count('name'))
		#benches = Benchmark.objects.filter(algorithm_tool__tool=c.tool, algorithm_tool__algorithm = c.algorithm).filter(model__in=[m['id'] for m in models])
		#models = Model.objects.filter(id__in=[b.model.id for b in benches])
		benches = Benchmark.objects.filter(algorithm_tool__tool=c.tool, algorithm_tool__algorithm = c.algorithm)
		
		form = ExportGraphForm()
		response = render_to_response('comparisons/compare_models.html', { 'comparison' : c, 'form' : form,  'benches' : benches}, context_instance=RequestContext(request))
	else:
		c = get_object_or_404(Comparison,pk=id)
		
		at_a = c.algorithm_tool_a
		at_b = c.algorithm_tool_b
		b1 = Benchmark.objects.filter(algorithm_tool=at_a)
		b2 = Benchmark.objects.filter(algorithm_tool=at_b)
		b1 = b1.filter(model__in=[b.model.pk for b in b2])

		# Model should be consistent for b1 and b2, so doesn't matter which you pick
		model = [b.model.name for b in b1]
		
		# Memory
		m1 = [b.memory_VSIZE for b in b1]
		m2 = [b.memory_VSIZE for b in b2]
		
		# Make new arrays with only the elapsed time
		t1 = [(float(b.elapsed_time)) for b in b1]
		t2 = [(float(b.elapsed_time)) for b in b2]
		
		list = zip(model,m1,m2,t1,t2)
		
		form = ExportGraphForm()
		response = render_to_response('comparisons/compare.html', { 'comparison' : c, 'form' : form, 'list' : list }, context_instance=RequestContext(request))
	
	# Check if the user has rights to see the results:
	#	- Either the user provided a correct query string like ?auth=<hash>
	#	- Or the user is the owner of this comparison
	if ((request.GET.__contains__('auth') and request.GET['auth'] == c.hash) or c.user == request.user):
		return response	
	
	# Otherwise, forbidden to see this page
	else:
		return HttpResponseForbidden('<h1>You are not authorised to view this page.</h1>')

"""
ModelCompareForm handler
"""	
@login_required()
def compare_model(request):
	"""
	return render_to_response('compare_models_form.html', { 'tools' : Tool.objects.all() }, context_instance=RequestContext(request))
	"""
	if request.method == 'POST': # If the form has been submitted...
		form = CompareModelsForm(request.POST) # A form bound to the POST data
		if form.is_valid(): # All validation rules pass
			c, created = ModelComparison.objects.get_or_create(
				user = request.user, 
				algorithm = form.cleaned_data['algorithm'],
				tool = form.cleaned_data['tool'],
				optionvalue = form.cleaned_data['option'],
				type = form.cleaned_data['type'],
				name = form.cleaned_data['name']
			)
			
			c.hash = c.getHash()
			if (c.name == ''): 
				c.name = str(c.id)
			c.save()
			
			#return render_to_response('compare_models.html', { 'id' : comparison.id }, context_instance=RequestContext(request))
			return redirect('detail_model', id=c.id)
	else:
		form = CompareModelsForm() # An unbound form
	
	return render_to_response('comparisons/compare_models_form.html', {
		'form': form, 
	}, context_instance=RequestContext(request))
	
	
@login_required()
def compare_scatterplot(request):
	if request.method == 'POST': # If the form has been submitted...
		form = CompareScatterplotForm(request.POST) # A form bound to the POST data
		if form.is_valid(): # All validation rules pass
			id_a = form.cleaned_data['a_algorithmtool']
			id_b = form.cleaned_data['b_algorithmtool']
			
			c, created = Comparison.objects.get_or_create(
				user = request.user, 
				algorithm_tool_a = id_a,
				algorithm_tool_b = id_b,
				name = form.cleaned_data['name']
			)
			
			c.hash = c.getHash()
			if (c.name == ''): 
				c.name = str(c.id)
			c.save()
			return redirect('detail_benchmark', id=c.id)
	else:
		form = CompareScatterplotForm() # An unbound form
	return render_to_response('comparisons/compare_benchmarks_form.html', {
		'form': form,
	}, context_instance=RequestContext(request))

	
"""
DEPRECATED
Old graph function to plot a histogram with benchmark data from db
"""
def simple(request, id, format='png'):
	
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
	canvas = FigureCanvas(fig)
	
	#fig.set_size_inches(4,8)
	title = benchmark_IDs.name
	response = graph.export(canvas, title, format)
	return response
