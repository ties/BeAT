from django.template import RequestContext
from beat.benchmarks.models import *
from beat.benchmarks.filter import *
from datetime import datetime
from django.db import connection,transaction
import json

DEFAULTSORT = 'id'
DEFAULTSORTORDER = 'ASC'
DEFAULTRESPERPAGE = 50
SORTS = {'model':'model__name','id':'id','states':'states_count','runtime':'total_time','memory_rss':'memory_RSS','finished':'finished'}
SORT_ASCENDING = 'ASC'
SORT_DESCENDING = 'DESC'
DEFAULTCOLUMNS = {}

def getBenchmarks(request):
	print 'check'
	filters = {}
	if 'filters' in request.POST.keys():
		filters = convertfilters(json.loads(request.POST['filters']))
	
	print 'check'
	
	sort = DEFAULTSORT
	sortorder = DEFAULTSORTORDER
	columns = DEFAULTCOLUMNS
	
	if 'sort' in request.POST.keys():
		jsonsort = json.loads(request.POST['sort'])
		sort = str(jsonsort['sort'])
		sortorder = str(jsonsort['sortorder'])
	
	if 'columns' in request.POST.keys():
		columns = json.loads(request.POST['columns'])
		print '-------------cols'
		print columns
	print 'check'
	
	res = getResponse(Benchmark.objects.all(),filters,sort,sortorder,columns)
	
	return res

def getResponse(qs,filters,sort,sortorder,columns):
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
		
		if f.type==MODEL:
			models = getModels(qs)
			modeldone = True
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
	if modeldone==False:
		models = getModels(qs)
	
	if algorithmdone==False:
		algorithms = getAlgorithms(qs)
	
	if tooldone==False:
		tools = getTools(qs)
	
	if optionsdone==False:
		options = getOptions(qs)
	
	possiblecolumns = getColumns(qs)
	
	print "sorting!"
	qs = sortQuerySet(qs,sort,sortorder)
	
	for benchmark in qs:
		dict = {'id':benchmark.id}
		
		benchmarks.append({
			'id': benchmark.id,
			'model': benchmark.model.name,
			'states': benchmark.states_count,
			'runtime': benchmark.total_time,
			'memory': benchmark.memory_RSS,
			'finished': benchmark.finished
		})
	
	result['benchmarks'] = benchmarks
	result['columns'] = possiblecolumns
	result['algorithms'] = algorithms
	result['options'] = options
	result['tools'] = tools
	result['models'] = models
	
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
	cursor.execute("SELECT `id`,`name`,`takes_argument` FROM `benchmarks_option` \
		WHERE EXISTS (\
			SELECT `id` FROM `benchmarks_optionvalue` \
				WHERE `benchmarks_optionvalue`.`option_id`=`benchmarks_option`.`id` AND \
				EXISTS \
				(SELECT `id` FROM `benchmarks_benchmarkoptionvalue` \
					WHERE `benchmarks_benchmarkoptionvalue`.`optionvalue_id`=`benchmarks_optionvalue`.`id` AND \
					`benchmarks_benchmarkoptionvalue`.`benchmark_id` IN \
					("+q+")))")
	options = []
	for option in cursor:
		options.append({'id':option[0],'name':option[1],'takes_argument':option[2]})
	
	return options

def sortQuerySet(qs,sort,sortorder):
	s = ""
	if sort in SORTS.keys():
		s = SORTS[sort]
	else:
		s = sort
		
	if sortorder==SORT_DESCENDING:
		s = '-'+s
	print 'sort with: '+s
	qs = qs.order_by(s)
	return qs

def getColumns(qs):
	result = []
	result.append({'header':'Model','value':'model__name'})
	result.append({'header':'States','value':'states_count'})
	result.append({'header':'Runtime','value':'total_time'})
	result.append({'header':'Memory (RSS)','value':'memory_RSS'})
	result.append({'header':'Memory (VSIZE)','value':'memory_VSIZE'})
	result.append({'header':'Finished','value':'finished'})
	return result