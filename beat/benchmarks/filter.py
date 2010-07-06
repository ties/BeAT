"""
This file contains the specifications for Filter-classes, which can filter a Django QuerySet, given certain data
"""
from datetime import datetime
from beat.benchmarks.models import *
"""
Names of all the filters
"""
MODEL 			= 'model__name'
ALGORITHM 		= 'algorithm_tool__algorithm__name'
TOOL 			= 'algorithm_tool__tool__name'
MEMORY_RSS		= 'memory_RSS'
MEMORY_VSIZE	= 'memory_VSIZE'
RUNTIME 		= 'total_time'
STATES 			= 'states_count'
TRANSITIONS 	= 'transition_count'
DATE 			= 'date_time'
OPTIONS 		= 'options'
FINISHED 		= 'finished'
COMPUTERNAME 	= 'computername'
CPU 			= 'cpu'
RAM				= 'memory'
VERSION			= 'algorithm_tool__version'
KERNELVERSION	= 'kernelversion'
DISKSPACE		= 'disk_space'

"""
Filter styles of value filters
"""
EQUAL 			= 'equal'
GREATERTHAN 	= 'greaterthan'
LESSTHAN 		= 'lessthan'

"""
Filter styles of date filter
"""
ON 				= 'on'
BEFORE			= 'before'
AFTER 			= 'after'
"""
List containing all the list filters
"""
LISTFILTERS = [MODEL,ALGORITHM,TOOL,COMPUTERNAME,VERSION,KERNELVERSION,CPU]
"""
List containing all value filters
"""
VALUEFILTERS = [MEMORY_RSS,MEMORY_VSIZE,RUNTIME,STATES,TRANSITIONS,RAM,DISKSPACE]
"""
List containing all filters that need context
"""
CONTEXTFILTERS = [MODEL,ALGORITHM,TOOL,COMPUTERNAME,CPU,OPTIONS,VERSION,KERNELVERSION]

"""
Class Filter
Acts as an abstract class for all filters
"""
class Filter(object):
	def __init__(self, type, row):
		self.type = str(type)
		self.row = row

"""
Class ListFilter
Takes a list of values and filters a given QuerySet that it should at least satisfy one of them
"""
class ListFilter(Filter):
	def __init__(self,type,row,list):
		super(ListFilter,self).__init__(type,row)
		self.list = list
	
	def apply(self,qs):
		if self.type == MODEL:
			qs = qs.filter(model__name__in=self.list)
		elif self.type == ALGORITHM:
			qs = qs.filter(algorithm_tool__algorithm__name__in=self.list)
		elif self.type == TOOL:
			qs = qs.filter(algorithm_tool__tool__name__in=self.list)
		elif self.type == COMPUTERNAME:
			qs = qs.filter(hardware__computername__in=self.list)
		elif self.type == CPU:
			qs = qs.filter(hardware__cpu__in=self.list)
		elif self.type == KERNELVERSION:
			qs = qs.filter(hardware__kernelversion__in=self.list)
		elif self.type == VERSION:
			qs = qs.filter(algorithm_tool__version__in=self.list)
		return qs

"""
Class ValueFilter
Takes a filtering style (EQUAL, GREATERTHAN, or LESSTHAN) and a value and filters the QuerySet on them
"""
class ValueFilter(Filter):
	def __init__(self,type,row,style,value):
		super(ValueFilter,self).__init__(type,row)
		self.style = str(style)
		self.value = int(value)
	
	def apply(self,qs):
		f = ""
		if self.type==STATES:
			f="states_count"
		elif self.type==TRANSITIONS:
			f="transition_count"
		elif self.type==MEMORY_RSS:
			f="memory_RSS"
		elif self.type==MEMORY_VSIZE:
			f="memory_VSIZE"
		elif self.type==RUNTIME:
			f="total_time"
		elif self.type==RAM:
			f="hardware__memory"
		elif self.type==DISKSPACE:
			f="hardware__disk_space"
		
		if self.style==EQUAL:
			f+="__exact"
		elif self.style==GREATERTHAN:
			f+="__gte"
		elif self.style==LESSTHAN:
			f+="__lte"
		
		col = {}
		col[f] = self.value
		qs = qs.filter(**col)
		
		return qs

"""
Class OptionsFilter
Takes a list of option identifiers and values and filters a QuerySet so it only contains benchmarks with all the correct options and values
"""
class OptionsFilter(Filter):
	def __init__(self,row,options):
		super(OptionsFilter,self).__init__(OPTIONS,row)
		self.options = options
	
	def apply(self,qs):
		for k,v in self.options.iteritems():
			try:
				ov = OptionValue.objects.get(option=k,value=v)
				qs = qs.filter(optionvalue__in = [ov.id])
			except OptionValue.DoesNotExist:
				#This will return an empty QuerySet... since EmptyQuerySet.values.distinct fails
				return Benchmark.objects.filter(id__in=[0])
			
		return qs

"""
Class DateFilter
Takes a filter style and value and filters a QuerySet so it only contains benchmarks satisfying them
"""
class DateFilter(Filter):
	def __init__(self,row,style,date):
		super(DateFilter,self).__init__(DATE,row)
		self.style = str(style)
		strarr = date.split('-')
		arr = []
		arr.append(int(strarr[0]))
		arr.append(int(strarr[1]))
		arr.append(int(strarr[2]))
		self.date = arr
	
	def apply(self,qs):
		if self.style==ON:
			qs = qs.filter(date_time__gte=datetime(self.date[0],self.date[1],self.date[2],0,0,0),date_time__lte=datetime(self.date[0],self.date[1],self.date[2],23,59,59))
		elif self.style==BEFORE:
			qs = qs.filter(date_time__lte=datetime(self.date[0],self.date[1],self.date[2],23,59,59))
		elif self.style==AFTER:
			qs = qs.filter(date_time__gte=datetime(self.date[0],self.date[1],self.date[2],0,0,0))
		
		return qs

"""
Class FinishedFilter
Takes a Boolean value and filters a QuerySet to contain only those benchmarks of which the finished value is equal to the Boolean value
"""
class FinishedFilter(Filter):
	def __init__(self,row,finished):
		super(FinishedFilter,self).__init__(FINISHED,row)
		self.finished = (str(finished).lower()=="true")
	
	def apply(self,qs):
		qs = qs.filter(finished__exact=self.finished)
		return qs

"""
Function convertfilters
This function converts data received from the client to Filter objects
"""
def convertfilters(arr):
	result = {}
	for filter in arr:
		row = filter['row']
		type = filter['type']
		if type in LISTFILTERS:
			result[row] = ListFilter(type,row,filter['value'])
		elif type in VALUEFILTERS:
			result[row] = ValueFilter(type,row,str(filter['style']),float(filter['value']))
		elif type==DATE:
			result[row] = DateFilter(row,filter['style'],filter['value'])
		elif type==OPTIONS:
			options = {}
			for i in range(len(filter['value'][0])):
				options[int(filter['value'][0][i])] = str((filter['value'][1])[i])
			result[row] = OptionsFilter(row,options)
		elif type==FINISHED:
			result[row] = FinishedFilter(row,filter['value'])
	return result