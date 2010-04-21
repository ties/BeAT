from datetime import datetime

LISTFILTERS = [
	u'model',
	u'tool',
	u'algorithm']

OPTIONFILTERS = [u'options']
VALUEFILTERS = [
	u'memory',
	u'runtime',
	u'states',
	u'transitions']
DATEFILTERS = [u'date']

class Filter(object):
	def __init__(self, type, row):
		self.type = type
		self.row = row

class ListFilter(Filter):
	def __init__(self,type,row,list):
		super(ListFilter,self).__init__(type,row)
		print "made listfilter"
		self.list = list
	
	def apply(self,qs):
		f=self.type+u'__id__in'
		print "check apply listfilter"
		col = {}
		col[f] = list(set(self.list))
		print col
		qs = qs.filter(**col)
		print "check applied"
		return qs

class ValueFilter(Filter):
	def __init__(self,type,row,style,value):
		super(ValueFilter,self).__init__(type,row)
		self.style = style
		self.value = value
	
	def apply(self,qs):
		f = ""
		if self.type==u'states':
			f="states_count"
		elif self.type==u'transitions':
			f="transition_count"
		elif self.type==u'memory':
			f="memory_RSS"
		elif self.type==u'runtime':
			f="total_time"
		
		if self.style==u'equal':
			f+="__exact"
		elif self.style==u'greaterthan':
			f+="__gte"
		elif self.style==u'lessthan':
			f+="__lte"
		
		col = {}
		col[f] = self.value
		qs = qs.filter(**col)
		
		return qs

class OptionFilter(Filter):
	def __init__(self,row,options):
		super(OptionFilter,self).__init__(u'options',row)
		self.options = options
	
	def apply(self,qs):
		for k,v in self.options.iteritems():
			print k
			print v
			qs = qs.filter(optionvalue__option__id__exact=k,optionvalue__value__iexact=str(v))
		return qs

class DateFilter(Filter):
	def __init__(self,row,style,date):
		super(DateFilter,self).__init__(u'date',row)
		self.style = style
		strarr = date.split('-')
		arr = []
		arr.append(int(strarr[0]))
		arr.append(int(strarr[1]))
		arr.append(int(strarr[2]))
		self.date = arr
	
	def apply(self,qs):
		if self.style==u'on':
			qs = qs.filter(date_time__gte=datetime(self.date[0],self.date[1],self.date[2],0,0,0),date_time__lte=datetime(self.date[0],self.date[1],self.date[2],23,59,59))
		elif self.style==u'before':
			qs = qs.filter(date_time__lte=datetime(self.date[0],self.date[1],self.date[2],23,59,59))
		elif self.style==u'after':
			qs = qs.filter(date_time__gte=datetime(self.date[0],self.date[1],self.date[2],0,0,0))
		
		return qs

def convertfilters(filters):
	result = []
	for filter in filters:
		row = int(filter[0][6])
		type = filter[1][0]
		
		if type in LISTFILTERS:
			list = []
			for v in filter[1][1:]:
				list.append(int(v))
			result.append(ListFilter(type,row,list))
		elif type in VALUEFILTERS:
			result.append(ValueFilter(type,row,filter[1][1],float(filter[1][2])))
		elif type in DATEFILTERS:
			result.append(DateFilter(row,filter[1][1],filter[1][2]))
		elif type in OPTIONFILTERS:
			options = {}
			for v in filter[1][1:]:
				arr = v.split(',')
				options[int(arr[0])] = arr[1]
			result.append(OptionFilter(row,options))
	print "check"
	return result

def filter(qs,filters):
	for f in filters:
		print f
		qs = f.apply(qs)
	return qs