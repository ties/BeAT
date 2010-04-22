import re
from benchmarks.models import *

#this pair of functions will replace both regexes until I figure out how to do it right in regex
def field_slicer(string):
	model_name = ''
	contents = []
	#read model name
	i = 0
	c = ''
	while c != ',':
		model_name+=c
		c = string[i]
		i+=1
	data = read_contents(string, i)
	return (model_name, data)

def read_contents(string, i):
	depth = 0
	c=''
	contents = []
	#read contents
	while i<len(string)-1:
		#read (optional) field_name
		while c != ':':
			c = string[i]
			i+=1
		#fetch first char of the value
		c = string[i]
		i+=1
		if c == '(':
			#there's a nesting
			depth+=1
			tmp=''
			while depth>0:
				c = string[i]
				i+=1
				if c=='(':
					depth+=1
				elif c==')':
					depth-=1
				if depth>0:
					tmp+=c
			data = read_contents(tmp, 0)
			 #i gets updated, data is what we want to store
			contents.append(data)
			#eat a comma
			i+=1
		else:
			#no nesting
			tmp =''
			while c != ',':
				tmp+=c
				c = string[i]
				i+=1
			contents.append(tmp)
	return contents

#procedure to check/queue changes to the DB
def queue_save(item):
	queue.append(item)

#procedure to save everything currently in the queue
#ignores any errors that may occur
def save_queue():
	for q in queue:
		try:
			q.save()
#			print "Processed: %s"%(q)
		except Exception, e:
#			print "Error: %s. Object: %s"%(e,q)
			pass
	for q in queue:
		queue.remove(q)
	

#converts a nested csv to a nested list.
#(a,b,c,(1,2,3)) becomes a list containing a, b, c and a list, which in turn contains 1, 2 and 3
def csv_to_array(str):
	field_list = field_slice.findall(str)
	field_array = []
	for x in field_list:
		if x[0]:
			y = csv_to_array(x[0])
			field_array.append(y)
		else:
			field_array.append(x[1])
#	print "<<%s>> -> <<%s>>"%(str, field_array)
	return field_array
	
#this is really really really really really ugly
def handler(type, args):
	created = False
	result = None
	if type == 'model':
		result = Model(name = args[0])
	elif type == 'ov':
		o = handler('option', args[0])
		result, created = OptionValue.objects.get_or_create(option=o, value=args[1])
	elif type == 'option':
		result, created = Option.objects.get_or_create(name=args[0])
	elif type == 'hw':
		result, created = Hardware.objects.get_or_create(name=args[0], memory=args[1], cpu=args[2], disk_space=args[3], os=args[4])
	elif type == 'tool':
		result, created = Tool.objects.get_or_create(name=args[0], version = args[1])
	elif type == 'validopt':
		at = handler('algtool', args[0])
		op = handler('option', args[1])
		if len(args)==3:#possible creation
			r  = handler('regex', args[2])
			result, created = ValidOption.objects.get_or_create(algorithm_tool=at, option=op, defaults={'regex':r})
		else:#existing item
			result = ValidOption.get(algorithm_tool=at, option=op)
	elif type == 'algtool':
		a = handler('alg', args[0])
		t = handler('tool',args[1])
		if len(args)==3:#creation?
			r = handler('regex', args[2])
			result, created = AlgorithmTool.objects.get_or_create(algorithm=a, tool=t, defaults={'regex':r})
		else:#use existing
			result = AlgorithmTool.objects.get(algorithm=a, tool=t)
	elif type == 'alg':
		result, created = Algorithm.objects.get_or_create(name=args[0])
	elif type == 'regex':
		result, created = Regex.objects.get_or_create(regex=args[0])
	elif type == 'shortarg':
		at = handler('algtool', args[0])
		op = handler('option', args[1])
		result, created = RegisteredShortcut.objects.get_or_create(algorithm_tool=at, option=op, shortcut=args[2])
	else:
		print "Warning: failed to handle: %s with %s"%(type, args)
	if created:
		queue_save(result)
	return result
	
#models:
#	'model':		Model,			#(name, version, location)),
#	'ov':			OptionValue,		#(option, value)), #option is an FK
#	'option':		Option,			#(name)),
#	'hw':			Hardware,			#(name, memory, cpu, disk_space, os)),
#	'tool':		Tool,				#(name, version)),
#	'validopt':		ValidOption,		#(algorithm_tool, option, regex)), #all three are FKs
#	'algtool':		AlgorithmTool,		#(algorithm, tool, regex)), #all three are FKs
#	'alg':			Algorithm,			#(name)),
#	'regex':		Regex,			#(regex)),
#	'shortarg':		RegisteredShortcut,	#(algorithm_tool, option, shortcut)) #first two are FKs
#

#recursively fixes escapes in the provided argument.
#array may be a string or any nesting of lists, as long as their contents are only lists and strings.
def fix_escapes(array):
	if array:
		if isinstance(array,list):#process what's inside
			tmp = []
			for x in array:
				tmp.append(fix_escapes(x))
			array = tmp
		else:
			#replace escaped comma
			array = array.replace('\\1',',')
			#replace escaped (
			array = array.replace('\\2','(')
			#replace escaped )
			array = array.replace('\\3',')')
			#replace escaped backslash
			array = array.replace('\\\\','\\')
	return array
	

use_regex = False

#regular expression for splitting a line into the model identifier and the contents
table_slice = re.compile(r'(.*?),(.*)')
#regular expression to break the contents up into bits, such that the data for each field is contained in one of the two groups
#if the data represents a foreign key, the data will be in the left group ([0]), otherwise in the right group ([1])
#use field_slice.findall() to get a list containing a series of tuples, each containing these left and right groups.
field_slice = re.compile(r'(?:[^:]*?:\(([^)]*?)\),)|(?:[^:]*?:([^,]*?),)')

queue = []

# ####	code starts here	##### #
#read file
rows = []
with open('db_defaults', 'r') as file:
	for line in file:
		if not line.startswith('#') and len(line)>1:#filters out comments and empty lines
			rows.append(line)
import time
currtime = time.time()
#do something with the data
for item in rows:
	if use_regex:
		m =table_slice.match(item)
		model_name = m.group(1)
		fields = m.group(2)
		field_array = fix_escapes(csv_to_array(fields))
	else:
		model_name, field_array = field_slicer(item)
		field_array = fix_escapes(field_array)

	handler(model_name, field_array)
	save_queue()
#	print "created %s with data %s" %(model_name, field_array)
print "done! Took %s seconds" %(time.time()-currtime)

