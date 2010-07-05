from django.template import RequestContext
from beat.benchmarks.models import *
from beat.benchmarks.filter import *
from datetime import datetime
import json,copy
from beat import settings

ASCENDING = 'ASC'
DESCENDING = 'DESC'

STANDARDCOLUMNS = 	[
						{'dbname':MODEL,'name':'Model name'},
						{'dbname':STATES,'name':'States'},
						{'dbname':TRANSITIONS,'name':'Transitions'},
						{'dbname':RUNTIME,'name':'Runtime'},
						{'dbname':MEMORY_RSS,'name':'Memory (RSS)'},
						{'dbname':MEMORY_VSIZE,'name':'Memory (VSIZE)'},
						{'dbname':TOOL,'name':'Tool name'},
						{'dbname':ALGORITHM,'name':'Algorithm name'},
						{'dbname':VERSION,'name':'Version'},
						{'dbname':DATE,'name':'Date'},
						{'dbname':FINISHED,'name':'Finished'},
						{'dbname':COMPUTERNAME,'name':'Computername'},
						{'dbname':CPU,'name':'Processor'},
						{'dbname':RAM,'name':'RAM'},
						{'dbname':KERNELVERSION,'name':'Kernel version'},
						{'dbname':DISKSPACE,'name':'Disk space'},
						{'dbname':OPTIONS,'name':'Options'},
					]

STANDARDCOLUMNSARRAY = [MODEL,STATES,TRANSITIONS,RUNTIME,MEMORY_RSS,MEMORY_VSIZE,TOOL,ALGORITHM,VERSION,DATE,FINISHED,COMPUTERNAME,CPU,RAM,KERNELVERSION,DISKSPACE,OPTIONS]

HARDWARECOLUMNS = 	[
						{'dbname':COMPUTERNAME,'name':'Computername'},
						{'dbname':CPU,'name':'Processor'},
						{'dbname':RAM,'name':'RAM'},
						{'dbname':KERNELVERSION,'name':'Kernel version'},
						{'dbname':DISKSPACE,'name':'Disk space'},
					]

HARDWARECOLUMNSARRAY = [COMPUTERNAME,CPU,RAM,KERNELVERSION,DISKSPACE]

def getBenchmarks(request):
	data = json.loads(request.POST['data'])
	return makeResponse(Benchmark.objects.all()
						, convertfilters(data['filters'])
						, data['sort']
						, data['columns']
						, data['page']
						, data['pagesize']
						, data['subset'])

def makeResponse(qs=Benchmark.objects.all(),filters=[],sort=[],columns=[MODEL],page=0,pagesize=200,subset=[]):
	result = 	{	'benchmarks'		: [],
					'columns'			: {},
					'benchmark_ids'		: [],
					MODEL				: [],
					ALGORITHM			: [],
					TOOL				: [],
					OPTIONS				: [],
					CPU					: [],
					COMPUTERNAME		: [],
					VERSION				: [],
					KERNELVERSION		: [],
				}
	
	#Apply the subset if identifiers
	if len(subset) != 0:
		qs = qs.filter(id__in = subset)
	
	#Apply all the filters, get modelnames/algorithmnames/toolnames/options/processornames/computernames before applying the corresponding filter
	for k,f in filters.iteritems():
		if f.type in CONTEXTFILTERS:
			result[f.type] = getContext(qs,f.type)
		
		qs = f.apply(qs)
	
	#getting remaining results
	for s in CONTEXTFILTERS:
		if len(result[s]) == 0:
			result[s] = getContext(qs,s)
	
	result['benchmark_ids'] = list(qs.values_list('id',flat=True)) 				#Get all possible identifiers in the QuerySet
	
	#Select columns
	qs = addColumns(qs,columns)
	
	#Sort the queryset
	qs = sortQuerySet(qs,sort)
	
	result['benchmarks'] = list(qs[ page * pagesize : (page+1) * pagesize ]) 	#Get paged benchmarks
	result['columns'] = getColumns(qs) 											#Get all possible columns
	return result

def getModels(qs):
	return sa(qs.values_list('model__name',flat=True).order_by('model__name').distinct())
	models = []
	for model in qs.values_list('model__name',flat=True).order_by('model__name').distinct():
		models.append(model)
	return models

def getAlgorithms(qs):
	return sa(qs.values_list('algorithm_tool__algorithm__name',flat=True).order_by('algorithm_tool__algorithm__name').distinct())
	algorithms = []
	for algorithm in qs.values('algorithm_tool__algorithm','algorithm_tool__algorithm__name').order_by('algorithm_tool__algorithm__name').distinct():
		algorithms.append({'id':algorithm['algorithm_tool__algorithm'],'name':algorithm['algorithm_tool__algorithm__name']})
	return algorithms

def getTools(qs):
	return sa(qs.values_list('algorithm_tool__tool__name',flat=True).order_by('algorithm_tool__tool__name').distinct())
	tools = []
	for tool in qs.values('algorithm_tool__tool','algorithm_tool__tool__name').order_by('algorithm_tool__tool__name').distinct():
		tools.append({'id':tool['algorithm_tool__tool'],'name':tool['algorithm_tool__tool__name']})
	return tools

def getOptions(qs):
	optionlist = OptionValue.objects.filter(benchmark__in = qs).values("option__id","option__name","option__takes_argument").distinct()
	options = []
	
	for item in optionlist:
		options.append({'id':item['option__id'],'name':item['option__name'],'takes_argument':item['option__takes_argument']})
	
	return options

def getCPUs(qs):
	return sa(BenchmarkHardware.objects.filter(benchmark__in = qs).values_list('hardware__cpu',flat=True).distinct())
	hw = Hardware.objects.values_list("cpu",flat=True).distinct()
	list = []
	for i in range(0,len(hw)):
		list.append({'id':i,'name':hw[i]})
	return list

def getComputerNames(qs):
	return sa(BenchmarkHardware.objects.filter(benchmark__in = qs).values_list('hardware__computername',flat=True).distinct())
	hw = Hardware.objects.values("id","computername")
	list = []
	for item in hw:
		list.append({'id':item['id'],'name':item['computername']})
	return list

def getVersions(qs):
	return sa(qs.values_list('algorithm_tool__version',flat=True).distinct())
	versions = qs.values_list('algorithm_tool__version',flat=True).distinct()
	res = []
	for v in versions:
		res.append(str(v))
	return res

def getKernelVersions(qs):
	return sa(BenchmarkHardware.objects.filter(benchmark__in = qs).values_list('hardware__kernelversion',flat=True).distinct())
	kernelversions = BenchmarkHardware.objects.filter(benchmark__in = qs).values_list('hardware__kernelversion',flat=True).distinct()
	res = []
	for v in kernelversions:
		res.append(str(v))
	return res

def sortQuerySet(qs,sort):
	if sort != []:
		order = []
		
		for s in sort:
			if s[1] == DESCENDING:
				order.append('-' + s[0])
			else:
				order.append(s[0])
		
		return apply(qs.order_by, order)
	
	return qs.order_by('id')

def getColumns(qs):
	cols = copy.deepcopy(STANDARDCOLUMNS)
	extracols = ExtraValue.objects.filter(benchmark__in=qs.values_list("id")).values_list("name",flat=True).distinct()
	for c in extracols:
		cols.append({'dbname' : c, 'name' : c})
	
	return cols

def getContext(qs,type):
	if type == MODEL:
		return getModels(qs)
	elif type == ALGORITHM:
		return getAlgorithms(qs)
	elif type == TOOL:
		return getTools(qs)
	elif type == COMPUTERNAME:
		return getComputerNames(qs)
	elif type == CPU:
		return getCPUs(qs)
	elif type == OPTIONS:
		return getOptions(qs)
	elif type == VERSION:
		return getVersions(qs)
	elif type == KERNELVERSION:
		return getKernelVersions(qs)

def addColumns(qs,columns):
	for c in columns:
		if c == OPTIONS:
			if settings.DATABASES.get('default').get('ENGINE') == 'django.db.backends.postgresql_psycopg2' or settings.DATABASES.get('default').get('ENGINE') == 'django.db.backends.postgresql':
				qs = qs.extra(select={c:"SELECT array_to_string( ARRAY( SELECT (benchmarks_option.name || '=' || benchmarks_optionvalue.value) FROM benchmarks_benchmarkoptionvalue, benchmarks_optionvalue, benchmarks_option WHERE benchmarks_benchmarkoptionvalue.optionvalue_id = benchmarks_optionvalue.id AND benchmarks_benchmarkoptionvalue.benchmark_id = benchmarks_benchmark.id AND benchmarks_optionvalue.option_id = benchmarks_option.id), ', ')"})
			elif settings.DATABASES.get('default').get('ENGINE') == 'sqlite3' or settings.DATABASES.get('default').get('ENGINE') == 'django.db.backends.sqlite3':
				qs = qs.extra(select={c:"SELECT group_concat((benchmarks_option.name || '=' || benchmarks_optionvalue.value),', ') FROM benchmarks_benchmarkoptionvalue, benchmarks_optionvalue, benchmarks_option WHERE benchmarks_benchmarkoptionvalue.optionvalue_id = benchmarks_optionvalue.id AND benchmarks_benchmarkoptionvalue.benchmark_id = benchmarks_benchmark.id AND benchmarks_optionvalue.option_id = benchmarks_option.id"})
		elif c in HARDWARECOLUMNSARRAY:
			qs = qs.extra(select={c:'SELECT ' + c + ' FROM benchmarks_benchmarkhardware, benchmarks_hardware WHERE benchmarks_benchmarkhardware.hardware_id = benchmarks_hardware.id AND benchmarks_benchmarkhardware.benchmark_id = benchmarks_benchmark.id'})
		elif c not in STANDARDCOLUMNSARRAY:
			qs = qs.extra(select={c:"SELECT value FROM benchmarks_extravalue WHERE benchmark_id=benchmarks_benchmark.id AND name LIKE '" + c + "'"})
	
	return apply(qs.values, columns)

def sa(qs):
	res = []
	for v in qs:
		res.append(str(v))
	return res






