from django.template import RequestContext
from beat.benchmarks.models import *
from beat.benchmarks.filter import *
from datetime import datetime
from django.db import connection,transaction
import json

SORT_ASCENDING = 'ASC'
SORT_DESCENDING = 'DESC'

DEFAULTSORT = 'id'
DEFAULTSORTORDER = SORT_ASCENDING
SORTS = {}
DEFAULTCOLUMNS = []
DEFAULTFILTERS = {}
DEFAULTPAGE = 0
DEFAULTPAGESIZE = 200

DEFAULTDATA = 	{
					'filters':		DEFAULTFILTERS,
					'sort':			DEFAULTSORT,
					'sortorder':	DEFAULTSORTORDER,
					'columns':		DEFAULTCOLUMNS,
					'page':			DEFAULTPAGE,
					'pagesize':		DEFAULTPAGESIZE
				}

def getBenchmarks(request):
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
	cpus = []
	pcnames = []
	benchmark_ids = []
	
	if len(data['subset']) != 0:
		qs = qs.filter(id__in=data['subset'])
	
	for k,f in data['filters'].iteritems():
		if f.type==MODEL:
			models = getModels(qs)
		if f.type==ALGORITHM:
			algorithms = getAlgorithms(qs)
		elif f.type==TOOL:
			tools = getTools(qs)
		elif f.type==OPTIONS:
			options = getOptions(qs)
		elif f.type==CPU:
			cpus = getCPUs(qs)
		elif f.type==COMPUTERNAME:
			pcnames = getPCNames(qs)
		
		qs = f.apply(qs)
	
	#getting remaining results
	if len(models)==0:
		models = getModels(qs)
	
	if len(algorithms)==0:
		algorithms = getAlgorithms(qs)
	
	if len(tools)==0:
		tools = getTools(qs)
	
	if len(options)==0:
		options = getOptions(qs)
	
	if len(cpus)==0:
		cpus = getCPUs(qs)
	
	if len(pcnames)==0:
		pcnames = getPCNames(qs)
	
	#Adding values of selected extra columns:
	#Benchmark.objects.extra(select={"name":'SELECT value FROM benchmarks_extravalue WHERE benchmark_id=benchmarks_benchmark.id'})
	benchmark_ids = list(qs.values_list('id',flat=True))
	extracolumns = getExtraColumns(qs)
	qs = sortQuerySet(qs,data['sort'],data['sortorder'])
	page = data['page']
	pagesize = data['pagesize']
	
	qs = apply(qs.values, data['columns'])
	
	result['benchmarks'] = list(qs[page*pagesize : (page+1)*pagesize]) #includes paging
	result['columns'] = list(extracolumns)
	result['algorithms'] = algorithms
	result['options'] = options
	result['tools'] = tools
	result['models'] = models
	result['cpus'] = cpus
	result['computernames'] = pcnames
	result['benchmark_ids'] = benchmark_ids
	return result

def getModels(qs):
	models = []
	for model in qs.values('model','model__name').order_by('model__name').distinct():
		models.append({'id':model['model'],'name':model['model__name']})
	return models

def getAlgorithms(qs):
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

def getCPUs(qs):
	hw = Hardware.objects.values_list("cpu",flat=True).distinct()
	list = []
	for i in range(0,len(hw)):
		list.append({'id':i,'name':hw[i]})
	return list

def getPCNames(qs):
	hw = Hardware.objects.values("id","name")
	list = []
	for item in hw:
		list.append({'id':item['id'],'name':item['name']})
	return list

def sortQuerySet(qs,sort,sortorder):
	#translate if needed
	#if sort in SORTS.keys():
		#sort = SORTS[sort]
		
	if sortorder == SORT_DESCENDING:
		sort = '-' + sort
	qs = qs.order_by(sort)
	return qs

def getExtraColumns(qs):
	cols = ExtraValue.objects.filter(benchmark__in=qs.values_list("id")).values("name").distinct()
	return cols