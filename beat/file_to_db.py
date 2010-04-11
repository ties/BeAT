import re
from benchmarks.models import *

queue = []

#procedure to check/queue changes to the DB
def queue_save(item):
	queue.append(item)

#procedure to save everything currently in the queue
#ignores any errors that may occur
def save_queue(queue):
	for q in queue:
		try:
			q.save()
		except Exception, e:
			print e
			pass
	queue = []

#empties the queue without saving
def clear_queue():
	queue = []

	

#converts a nested csv to a nested list.
#(a,b,c,(1,2,3)) becomes a list containing a, b, c and a list, which in turn contains 1, 2 and 3
def csv_to_array(str, sfl=False):
	print str
	field_list = field_slice.findall(str)
	print field_list 
	field_array = []
	for x in field_list:
		if x.startswith('('):
			y = csv_to_array(x.lstrip('(').rstrip(')'))
			field_array.append(y)
		else:
			field_array.append(x)
	return field_array
	

#this is really really really really really ugly
def handler(type, args):
	result = None
	if type == 'model':
		result = Model(name = args[0])
	elif type == 'ov':
		o = handler('option', args[0])
		result = OptionValue(option=o, value=args[1])
	elif type == 'option':
		result = Option(name=args[0])
	elif type == 'hw':
		result = Hardware(name=args[0], memory=args[1], cpu=args[2], disk_space=args[3], os=args[4])
	elif type == 'tool':
		result = Tool(name=args[0], version = args[1])
	elif type == 'validopt':
		at = handler('algtool', args[0])
		op = handler('option',  args[1])
		r  = handler('regex',   args[2])
		result = ValidOption(algorithm_tool=at, option=op, regex=r)
	elif type == 'algtool':
		a = handler('alg', args[0])
		t = handler('tool',args[1])
		r = handler('regex',args[2])
		result = AlgorithmTool(algorithm=a, tool=t, regex=r)
	elif type == 'alg':
		result = Algorithm(name=args[0])
	elif type == 'regex':
		result = Regex(regex=args[0])
	elif type == 'shortarg':
		at = handler('algtool', args[0])
		op = handler('option', args[1])
		result = RegisteredShortcut(algorithm_tool=at, option=op, shortcut=args[2])
	else:
		print "Warning: failed to handle: %s with %s"%(type, args)
	queue_save(result)
	return result
	
#this is a simple script that imports default data from the included db_defaults file

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

#read file
rows = []
with open('db_defaults', 'r') as file:
	for line in file:
		if not line.startswith('#'):
			rows.append(line)

table_slice = re.compile(r'(.*?),(.*)')
field_slice = re.compile(r'(?:.*?):(.*?),')
sub_field_slice = re.compile(r'(?:.*?):\((.*)\),')
#do something with the data
for item in rows:
	m =table_slice.match(item)
	model_name = m.group(1)
	fields = m.group(2)
	field_array = csv_to_array(fields)
	#print field_array
	handler(model_name, field_array)
	print "created %s with data %s" %(model_name, field_array)
	save_queue(queue)
	