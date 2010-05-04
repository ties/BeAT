from django.template import RequestContext
from beat.benchmarks.models import *
from beat.benchmarks.filter import *
from datetime import datetime
from django.db import connection,transaction
import json

DEFAULTSORT = 'id'
DEFAULTSORTORDER = 'ASC'
DEFAULTRESPERPAGE = 50
SORT_ID = 'id'
SORT_MODEL = 'model'
SORT_STATES = 'states'
SORT_RUNTIME = 'runtime'
SORT_MEMORY_RSS = 'memory_rss'
SORT_FINISHED = 'finished'
SORT_ASCENDING = 'ASC'
SORT_DESCENDING = 'DESC'

def getBenchmarks(request):
	print 'check'
	filters = {}
	if 'filters' in request.POST.keys():
		filters = convertfilters(json.loads(request.POST['filters']))
	
	print 'check'
	
	sort = DEFAULTSORT
	sortorder = DEFAULTSORTORDER
	
	print 'check'
	
	if 'sort' in request.POST.keys():
		jsonsort = json.loads(request.POST['sort'])
		sort = str(jsonsort['sort'])
		sortorder = str(jsonsort['sortorder'])
	
	print 'check'
	
	res = getResponse(Benchmark.objects.all(),filters,sort,sortorder)
	print res['tools']
	return res

def getResponse(qs,filters,sort,sortorder):
	print "variables; sort=%s, sortorder=%s" % (sort,sortorder)
	
	result = {}
	
	benchmarks = []
	algorithms = []
	options = []
	tools = []
	models = []
	
	algorithmdone = False
	optionsdone = False
	tooldone = False
	modeldone = False
	
	for k,f in filters.iteritems():
		print "Now starting filter row %i" % f.row
		
		#if f.type==MODEL:
			#models = getModels(qs)
			#modeldone = True
		if f.type==ALGORITHM:
			algorithms = getAlgorithms(qs)
			algorithmdone = True
		elif f.type==TOOL:
			tools = getTools(qs)
			tooldone = True
		elif f.type==OPTIONS:
			options = getOptions(qs)
			optionsdone = True
		
		qs = f.apply(qs)
	
	#getting remaining results
	#if modeldone==False:
		#models = getModels(qs)
	
	if algorithmdone==False:
		algorithms = getAlgorithms(qs)
	
	if tooldone==False:
		tools = getTools(qs)
	
	if optionsdone==False:
		options = getOptions(qs)
	
	print "sorting!"
	qs = sortQuerySet(qs,sort,sortorder)
	
	for benchmark in qs:
		benchmarks.append({
			'id': benchmark.id,
			'model': benchmark.model.name,
			'states': benchmark.states_count,
			'runtime': benchmark.total_time,
			'memory': benchmark.memory_RSS,
			'finished': benchmark.finished
		})
	
	result['benchmarks'] = benchmarks
	
	result['algorithms'] = algorithms
	result['options'] = options
	result['tools'] = tools
	#result['models'] = models
	
	print "result made!"
	return result

def getModels(qs):
	models = []
	for model in qs.values('model','model__name').order_by('model__name').distinct():
		models.append({'id':model['model'],'name':model['model__name']})
	return models

def getAlgorithms(qs):
	algorithms = []
	for algorithm in qs.values('algorithm','algorithm__name').order_by('algorithm__name').distinct():
		algorithms.append({'id':algorithm['algorithm'],'name':algorithm['algorithm__name']})
	return algorithms

def getTools(qs):
	tools = []
	for tool in qs.values('tool','tool__name','tool__version').order_by('tool__name','tool__version').distinct():
		tools.append({'id':tool['tool'],'name':tool['tool__name'],'version':tool['tool__version']})
	return tools

def getOptions(qs):
	q = str(qs.values_list('id',flat=True).query)
	cursor = connection.cursor()
	cursor.execute("SELECT * FROM `benchmarks_option` WHERE EXISTS (SELECT `id` FROM `benchmarks_optionvalue` WHERE `benchmarks_optionvalue`.`option_id`=`benchmarks_option`.`id` AND EXISTS (SELECT `id` FROM `benchmarks_benchmarkoptionvalue` WHERE `benchmarks_benchmarkoptionvalue`.`optionvalue_id`=`benchmarks_optionvalue`.`id` AND `benchmarks_benchmarkoptionvalue`.`benchmark_id` IN ("+q+")))")
	options = []
	for option in cursor:
		options.append({'id':option[0],'name':option[1],'takes_argument':option[2]})
	
	return options

def sortQuerySet(qs,sort,sortorder):
	s = ""
	if sort==SORT_ID:
		s='id'
	elif sort==SORT_MODEL:
		s='model__name'
	elif sort==SORT_STATES:
		s='states_count'
	elif sort==SORT_RUNTIME:
		s='total_time'
	elif sort==SORT_MEMORY_RSS:
		s='memory_RSS'
	elif sort==SORT_FINISHED:
		s='finished'
	
	if sortorder==SORT_DESCENDING:
		s = '-'+s
	print 'sort with: '+s
	qs = qs.order_by(s)
	return qs