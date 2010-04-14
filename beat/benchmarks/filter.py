from datetime import date,timedelta

class Filter:
	def __init__(self, filterType, filterStyle, filterValue, row):
		self.filterType = filterType
		self.filterStyle = filterStyle
		self.filterValue = filterValue
		self.row = row
	
	def apply(self,qs):
		
		if self.filterType==u'options':
			print "options: "+self.filterStyle+","+self.filterValue
			
			qs = qs.filter(optionvalue__option__name__iexact=str(self.filterStyle),optionvalue__value__iexact=str(self.filterValue))
		elif self.filterType==u'date':
			strarr = self.filterValue.split('-')
			arr = []
			arr.append(int(strarr[0]))
			arr.append(int(strarr[1]))
			arr.append(int(strarr[2]))
			print arr
			
			if self.filterStyle==u'on':
				qs = qs.filter(date_time__gte=date(arr[0],arr[1],arr[2]),date_time__lt=(date(arr[0],arr[1],arr[2])+timedelta(days=1)))
			elif self.filterStyle==u'before':
				qs = qs.filter(date_time__lte=date(arr[0],arr[1],arr[2]))
			elif self.filterStyle==u'after':
				qs = qs.filter(date_time__gte=date(arr[0],arr[1],arr[2]))
			print qs
		else:
			f = ""
			if self.filterType==u'name':
				f+="model__name"
			elif self.filterType==u'memory':
				f+="memory_VSIZE"
			elif self.filterType==u'runtime':
				f+="elapsed_time"
			elif self.filterType==u'states':
				f+="states_count"
			elif self.filterType==u'transitions':
				f+="transition_count"
			
			if self.filterStyle==u'equal':
				f+="__iexact"
			elif self.filterStyle==u'contains':
				f+="__icontains"
			elif self.filterStyle==u'beginswith':
				f+="__istartswith"
			elif self.filterStyle==u'endswith':
				f+="__iendswith"
			elif self.filterStyle==u'greaterthen':
				f+="__gte"
			elif self.filterStyle==u'lessthan':
				f+="__lte"
			
			print "filter: "+f
			bla = {}
			bla[f] = self.filterValue
			qs = qs.filter(**bla)
		
		return qs
	
	def __unicode__(self):
		return u'type:'+self.filterType+',style:'+self.filterStyle+',value:'+self.filterValue

"""
	Function to convert all given filters to a dictionary so it can be immediatelly used in QuerySet.filter(**dictionary)
	@todo add options to filter
"""
def convertfilters(filters):
	result = []
	for k,v in filters.iteritems():
		arr = v.split(',')
		result.append(Filter(arr[0],arr[1],arr[2],arr[3]))
	return result

"""
	Function that converts the filters given through ajax and returns the filtered benchmarks
"""
def filter(qs, filters):
	for f in filters:
		qs = f.apply(qs)
	return qs