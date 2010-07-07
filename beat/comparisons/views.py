from django.http import HttpResponse, HttpResponseForbidden
from django.shortcuts import render_to_response, redirect, get_object_or_404, get_list_or_404
from django.contrib.auth.decorators import login_required
from django.template import RequestContext
from forms import *
from beat.tools import graph, intersect
from django.views.decorators.cache import cache_page
from decimal import Decimal
#json export voor model instanties
#zoals: resultsjson = serializers.serialize("json", results) maar dan met model instanties ipv array.
from django.core import serializers
#json
import json
from benchmarks.ajax_execute import BenchmarkJSON

# MatPlotLib
import numpy as np

def benchFind(b, ovs):
	"""
	Finds the benchmarks from b with the optionvalues as specified in ovs
	@param b Benchmark object
	@param ovs A list of OptionValue ids.
	"""
	
	res = []
	for benchmark in b:
		opts = [o.id for o in benchmark.optionvalue.all()]
		if (set(opts) == set(ovs)):
			res.append(benchmark)
	return res

def printlabel(at, ov):
	"""
	Method to produce a label for the axes of a graph, print the used AlgorithmTool and all OptionValues.
	@param at AlgorithmTool object
	@param ov OptionValue objects
	"""
	
	return str(at) + ' ' + str(','.join([str(o) for o in ov.all()]))

@cache_page(60 * 15)
def scatterplot(request, id, format='png'):
	"""
	Produces a scatterplot from a set of benchmarks.
	Filters two sets of Benchmark objects based on the Comparison object and takes total_time and memory_VSIZE values from them.
	@param id The identifier of the Comparison object.
	@param format The export format for the graph, png is default. Choices: ['png','pdf','ps','eps','svg']
	""" 
	
	# General library stuff
	from matplotlib.backends.backend_agg import FigureCanvasAgg as FigureCanvas
	from matplotlib.figure import Figure
	
	# Colorconverter to make red and blue dots in the plot
	from matplotlib.colors import ColorConverter
	cc=ColorConverter()

	import math
	fig=Figure(facecolor='w')
	
	# Make a subplot for the Total Time data of a benchmark set
	ax=fig.add_subplot(211)
	
	# Fetch two benchmarks sets from DB
	c = get_object_or_404(Comparison,id=id)
	at_a = c.algorithm_tool_a
	at_b = c.algorithm_tool_b
	
	# First filter AlgorithmTool
	b1 = Benchmark.objects.filter(algorithm_tool=at_a)
	b2 = Benchmark.objects.filter(algorithm_tool=at_b)
	
	# Only keep Benchmark that have overlapping Models.
	b1 = b1.filter(model__in=[b.model.pk for b in b2])
	b2 = b2.filter(model__in=[b.model.pk for b in b1])
	
	# Filter the selected options from Benchmark sets.
	b1 = benchFind(b1,[o.id for o in c.optionvalue_a.all()])
	b2 = benchFind(b2,[o.id for o in c.optionvalue_b.all()])
	
	# Calculate the average values for Models that are double in the set.
	model_list = []
	for b in b2:
		if not b.model.pk in model_list:
			model_list.append(b.model.pk)
	t1avg = []
	t2avg = []
	m1avg = []
	m2avg = []
	for model in model_list:
		tmp1 = []
		for bench in b1:
			if bench.model.pk == model:
				tmp1.append(bench)
		tmp2 = []
		for bench in b2:
			if bench.model.pk == model:
				tmp2.append(bench)
		if tmp1 and tmp2:
			x=[(float(b.total_time)) for b in tmp1]
			t1avg.append(float(sum(x))/len(x))
			x=[(float(b.total_time)) for b in tmp2]
			t2avg.append(float(sum(x))/len(x))
			x=[(float(b.memory_VSIZE)) for b in tmp1]
			m1avg.append(float(sum(x))/len(x))
			x=[(float(b.memory_VSIZE)) for b in tmp2]
			m2avg.append(float(sum(x))/len(x))

	# Check for empty set
	if len(t1avg) != 0:
		
		# Use the averages, in case any doubles occur
		t1 = t1avg
		t2 = t2avg
		
		# Color mask: if t[1] < t[2] --> red dot in graph; else blue dot
		mask = []
		for index in range(len(t1)):
			if t1[index] < t2[index]:
				mask.append(cc.to_rgb('red'))
			else:
				mask.append(cc.to_rgb('blue'))
		
		# Draw a linear function from .001 until the first power of 10 greater than max_value
		max_value_t = max(max(t1avg),max(t2avg))
		max_value_t = math.pow(10,math.ceil(math.log10(max_value_t)))
		ax.plot(np.arange(0,max_value_t,step=.001),np.arange(0,max_value_t,step=.001),'k-')
		
		# Plot data
		ax.scatter(t1, t2, s=10, color=mask, marker='o')
		
		# Axes mark-up
		ax.set_xscale('log')
		ax.set_yscale('log')
		ax.set_xlabel(printlabel(at_a,c.optionvalue_a), color='red')
		ax.set_ylabel(printlabel(at_b,c.optionvalue_b), color='blue')
		ax.set_title('Runtime (s)', size='small')
		ax.grid(True)
			
		# -------- Plotting memory data starts here in a new subplot ---------
		ax=fig.add_subplot(212)
		
		# Average memory values.
		m1 = m1avg
		m2 = m2avg
		
		# Color mask again
		mask = []
		for index in range(len(t1)):
			if m1[index] < m2[index]:
				mask.append(cc.to_rgb('blue'))
			else:
				mask.append(cc.to_rgb('red'))
		
		# Plot linear function again
		max_value_m = max(max(m1),max(m2))
		max_value_m = math.pow(10,math.ceil(math.log10(max_value_m)))
		ax.plot(np.arange(0,max_value_m),np.arange(0,max_value_m),'k-')
		
		# Axes mark-up
		ax.set_xscale('log')
		ax.set_yscale('log')
		ax.set_xlabel(printlabel(at_a,c.optionvalue_a), color='red')
		ax.set_ylabel(printlabel(at_b,c.optionvalue_b), color='blue')
		ax.grid(True)
		
		# Plot data
		ax.scatter(m1,m2,s=10,color=mask,marker='o')
		ax.set_title('Memory VSIZE (kb)', size='small')
	# Result set is empty
	else: 
		ax=fig.add_subplot(211)
		ax.set_title('Runtime (s)', size='small')
		ax.text(0.3,0.5,"Empty result set.") 
		ax=fig.add_subplot(212)
		ax.set_title('Memory VSIZE (kb)', size='small')
		ax.text(0.3,0.5,"Empty result set.")
	
	# Output graph
	fig.set_size_inches(5,10)
	canvas = FigureCanvas(fig)
	response = graph.export(canvas, c.name, format)
	return response
	

@cache_page(60 * 15)
def graph_model(request, id, format='png'):
	"""
	Output a graph for model comparison.
	Each seperate Model has one line; the data for this line is determined by Benchmarks that are filtered from the db.
	@param id ModelComparison ID from the database, used to filter the Benchmark data from the db.
	@param format The export format for the graph. Choices: ['png','pdf','ps','eps','svg']
	"""
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
		benchmarks = benchFind(benchmarks,[o.id for o in c_option.all()])
		
		if (len(benchmarks) != 0):
			
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

	# Mark-up
	title = c_tool.name + c_algo.name
	if c_option.all():
		options = [str(o) for o in c_option.all()]
		title = title + ' [' + ','.join(options) + ']'
	ax.set_title(title)
	
	# Print legend for lines in the graph.
	leg = ax.legend(fancybox=True, loc='upper left',bbox_to_anchor = (1,1.15), markerscale=5)
	if leg:
		for t in leg.get_texts():
			t.set_fontsize('xx-small')
		
	# Print labels for the axes.
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
	response = graph.export(canvas, comparison.name, format)
	return response

	
@login_required()
def export_graph(request, id, model=False):
	"""
	Method that handles clicking of the export graph button. It uses the ExportGraphForm that is defined in forms.py.
	The format is taken from the POSTed form and used in the method to produce a graph.
	@param id The id of the ModelComparison or Comparison object. This ID is taken from the URL.
	@param model Boolean value to inidicate whether it is a ModelComparison or Comparison object being exported.
	"""
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
	
	
@login_required()
def comparison_delete(request, id, model=False):
	"""
	Deletes a Comparison if model=False; else deletes a ModelComparison
	@param id The id of the (Model)Comparison that needs to be deleted
	@param model Boolean value to inidicate whether it is a ModelComparison or Comparison object being deleted.
	"""
	if model:
		c = ModelComparison.objects.get(pk=id)
	else:
		c = Comparison.objects.get(pk=id)
	
	# Check if the user is authorized to delete the object
	if c.user == request.user:
		c.delete()
		return redirect('/user/compare/')
	else:
		return HttpResponseForbidden('<h1>You are not authorized to view this page.</h1>')

def compare_detail(request, id, model=False):
	"""
	Shows the comparison graph that is saved by a user.
	@param id Comparison object id
	@param model Boolean value to inidicate whether it is a ModelComparison or Comparison object being viewed.
	"""
	
	# Check if the comparison is a ModelComparison or Comparison
	# Then retrieve the correct object and make a response object with it
	if model:
		# Find the ModelComparison or give a 404 error.
		c = get_object_or_404(ModelComparison,pk=id)
		
		# Filter selected OptionValues.
		benchesNoOptionFilter = Benchmark.objects.filter(algorithm_tool__tool=c.tool, algorithm_tool__algorithm = c.algorithm).order_by('model__name')
		benches = benchFind(benchesNoOptionFilter,[o.id for o in c.optionvalue.all()])
		
		# Filter the Model names.
		models = Model.objects.filter(id__in=[b.model.id for b in benches])

		# JSON serialization for flot graph.
		benchjson = serializers.serialize("json", benches)		
		modeljson = serializers.serialize("json", models)
		
		# Empty export form, so the user can choose an export format.
		form = ExportGraphForm()
		
		response = render_to_response('comparisons/compare_models.html', { 'comparison' : c, 'form' : form, 'benches' : benches, 'benchjson' : benchjson, 'modeljson' : modeljson}, context_instance=RequestContext(request))
	else:
		# Get the Comparison object or 404.
		c = get_object_or_404(Comparison,pk=id)
		
		# Filter the AlgorithmTool.
		at_a = c.algorithm_tool_a
		at_b = c.algorithm_tool_b
		b1 = Benchmark.objects.filter(algorithm_tool=at_a)
		b2 = Benchmark.objects.filter(algorithm_tool=at_b)
		
		# Filter on Models.
		b1 = b1.filter(model__in=[b.model.pk for b in b2])
		b2 = b2.filter(model__in=[b.model.pk for b in b1])
		
		# Filter on OptionValues.
		b1 = benchFind(b1,[o.id for o in c.optionvalue_a.all()])
		b2 = benchFind(b2,[o.id for o in c.optionvalue_b.all()])

		# Model should be consistent for b1 and b2, so doesn't matter which you pick.
		model = [b.model.name for b in b1]
		
		# Get memory values from Benchmark sets.
		m1 = [b.memory_VSIZE for b in b1]
		m2 = [b.memory_VSIZE for b in b2]
		
		# Make new arrays with only the elapsed time
		t1 = [(float(b.total_time)) for b in b1]
		t2 = [(float(b.total_time)) for b in b2]
		
		list = zip(model,t1,t2,m1,m2)
		
		#less then cute.
		from StringIO import StringIO
		io = StringIO()
		json.dumps(list)
		scatterjson = io.getvalue()
		
		form = ExportGraphForm()
		response = render_to_response('comparisons/compare.html', { 'comparison' : c, 'form' : form, 'list' : list, 'scatterdata' : scatterjson }, context_instance=RequestContext(request))
	
	# Check if the user has rights to see the results:
	#	- Either the user provided a correct query string like ?auth=<hash>
	#	- Or the user is the owner of this comparison
	if ((request.GET.__contains__('auth') and request.GET['auth'] == c.hash) or c.user == request.user):
		return response	
	
	# Otherwise, forbidden to see this page
	else:
		return HttpResponseForbidden('<h1>You are not authorized to view this page.</h1>')

	
@login_required()
def compare_model(request):
	"""
	CompareModelsForm handler. Creates a ModelComparison object if the form is valid and returns the graph.
	"""
	if request.method == 'POST': # If the form has been submitted...
		form = CompareModelsForm(request.POST) # A form bound to the POST data
		if form.is_valid(): # All validation rules pass
			
			# Create a ModelComparison object with posted form data.
			c = ModelComparison.objects.create(
				user = request.user, 
				algorithm = form.cleaned_data['algorithm'],
				tool = form.cleaned_data['tool'],
				type = form.cleaned_data['type'],
				name = form.cleaned_data['name']
			)
			
			# Add Many-To-Many relations for the OptionValues.
			for o in OptionValue.objects.filter(id__in=form.cleaned_data['option']):
				c.optionvalue.add(o)
			
			# Fix the hash and name.
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
	"""
	CompareScatterplotForm handler. Creates a Comparison object if the form is valid and returns the graph.
	"""
	if request.method == 'POST': # If the form has been submitted...
		form = CompareScatterplotForm(request.POST) # A form bound to the POST data
		if form.is_valid(): # All validation rules pass
			id_a = form.cleaned_data['a_algorithmtool']
			id_b = form.cleaned_data['b_algorithmtool']
			
			# Create a Comparison object with posted form data.
			c = Comparison.objects.create(
				user = request.user, 
				algorithm_tool_a = id_a,
				algorithm_tool_b = id_b,
				name = form.cleaned_data['name']
			)
			
			# Add Many-To-Many relations for the OptionValues.
			for o_a in OptionValue.objects.filter(id__in=form.cleaned_data['a_options']):
				c.optionvalue_a.add(o_a)
			for o_b in OptionValue.objects.filter(id__in=form.cleaned_data['b_options']):
				c.optionvalue_b.add(o_b)
			
			# Add many-to-many fields for 
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
