import re
from benchmarks.models import *

#this pair of functions will replace both regexes until I figure out how to do it right in regex
def field_slicer(string):
	result = string.partition(',')
	model_name = result[0]
	data = read_contents(result[2])
	return (model_name, data)

def read_contents(string):
	contents = []
	#read contents
	while string:
		string = string[string.find(":"):]
		if string[0] == '(':
			depth = 1
			i = 1
			while depth > 0:
				if string[i] == '(':
					depth += 1
				elif string[i] == ')':
					depth -= 1
				i += 1
			contents.append( read_contents(string[1:i-2]) )
			string = string[i:]
		else:
			content, _, string = string.partition(',')
			contents.append(content)
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
	
#this is really really really really really ugly
def handler(type, args):
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
		if isinstance(array,list):			#process what's inside
			return fix_escapes(array[0]) + fix_escapes(array[1:])
		else:
			tmp = ""
			i = array.find('\\')
			while i is not -1:
				tmp += array[:i]
				if array[i+1] is '1':
					tmp += ','
				elif array[i+1] is '2':
					tmp += '('
				elif array[i+1] is '3':
					tmp += ')'
				elif array[i+1] is '\\':
					tmp += '\\'
				else:
					# ERROR!
					pass
				array = array[i+2:]
				i = array.find('\\')
			tmp += array
			return tmp
	return ""
	
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
	model_name, field_array = field_slicer(item)
	field_array = fix_escapes(field_array)

	handler(model_name, field_array)
	save_queue()
#	print "created %s with data %s" %(model_name, field_array)
print "done! Took %s seconds" %(time.time()-currtime)