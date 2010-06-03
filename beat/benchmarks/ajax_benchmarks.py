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
	
	#Adding values of selected extra columns:
	#Benchmark.objects.extra(select={"name":'SELECT value FROM benchmarks_extravalue WHERE benchmark_id=benchmarks_benchmark.id'})
	benchmark_ids = list(qs.values_list('id',flat=True))
	
	extracolumns = getExtraColumns(qs)
	
	qs = sortQuerySet(qs,data['sort'])
	
	page = data['paging']['page']
	resperpage = data['paging']['resperpage']
	
	qs = apply(qs.values,data['columns'])
	
	result['benchmarks'] = list(qs[page*resperpage : (page+1)*resperpage]) #includes paging
	result['columns'] = extracolumns
	result['algorithms'] = algorithms
	result['options'] = options
	result['tools'] = tools
	result['models'] = models
	result['benchmark_ids'] = benchmark_ids
	
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
	return algorithms

def getTools(qs):
	tools = []
	for tool in qs.values('algorithm_tool__tool','algorithm_tool__tool__name').order_by('algorithm_tool__tool__name').distinct():
		tools.append({'id':tool['algorithm_tool__tool'],'name':tool['algorithm_tool__tool__name']})
	return tools

def getOptions(qs):
	ops = ValidOption.objects.filter(algorithm_tool__in=qs.values_list("algorithm_tool__id"))#use id's of benchmarks here
	optionlist = ops.values("option__id","option__name","option__takes_argument").distinct()
	options = []
	
	for item in optionlist:
		options.append({'id':item['option__id'],'name':item['option__name'],'takes_argument':item['option__takes_argument']})
	
	return options

def sortQuerySet(qs,sort):
	s = sort['sort']
	
	#translate if needed
	if s in SORTS.keys():
		s = SORTS[s]
		
	if sort['sortorder']==SORT_DESCENDING:
		s = '-'+s
	qs = qs.order_by(s)
	return qs

def getExtraColumns(qs):
	cols = ExtraValue.objects.filter(benchmark__in=qs.values_list("id")).values("name").distinct()
	#test dit! print cols
	return cols