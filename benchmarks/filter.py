"""
	Function to convert all given filters to a dictionary so it can be immediatelly used in QuerySet.filter(**dictionary)
	@todo add options to filter
"""
def convertfilters(filters):
	result = {}
	for k,v in filters.iteritems():
		arr = v.split(',')
		if arr[0]==u'options':
			i = 1
			while i<len(arr):
				#voeg de opties toe aan het resultaat
				i = i+2
		else:
			if arr[0]==u'name' or arr[0]==u'date':
				result[str(arr[1])] = str(arr[2])
			elif arr[0]==u'memory' or arr[0]==u'runtime' or arr[0]==u'states' or arr[0]==u'transitions':
				result[str(arr[1])] = int(arr[2])
	return result

"""
	Function that converts the filters given through ajax and returns the filtered benchmarks
"""
def filter(qs, filters):
	f = convertfilters(filters)
	return qs.filter(**f)