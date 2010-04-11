import re
from benchmarks.models import *

queue = []

#method to check/queue changes to the DB
def queue_save(item):
	queue.append(item)

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
#do something with the data
for item in rows:
	m =table_slice.match(item)
	model_name = m.group(1)
	fields = m.group(2)
	field_list = field_slice.findall(fields)
	print model_name
	print field_list
	handler(model_name, field_list)
	
print queue