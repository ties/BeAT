from datetime import datetime

MODEL 			= 'model'
ALGORITHM 		= 'algorithm'
TOOL 			= 'tool'
MEMORY_RSS		= 'memory_RSS'
MEMORY_VSIZE	= 'memory_VSIZE'
RUNTIME 		= 'runtime'
STATES 			= 'states'
TRANSITIONS 	= 'transitions'
DATE 			= 'date'
OPTIONS 		= 'options'
FINISHED 		= 'finished'
COMPUTERNAME 	= 'computername'
CPU 			= 'cpu'
RAM				= 'ram'
COMPUTERNAME	= 'computername'

EQUAL 			= 'equal'
GREATERTHAN 	= 'greaterthan'
LESSTHAN 		= 'lessthan'
ON 				= 'on'
BEFORE			= 'before'
AFTER 			= 'after'
TRUE 			= 'true'
FALSE 			= 'false'

LISTFILTERS = [MODEL,ALGORITHM,TOOL,COMPUTERNAME]

VALUEFILTERS = [MEMORY_RSS,MEMORY_VSIZE,RUNTIME,STATES,TRANSITIONS,RAM]

class Filter(object):
	def __init__(self, type, row):
		self.type = str(type)
		self.row = row

class ListFilter(Filter):
	def __init__(self,type,row,list):
		super(ListFilter,self).__init__(type,row)
		self.list = list
	
	def apply(self,qs):
		f = ""
		if self.type == MODEL:
			f = "model__in"
		elif self.type == ALGORITHM:
			f = "algorithm_tool__algorithm__in"
		elif self.type == TOOL:
			f = "algorithm_tool__tool__in"
		elif self.type == COMPUTERNAME:
			f = "hardware__in"
		elif self.type == CPU:
			f = "hardware__cpu__in"
		
		col = {}
		col[f] = list(set(self.list))
		qs = qs.filter(**col)
		return qs

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

class OptionsFilter(Filter):
	def __init__(self,row,options):
		super(OptionsFilter,self).__init__(OPTIONS,row)
		self.options = options
	
	def apply(self,qs):
		for k,v in self.options.iteritems():
			qs = qs.filter(optionvalue__option__id__exact=k,optionvalue__value__iexact=str(v))
		return qs

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

class FinishedFilter(Filter):
	def __init__(self,row,finished):
		super(FinishedFilter,self).__init__(FINISHED,row)
		self.finished = str(finished)
	
	def apply(self,qs):
		qs = qs.filter(finished__exact=self.finished)
		return qs

class CPUFilter(Filter):
	def __init__(self,row,list):
		super(CPUFilter,self).__init__(CPU,row)
		self.list = list
	
	def apply(self,qs):
		qs = qs.filter(hardware__cpu__in=self.list)
		return qs

def convertfilters(arr):
	result = {}
	for filter in arr:
		row = filter['row']
		type = filter['type']
		if type in LISTFILTERS:
			list = []
			for v in filter['value']:
				list.append(int(v))
			result[row] = ListFilter(type,row,list)
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
		elif type==CPU:
			result[row] = CPUFilter(row,filter['value'])
	return result