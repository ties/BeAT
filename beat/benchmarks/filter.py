from datetime import datetime

MODEL = 'model'
ALGORITHM = 'algorithm'
TOOL = 'tool'
MEMORY = 'memory'
RUNTIME ='runtime'
STATES ='states'
TRANSITIONS ='transitions'
DATE ='date'
OPTIONS = 'options'
FINISHED = 'finished'

EQUAL = 'equal'
GREATERTHAN = 'greaterthan'
LESSTHAN = 'lessthan'
ON = 'on'
BEFORE= 'before'
AFTER = 'after'
TRUE = 'true'
FALSE = 'false'

LISTFILTERS = [MODEL,ALGORITHM,TOOL]

VALUEFILTERS = [MEMORY,RUNTIME,STATES,TRANSITIONS]

class Filter(object):
	def __init__(self, type, row):
		self.type = str(type)
		self.row = row

class ListFilter(Filter):
	def __init__(self,type,row,list):
		super(ListFilter,self).__init__(type,row)
		self.list = list
	
	def apply(self,qs):
		f=str(self.type)+'__id__in'
		col = {}
		col[f] = list(set(self.list))
		print "List filter:"
		print col
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
		elif self.type==MEMORY:
			f="memory_RSS"
		elif self.type==RUNTIME:
			f="total_time"
		
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
			print k
			print v
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
		if self.finished==TRUE:
			qs = qs.filter(finished__exact=True)
		elif self.finished==FALSE:
			print "filtering false:"
			qs = qs.filter(finished__exact=False)
			print "done!"
			print qs.query
		
		return qs

def convertfilters(arr):
	result = {}
	for filter in arr:
		row = filter['row']
		type = filter['type']
		if type in LISTFILTERS:
			list = []
			for v in filter['list']:
				list.append(int(v))
			result[row] = ListFilter(type,row,list)
		elif type in VALUEFILTERS:
			result[row] = ValueFilter(type,row,str(filter['style']),float(filter['value']))
		elif type==DATE:
			result[row] = DateFilter(row,filter['style'],filter['value'])
		elif type==OPTIONS:
			options = {}
			for i in range(len(filter['options'])):
				options[int(filter['options'][i])] = str((filter['values'])[i])
			result[row] = OptionsFilter(row,options)
		elif type==FINISHED:
			print "Making finishedfilter with value: "+filter['value']
			result[row] = FinishedFilter(row,filter['value'])
	return result