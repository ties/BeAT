class Filter:
	def __init__(self, filterType, filterStyle, filterValue):
		self.filterType = filterType
		self.filterStyle = filterStyle
		self.filterValue = filterValue
	
	def apply(self,qs):
		print "apply:"
		f = ""
		if self.filterType==u'name':
			f+="model__name"
		elif self.filterType==u'date'
		
		if self.filterStyle==u'equal':
			f+="__iexact"
		elif self.filterStyle==u'contains':
			f+="__icontains"
		elif self.filterStyle==u'beginswith':
			f+="__istartswith"
		elif self.filterStyle==u'endswith':
			f+="__iendswith"
		elif self.filterStyle==u'on':
			f+="__date_time__exact"
		elif self.filterStyle==u'before':
			f+="__date_time__lte"
		elif self.filterStyle==u'after':
			f+="__date_time__gte"
		elif self.filterStyle==u'greaterthen':
			f+="__gte"
		elif self.filterStyle==u'lessthan':
			f+="__lte"
		
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
	print "convertfilters"
	result = []
	for k,v in filters.iteritems():
		arr = v.split(',')
		result.append(Filter(arr[0],arr[1],arr[2]))
		print "added filter:"+v
		#if arr[0]==u'options':
		#	i = 1
		#	while i<len(arr):
				#voeg de opties toe aan het resultaat
		#		i = i+2
		#else:
			#convert the values to strings or integers
		#	if arr[0]==u'name' or arr[0]==u'date':
		#		result[str(arr[1])] = str(arr[2])
		#	elif arr[0]==u'memory' or arr[0]==u'runtime' or arr[0]==u'states' or arr[0]==u'transitions':
		#		result[str(arr[1])] = int(arr[2])
	return result

"""
	Function that converts the filters given through ajax and returns the filtered benchmarks
"""
def filter(qs, filters):
	print filters
	for f in filters:
		qs = f.apply(qs)
	return qs