"""
This file contains functions to make a response for the client, given the data the client send (like filters, columns, etc.)
"""
from django.template import RequestContext
from beat.benchmarks.models import *
from beat.benchmarks.filter import *
from datetime import datetime
import json,copy
from beat import settings

#The constant ASCENDING, containing the string the client sends if it wants to sort on a column ascending
ASCENDING = 'ASC'
#The constant DESCENDING, containing the string the client sends if it wants to sort on a column descending
DESCENDING = 'DESC'

#The constant STANDARDCOLUMNS, contains all the names of the standard columns and the String which should be shown in the webinterface
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

#The STANDARDCOLUMNSARRAY, a list of all the standard column names
STANDARDCOLUMNSARRAY = [MODEL,STATES,TRANSITIONS,RUNTIME,MEMORY_RSS,MEMORY_VSIZE,TOOL,ALGORITHM,VERSION,DATE,FINISHED,COMPUTERNAME,CPU,RAM,KERNELVERSION,DISKSPACE,OPTIONS]

#The constant HARDWARECOLUMNS, contains all the names of the columns that come from the Hardware table and the String which should be shown in the webinterface
HARDWARECOLUMNS = 	[
						{'dbname':COMPUTERNAME,'name':'Computername'},
						{'dbname':CPU,'name':'Processor'},
						{'dbname':RAM,'name':'RAM'},
						{'dbname':KERNELVERSION,'name':'Kernel version'},
						{'dbname':DISKSPACE,'name':'Disk space'},
					]

#The HARDWARECOLUMNSARRAY, a list of all the hardware column names
HARDWARECOLUMNSARRAY = [COMPUTERNAME,CPU,RAM,KERNELVERSION,DISKSPACE]

"""
Function getBenchmarks
Called by ajax_execute, decodes the JSON-object the client send and returns the response
"""
def getBenchmarks(request):
	data = json.loads(request.POST['data'])
	return makeResponse(Benchmark.objects.all()
						, convertfilters(data['filters'])
						, data['sort']
						, data['columns']
						, data['page']
						, data['pagesize']
						, data['subset'])

"""
Function makeResponse
Makes a response for the client.
Takes an initial QuerySet and filters it, sorts it, gets all specified columns and selects the currect benchmarks for paging
This response also contains the context for all filters requiring context
"""
def makeResponse(qs=Benchmark.objects.all(),filters=[],sort=[],columns=[MODEL],page=0,pagesize=200,subset=[]):
	#initial result
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
	
	#Apply all the filters, get context before applying a ListFilter
	for k,f in filters.iteritems():
		if f.type in CONTEXTFILTERS:
			result[f.type] = getContext(qs,f.type)
		
		qs = f.apply(qs)
	
	#getting remaining results
	for s in CONTEXTFILTERS:
		if len(result[s]) == 0:
			result[s] = getContext(qs,s)
	
	#Get all possible identifiers in the QuerySet
	result['benchmark_ids'] = list(qs.values_list('id',flat=True))
	#Get all possible columns
	result['columns'] = getColumns(qs)
	#Select columns
	qs = addColumns(qs,columns)
	#Sort the queryset
	qs = sortQuerySet(qs,sort)
	
	#Get paged benchmarks
	result['benchmarks'] = list(qs[ page * pagesize : (page+1) * pagesize ])
	
	return result

"""
Function getModels
Takes a QuerySet and returns a list of all model names of the benchmarks in this QuerySet
"""
def getModels(qs):
	return sa(qs.values_list('model__name',flat=True).distinct())

"""
Function getAlgorithms
Takes a QuerySet and returns a list of all algorithm names of the benchmarks in this QuerySet
"""
def getAlgorithms(qs):
	return sa(qs.values_list('algorithm_tool__algorithm__name',flat=True).distinct())

"""
Function getTools
Takes a QuerySet and returns a list of all tool names of the benchmarks in this QuerySet
"""
def getTools(qs):
	return sa(qs.values_list('algorithm_tool__tool__name',flat=True).distinct())

"""
Function getOptions
Takes a QuerySet and returns a list of all option identifiers, names, and takes_argument's of the benchmarks in this QuerySet
"""
def getOptions(qs):
	optionlist = OptionValue.objects.filter(benchmark__in = qs).values("option__id","option__name","option__takes_argument").distinct()
	options = []
	
	for item in optionlist:
		options.append({'id':item['option__id'],'name':item['option__name'],'takes_argument':item['option__takes_argument']})
	
	return options

"""
Function getCPUs
Takes a QuerySet and returns a list of all processors of the benchmarks in this QuerySet
"""
def getCPUs(qs):
	return sa(BenchmarkHardware.objects.filter(benchmark__in = qs).values_list('hardware__cpu',flat=True).distinct())

"""
Function getComputerNames
Takes a QuerySet and returns a list of all computer names of the benchmarks in this QuerySet
"""
def getComputerNames(qs):
	return sa(BenchmarkHardware.objects.filter(benchmark__in = qs).values_list('hardware__computername',flat=True).distinct())

"""
Function getVersions
Takes a QuerySet and returns a list of all algorithm-tool versions of the benchmarks in this QuerySet
"""
def getVersions(qs):
	return sa(qs.values_list('algorithm_tool__version',flat=True).distinct())

"""
Function getKernelVersions
Takes a QuerySet and returns a list of all kernel versions of the benchmarks in this QuerySet
"""
def getKernelVersions(qs):
	return sa(BenchmarkHardware.objects.filter(benchmark__in = qs).values_list('hardware__kernelversion',flat=True).distinct())

"""
Function sortQuerySet
Takes a QuerySet and an array of column names and ascending/descending
Sorts the QuerySet on these columns
"""
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

"""
Function getColumns
Takes a QuerySet and returns a list of all available column names, which includes the standard columns (and thus hardware columns) and extra columns
"""
def getColumns(qs):
	cols = copy.deepcopy(STANDARDCOLUMNS)
	extracols = ExtraValue.objects.filter(benchmark__in=qs.values_list("id")).values_list("name",flat=True).distinct()
	for c in extracols:
		cols.append({'dbname' : c, 'name' : c})
	
	return cols

"""
Function getContext
Takes a QuerySet and a filter type and returns the corresponding context
"""
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

"""
Function addColumns
Takes a QuerySet and a list of column names and makes sure the columns are available for the QuerySet.
If a column name is not a standard columns, the function searches the value in the ExtraValue table.
The identifier of each benchmark is added as well
"""
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
	
	return apply(qs.values, columns + ['id'])

"""
Function sa (StringArray)
Takes a QuerySet which only has one value set through values(_list) and returns a list of strings of that value.
"""
def sa(qs):
	res = []
	for v in qs:
		res.append(str(v))
	return res






