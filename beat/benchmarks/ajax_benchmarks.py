from django.template import RequestContext
from beat.benchmarks.models import *
from beat.benchmarks.filter import *
from datetime import datetime
from django.db import connection,transaction
import json

SORT_ASCENDING = 'ASC'
SORT_DESCENDING = 'DESC'

PROCESSOR = 'cpu'
PHYSICALMEMORY = 'memory'
COMPUTERNAME = 'computername'
KERNELVERSION = 'kernelversion'
DISKSPACE = 'disk_space'

DEFAULTSORT = 'id'
DEFAULTSORTORDER = SORT_ASCENDING
SORTS = {}
DEFAULTCOLUMNS = []
DEFAULTFILTERS = {}
DEFAULTPAGE = 0
DEFAULTPAGESIZE = 200
DEFAULTHARDWARECOLUMNS = []

DEFAULTDATA = 	{
					'filters':			DEFAULTFILTERS,
					'sort':				DEFAULTSORT,
					'sortorder':		DEFAULTSORTORDER,
					'columns':			DEFAULTCOLUMNS,
					'page':				DEFAULTPAGE,
					'pagesize':			DEFAULTPAGESIZE,
					'hardwarecolumns': 	DEFAULTHARDWARECOLUMNS
				}

def getBenchmarks(request):
	data = json.loads(request.POST['data'])
	data['filters'] = convertfilters(data['filters'])
	res = getResponse(Benchmark.objects.all(),data)
	return res

def getResponse(qs,data):
	result = {'benchmarks':[],
				'columns':[],
				'algorithms':[],
				'options':[],
				'tools':[],
				'models':[],
				'cpus':[],
				'computernames':[],
				'benchmark_ids':[]}
	
	if len(data['subset']) != 0:
		qs = qs.filter(id__in=data['subset'])
	
	for k,f in data['filters'].iteritems():
		if f.type==MODEL:
			result['models'] = getModels(qs)
		if f.type==ALGORITHM:
			result['algorithms'] = getAlgorithms(qs)
		elif f.type==TOOL:
			result['tools'] = getTools(qs)
		elif f.type==OPTIONS:
			result['options'] = getOptions(qs)
		elif f.type==CPU:
			result['cpus'] = getCPUs(qs)
		elif f.type==COMPUTERNAME:
			result['computernames'] = getComputerNames(qs)
		
		qs = f.apply(qs)
	
	#getting remaining results
	if len(result['models'])==0:
		result['models'] = getModels(qs)
	
	if len(result['algorithms'])==0:
		result['algorithms'] = getAlgorithms(qs)
	
	if len(result['tools'])==0:
		result['tools'] = getTools(qs)
	
	if len(result['options'])==0:
		result['options'] = getOptions(qs)
	
	if len(result['cpus'])==0:
		result['cpus'] = getCPUs(qs)
	
	if len(result['computernames'])==0:
		result['computernames'] = getComputerNames(qs)
	
	columns = data['columns']
	selectdict = {}
	for extraval in data['extracolumns']:
		columns.append(extraval)
		selectdict[extraval] = "SELECT value FROM benchmarks_extravalue WHERE benchmark_id=benchmarks_benchmark.id AND name LIKE '"+extraval+"'"
	
	qs = qs.extra(select = selectdict)
	
	hwdict = {}
	for hwval in data['hardwarecolumns']:
		columns.append(hwval)
		hwdict[hwval] = 'SELECT ' + hwval + ' FROM benchmarks_benchmarkhardware, benchmarks_hardware WHERE benchmarks_benchmarkhardware.hardware_id = benchmarks_hardware.id AND benchmarks_benchmarkhardware.benchmark_id = benchmarks_benchmark.id'
	
	qs = qs.extra(select = hwdict)
	
	qs = apply(qs.values, columns)
	
	
	benchmark_ids = list(qs.values_list('id',flat=True))
	qs = sortQuerySet(qs,data['sort'],data['sortorder'])
	
	result['benchmarks'] = list(qs[data['page'] * data['pagesize'] : (data['page'] + 1) * data['pagesize']]) #includes paging
	result['extracolumns'] = list(getExtraColumns(qs))
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

def getComputerNames(qs):
	hw = Hardware.objects.values("id","computername")
	list = []
	for item in hw:
		list.append({'id':item['id'],'name':item['computername']})
	return list

def sortQuerySet(qs,sort,sortorder):
	if sortorder == SORT_DESCENDING:
		sort = '-' + sort
	qs = qs.order_by(sort)
	return qs

def getExtraColumns(qs):
	cols = ExtraValue.objects.filter(benchmark__in=qs.values_list("id")).values_list("name",flat=True).distinct()
	return cols