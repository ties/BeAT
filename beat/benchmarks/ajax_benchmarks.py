from django.template import RequestContext
from beat.benchmarks.models import *
from beat.benchmarks.filter import *
from datetime import datetime
from django.db import connection,transaction
import json

DEFAULTSORT = {'sort':'id','sortorder':'ASC'}
SORTS = {'model':'model__name','id':'id','states':'states_count','runtime':'total_time','memory_rss':'memory_RSS','finished':'finished'}
SORT_ASCENDING = 'ASC'
SORT_DESCENDING = 'DESC'
DEFAULTCOLUMNS = {}
DEFAULTPAGING = {'page':0,'resperpage':200}

DEFAULTDATA = {'filters':[],'sort':DEFAULTSORT,'columns':DEFAULTCOLUMNS,'paging':DEFAULTPAGING}

def getBenchmarks(request):
	data = DEFAULTDATA
	if 'data' in request.POST.keys():
		data = json.loads(request.POST['data'])
		data['filters'] = convertfilters(data['filters'])
		print data['filters']
		print data['sort']
		print data['columns']
		print data['paging']
	"""
	print 'check'
	filters = {}
	if 'filters' in request.POST.keys():
		filters = convertfilters(json.loads(request.POST['filters']))
	
	print 'check'
	
	sort = "id"
	sortorder = "ASC"
	columns = DEFAULTCOLUMNS
	paging = DEFAULTPAGING
	
	if 'sort' in request.POST.keys():
		jsonsort = json.loads(request.POST['sort'])
		sort = str(jsonsort['sort'])
		sortorder = str(jsonsort['sortorder'])
	
	if 'columns' in request.POST.keys():
		columns = json.loads(request.POST['columns'])
		print '-------------cols'
		print columns
	
	if 'paging' in request.POST.keys():
		paging = json.loads(request.POST['paging'])
	
	print '---------------paging!'
	print paging
	"""
	
	res = getResponse(Benchmark.objects.all(),data)
	
	return res

def getResponse(qs,data):
	result = {}
	
	benchmarks = []
	algorithms = []
	options = []
	tools = []
	models = []
	benchmark_ids = []
	
	algorithmdone = False
	optionsdone = False
	tooldone = False
	modeldone = False
	
	for k,f in data['filters'].iteritems():
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
	
	print "Done applying filters"
	#getting remaining results
	if modeldone==False:
		models = getModels(qs)
	
	if algorithmdone==False:
		algorithms = getAlgorithms(qs)
	
	if tooldone==False:
		tools = getTools(qs)
	
	if optionsdone==False:
		options = getOptions(qs)
	
	benchmark_ids = list(qs.values_list('id',flat=True))
	print "Done getting possible models, algorithms, tools and options"
	
	extracolumns = getColumns(qs)
	
	print "sorting!"
	qs = sortQuerySet(qs,data['sort'])
	
	page = data['paging']['page']
	resperpage = data['paging']['resperpage']
	
	result['benchmarks'] = list(qs.values('id','model__name','states_count','total_time','memory_RSS','finished')[page*resperpage : (page+1)*resperpage])
	result['columns'] = extracolumns
	result['algorithms'] = algorithms
	result['options'] = options
	result['tools'] = tools
	result['models'] = models
	result['benchmark_ids'] = benchmark_ids
	
	print "result made!"
	return result

def getModels(qs):
	models = []
	for model in qs.values('model','model__name').order_by('model__name').distinct():
		models.append({'id':model['model'],'name':model['model__name']})
	return models

def getAlgorithms(qs):
	#return list(qs.values('algorithm_tool__algorithm','algorithm_tool__algorithm__name').order_by('algorithm_tool__algorithm__name').distinct())
	algorithms = []
	for algorithm in qs.values('algorithm_tool__algorithm','algorithm_tool__algorithm__name').order_by('algorithm_tool__algorithm__name').distinct():
		algorithms.append({'id':algorithm['algorithm_tool__algorithm'],'name':algorithm['algorithm_tool__algorithm__name']})
	print "Algorithms:"
	print algorithms
	return algorithms

def getTools(qs):
	tools = []
	for tool in qs.values('tool','tool__name').order_by('tool__name').distinct():
		tools.append({'id':tool['tool'],'name':tool['tool__name']})
	print "Tools:"
	print tools
	return tools

def getOptions(qs):
	print "check"
	q = str(qs.values_list('id').query)
	#This is needed for sqlite3, which does not support the keywords False and True in queries
	q = q.replace(' False ',' 0 ')
	q = q.replace(' True ',' 1 ')
	print "check"
	print q
	cursor = connection.cursor()
	print "check"
	query = "SELECT `id`,`name`,`takes_argument` FROM `benchmarks_option` WHERE EXISTS (SELECT `id` FROM `benchmarks_optionvalue` WHERE `benchmarks_optionvalue`.`option_id`=`benchmarks_option`.`id` AND EXISTS (SELECT `id` FROM `benchmarks_benchmarkoptionvalue` WHERE `benchmarks_benchmarkoptionvalue`.`optionvalue_id`=`benchmarks_optionvalue`.`id` AND `benchmarks_benchmarkoptionvalue`.`benchmark_id` IN ("+q+")))"
	print query
	cursor.execute("SELECT `id`,`name`,`takes_argument` FROM `benchmarks_option` WHERE EXISTS (SELECT `id` FROM `benchmarks_optionvalue` WHERE `benchmarks_optionvalue`.`option_id`=`benchmarks_option`.`id` AND EXISTS (SELECT `id` FROM `benchmarks_benchmarkoptionvalue` WHERE `benchmarks_benchmarkoptionvalue`.`optionvalue_id`=`benchmarks_optionvalue`.`id` AND `benchmarks_benchmarkoptionvalue`.`benchmark_id` IN ("+q+")))")
	print "check"
	options = []
	for option in cursor:
		options.append({'id':option[0],'name':option[1],'takes_argument':option[2]})
	print "OPTIONS:"
	print options
	return options

def sortQuerySet(qs,sort):
	s = sort['sort']
	
	#translate if needed
	if s in SORTS.keys():
		s = SORTS[s]
		
	if sort['sortorder']==SORT_DESCENDING:
		s = '-'+s
	print 'sort with: '+s
	qs = qs.order_by(s)
	return qs

def getColumns(qs):
	result = []
	#result.append({'header':'Model','value':'model__name'})
	#result.append({'header':'States','value':'states_count'})
	#result.append({'header':'Runtime','value':'total_time'})
	#result.append({'header':'Memory (RSS)','value':'memory_RSS'})
	#result.append({'header':'Memory (VSIZE)','value':'memory_VSIZE'})
	#result.append({'header':'Finished','value':'finished'})
	return result