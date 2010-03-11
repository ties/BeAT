"""
This file reader is just an initial version.
Hopefully, the intermediate format will be implemented, which makes the process of parsing a lot easier.
For now, only nips2lts-grey and nips2lts-grey that writes to a .dir output file are supported.
Hardware, Options, timestamp and other stuff that is to be taken from the (not yet approved) commandline script is still missing.

Usage:
filereader.py [-v] %file%
-v:		verbose mode.

In the future, verbose mode will support various levels of detail.
Right now, verbose mode is only of much use when the user knows the code.
"""
import re
import datetime
import sys
from benchmarks.models import *

#function for matching regexes
#flags is optional
def match_regex(regex, input, flags=None):
	"""
	regex should be a regular expression string
	input should be any string
	flags will be passed directly to the regex compiler
	This method will return None, True or a dictionary, as defined by the groupdict() function of the python regex library (re).
	None will be returned when no match is found.
	True will be returned when a match is found, but the regex contained no groups (ie. groupdict() returns something empty).
	"""
	if flags:
		compiled = re.compile(regex, flags)
	else:
		compiled = re.compile(regex)
	match = compiled.match(input)
	#return any 
	if match:
		list = match.groupdict()
		if not list:
			#no group arguments
			list = True
		return list
	elif verbose:
		print "Warning: Regex ", regex, " on input ", input, "has an empty dictionary."
		if flags:
			print "Flags argument to compiler: ", flags
	return None

def write_to_db(data):
	"""
	the input, data is specified as follows:
	{
		'model'	:	(name, version, location)
		'tool'		:	(name, version)
		'hardware'	:	[(name, memory, cpu, disk_space, os),			]
		'options'	:	[(name, value), (name, value),					]
		'benchmark':	(date, elapsedtime, usertime, systime, transitioncount, statecount, memoryVSIZE, memoryRSS)
	}
	for hardware and options, one tuple for each entry that should appear in the DB
	location in model should be such that it works with Django's FilePathField type
	the rest can be strings or integers, as python does automatic casting anyway.
	transitioncount should be -1 if not available
	TODO: checks all row creations for dupes
	"""
	#model entry
	name, version, location = data['model']
	if not name or version == -1 or not location:
		if verbose:
			print "Warning: Model.name=",name,"Model.version=",version,"Model.location=",location
		#name or version invalid -> raise an error
		#for location, just leave it none
	m = Model(name=name ,version=version, location=location)

	#tool entry
	name, version = data['tool']
	if not name or version == -1:
		if verbose:
			print "Warning: Tool.name=",name,"Tool.version=",version
		#name or version invalid -> raise an error
	t = Tool(name=name, version=version)

	#hardware entries
	hwdata = data['hardware']
	hardwarelist = []
	for tuple in hwdata:
		name, memory, cpu, disk_space, os = tuple
		if not name or memory == -1 or not cpu or disk_space ==-1 or not os:
			if verbose:
				print "Warning: HW.name=",name,"HW.memory=",memory,"HW.cpu",cpu,"HW.disk_space",disk_space,"HW.os",os
			#name, memory, cpu or os invalid -> raise error (or continue?)
			#disk_space invalid -> don't set
		if disk_space > 0:
			h = Hardware(name=name, memory=memory, cpu=cpu, disk_space=disk_space, os=os)
		else:
			h = Hardware(name=name, memory=memory, cpu=cpu, os=os)
		hardwarelist.append(h)

	#option entries
	optiondata = data['options']
	optionlist = []
	for tuple in optiondata:
		name, value = tuple
		if not name or not value or value == -1:
			if verbose:
				print "Warning, invalid option: name",name,"value",value
			continue #ignore this tuple and move on
		o = Option(name=name,value=value)
		optionlist.append(o)
	
	#this one's always new
	#add BenchmarkHardware and BenchmarkOption reference here
	date, utime, stime, etime, tcount, scount, mVSIZE, mRSS = data['benchmark']
	if date == -1 or utime == -1 or stime == -1 or etime == -1 or tcount == -1 or scount == -1 or mVSIZE == -1 or mRSS == -1:
		if tcount == -1:
			#tcount can be not defined.
			tcount = None
		else:
			if verbose:
				print "Warning, invalid value in benchmark"
			#raise an error
	
	#if the code goes up 'till here we can save everything.
	t.save()
	m.save()
	for hw in hardwarelist:
		hw.save()
	for o in optionlist:
		o.save()
	#now create and save the db object
	b = Benchmark(model_id=m, tool_id=t, date_time=date, user_time=utime, system_time=stime, elapsed_time=etime, transition_count=tcount, states_count=scount, memory_VSIZE=mVSIZE, memory_RSS=mRSS)
	b.save()
	#connect the manytomany relations. this has to happen AFTER calling save on the benchmark.
	for option in optionlist:
		b.option_id.add(option)
	for hardware in hardwarelist:
		b.hardware_id.add(hardware)
	b.save()
	
#here are the new parsers
#content should be a string containing the entire output here
def parse_nips_grey(content, options=None):
	# todo:
	#write here code to call various functions to parse the different types of nips2lts-grey output
	#this is a quickfix:
	if not options:
		match = match_regex(r'nips2lts-grey: NIPS language module initialized\n.*\nnips2lts-grey: state space(?P<statespaceline>.*)transitions\nExit \[[0-9]+\]\n(?P<memtimeline>.*)',content, re.MULTILINE + re.DOTALL)
	elif options.startswith('fileout_dir'):
		match = match_regex(r'nips2lts-grey: NIPS language module initialized\n.*\nnips2lts-grey: state space(?P<statespaceline>.*)transitions.*\nExit \[[0-9]+\]\n(?P<memtimeline>.*)',content, re.MULTILINE + re.DOTALL)
	if verbose:
		print "Notice: match (at start)= ", match
	if match:
		m0 = match_regex(r'^ has \d+ levels (?P<scount>\d+) states (?P<tcount>\d+) $',match['statespaceline'])
		m1 = match_regex(r'^(?P<utime>[0-9\.]+) user, (?P<stime>[0-9\.]+) system, (?P<etime>[0-9\.]+) elapsed --( Max | )VSize = (?P<vsize>\d+)KB,( Max | )RSS = (?P<rss>\d+)KB$',match['memtimeline'])
		if verbose:
			print "Notice: |",match['statespaceline'],"| parses to: ", m0
			print "Notice: |",match['memtimeline'],"| to: ", m1
		match = {
			'model':('test', -1, None),
			'tool':('nips2lts-grey', -1),
			'hardware':[],
			'options':[],
			'benchmark':(-1,m1['etime'], m1['utime'],m1['stime'],m0['tcount'],m0['scount'],m1['vsize'],m1['rss']),
		}
	if verbose:
		print "Notice: match (at end)= ", match
	return match
	
def get_parser(content):
	if(content.startswith('nips2lts-grey:')):
		return parse_nips_grey
	else:
		print "Error: parsing of the data in the specified file is not yet supported."
		exit()

# ######program starts here ######## #
verbose = False

for item in sys.argv:
	if item.startswith('-v'):
		print "Notice: Verbose switch provided. Get ready for lots of output!"
		verbose = True
	elif item.endswith('filereader.py'):
		path = None
	else:
		path = item
if not path:
	print "Error: no file provided.\nUsage: filereader.py [-v] file"
	exit()
if verbose:
	print sys.argv
try:
	file = open(path, 'r')
except IOError as detail:
	#if something breaks, output the error and ask for retry
	print 'Error: ', detail, '\n'
	print "Usage: filereader.py [-v] file"
	exit()
#we have a file to work with


#read the lines 
lines = []
runended = False
while not runended:
	try:
		line = file.next()
	except StopIteration:
		if verbose:
			print "Notice: end of file encountered"
		runended = True
		break
	lines.append(line)
if lines:
	parser = get_parser(''.join(lines))
elif verbose:
	print "Warning: no lines were parsed from ", file
file.close()
#run the parser and write the result
write_to_db(parser(''.join(lines), 'fileout_dir'))
exit()