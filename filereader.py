"""This script processes logs, using regular expressions that are in the database.
This script works as follows:
1. main() is called, either with or without arguments
2. if there are no arguments to main(), parse_app_options() is called to grab them from the commandline
3. the arguments, which should be a list of files, is iterated over, processing each file seperately.

Since each file may contain a sequence of logs, they are first split in seperate logs.
Then, we parse each log as follows (method: parse() unless noted otherwise):
1. Seperate the log in header and application log.
2. Read the header, deducing the required information (this includes talking to the database to find valid options) (methods: parse() and parse_call()).
3. Fetch from the database how to parse this application log (a regular expression).
4. Apply the regular expression to the application log and deduce information.
5. Write to the database (write_to_db()). This includes checking to protect against invalid data (check_data_validity()).
"""
#python libraries
import re		#regular expressions
import datetime	#for datetime objects
import sys		#for system calls
import os		#for os.path.split()
from decimal import Decimal #for use of DecimalField
from optparse import OptionParser

from beat.settings import LOGS_PATH, GIT_PATH
#from gitinterface import *

#django exceptions
from django.core.exceptions import ObjectDoesNotExist, MultipleObjectsReturned
#models
from beat.benchmarks.models import *

#the length of the header placed in the logs
RUN_DETAILS_HEADER = 11
#verbosity levels
V_NOISY = 2		#noisy:		print everything, including read input etc.
V_VERBOSE = 1	#verbose:	print debug support
V_QUIET = 0		#quiet:		print a line for each parsed log - default
V_SILENT = -1	#silent: 	surpress all messages except those that indicate database failure

#regular expression for the header
header_regex = re.compile(r'Nodename: (?P<name>.*)(\r\n|\n).*(\r\n|\n)OS: (?P<OS>.*)(\r\n|\n)Kernel-name: (?P<Kernel_n>.*)(\r\n|\n)Kernel-release: (?P<Kernel_r>.*)(\r\n|\n)Kernel-version: (?P<Kernel_v>.*)(\r\n|\n).*(\r\n|\n)Processor: (?P<processor>.*)(\r\n|\n)Memory-total: (?P<memory_kb>[0-9]+)(\r\n|\n)DateTime: (?P<datetime>.*)(\r\n|\n)ToolVersion: (?P<toolversion>.*)(\r\n|\n)Call: (?P<call>.*)(\r\n|\n)', re.MULTILINE + re.DOTALL)

#regular expression for extracting the model name from the filename of a log
logextension = re.compile(r'(.*)\.e[0-9]+')

class FileReader:
	#this variable will contain the log of the run of this filereader
	log = []
	#the verbosity level of this filereader. default is quiet.
	verbose = V_QUIET
	use_dulwich = False
	override = False
	
	def print_message(self, level, text):
		"""Function to log, based on verbosity level
		Arguments:
			level		the level from which this message should be printed
			text		the message

		Returns:
			This function returns nothing.
		"""
		if self.verbose >= level:
			#self.log.append(text)
			print text
	#end of print_message

	def match_regex(self, regex, input, flags=None):
		"""Matches a given regex on the input, given flags
		This function compiles (with flags, if given) and matches the regex on the input.
		Given an empty regex (ie. providing something that evaluates to False for regex) returns an empty dictionary
		If the regex does not use groups (ie. the groupdict() method returns None), this method will return True on a match.
		In other words, the function returns whether the regex matches, and returns the dictionary, if any.
		Arguments:
			regex		a regular expression string( r'' )
			input		any string to be matched on
			flags		a value to be passed to re.compile(), defaults to None.
		
		Returns:
			An empty dictionary if regex evaluates to False
			On a match, a dictionary containing the named groups
				or a list if the regex does not use named groups
				or true if this dictionary is empty
			Otherwise, returns None.
		"""
		#this fixes an issue; this function returned a list for the empty regex, but it makes more sense to get a dictionary
		if not regex:
			return {}
		#compile expression
		if flags:
			compiled = re.compile(regex, flags)
		else:
			compiled = re.compile(regex)
		#attempt a match
		match = compiled.match(input)
		if match:
			list = match.groupdict()
			if not list:
				#if there is no groupdict, named groups may not be used
				#figure out if there are non-named groups, eg using brackets only
				list = []
				i=0
				try:
					#this is quite ugly.
					while True:
						#will eventually throw an exception, causing us to jump to the except clause, from which we return
						list.append(match.group(i))
						i+=1
				except IndexError: #thrown when i = number of groups
					#check if there were any numbered groups at all, return them
					if i!=0:
						return list
				#no groups, but a match occurred: return True
				list = True
			return list
		else:
			return None
	#end of match_regex
	
	def parse(self, lines):
		"""Parse a run from the specified lines.
		This method analyzes the log file of one run, including a header. The length of the header is specified by the RUN_DETAILS_HEADER constant.
			Arguments:
				lines		a list of strings, including newlines
			Returns:
				None when some (non-fatal) error occurs, or:
				A dictionary, as specified by parse_log.
		"""
		self.print_message(V_NOISY, "Notice: Reading the header...")

		# # # # # # # # # # # # seperate the header

		header = []
		call = 0 #var for the line number for the line "Call: ..."
		dt = 0	 #var for the line number for the line "Datetime: ..."
		offset = 0	#offset, to skip content between logs or before the header
		
		header_started = False
		i = 0
		done = False
		#iterate 'till we've seen the whole log or when the header ends
		while i < len(lines) and not done:
			if header_started:
				#we're reading the header, check for its end
				if not lines[i].startswith("END OF HEADER"):
					header.append(lines[i])
					if lines[i].startswith("Call:"):
						call = i-1 - offset
					if lines[i].startswith("DateTime:"):
						dt = i-1 - offset
				else:
					done = True #stop
			#we're not at the header yet, keep reading 'till we find the start
			elif lines[i].startswith("BEGIN OF HEADER"):
				header_started = True
				offset = i
			i += 1
		
		#split the header off
		lines = lines[i:]
		
		# # # # # # # # # # # # analyze the header
		match = header_regex.match(''.join(header))
		if not match:
			self.print_message(V_QUIET, "Error: Could not analyze header. Are you sure the header is correctly formatted?")
			return None
		self.print_message(V_NOISY, "Notice: header is: %s"%(''.join(header)))
		m = match.groupdict()
		if not m:
			#matching the regex went quite wrong, the log must be broken
			self.print_message(V_QUIET, "Error: missing data in the header. Are you sure this log is complete?")
			return None
		
		#m contains the keys toolversion, name, memory_kb, processor, OS, Kernel_n, Kernel_r, Kernel_v
		
		toolversion = m.get('toolversion')
		tv = toolversion.split('-')
		
		#currently, only one hardware item is supported and disk size is not taken into account.
		hardware = [(m.get('name'), m.get('memory_kb'), m.get('processor'), 0, m.get('Kernel_r'))]

		#deduce information from the "Call: ..." line in the header
		tmp = self.parse_call(header[call][6:], toolversion)
		if tmp:
			(regexes, s, optlist, modelname) = tmp
		else:
			#An error occurred, skip this log
			return None
		
		#note: s[0] contains the whole call, s[1] contains the tool name and s[2] contains the algorithm name
		
		#fetch datetime info and create an object out of it
		dt = header[dt][10:].split(' ')
		dt = datetime.datetime(int(dt[0]), int(dt[1]), int(dt[2]), int(dt[3]), int(dt[4]), int(dt[5]))
		self.print_message(V_NOISY, "Notice: Header analysis complete!")
		self.print_message(V_NOISY, "Deduced information: %s\nTool: %s\nAlgorithm: %s\nOptions: %s\nModel: %s\nTime of run start:%s"%(m, s[1], s[2], optlist,modelname,dt))
		# # # # # # # # # # # # #parse the log content
		# we apply the regular expressions found in the database.
		m = {}
		first=True
		for rex in regexes:
			self.print_message(V_NOISY, "Applying regex: %s"%(rex))
			tmp = self.match_regex(rex.regex, ''.join(lines), re.MULTILINE + re.DOTALL)
			if not first:
				self.print_message(V_NOISY, "Notice: regex match gives: %s\n\tregex was:\"%s\""% (tmp,rex.regex))
			if not tmp and first:
				#the regex for the tool did not match, print an error and return None
				self.print_message(V_QUIET, "Error: Parse error. The log failed to match on the regex of the tool.")
				self.print_message(V_NOISY, "Notice: Details of error: \nExpression:\n%s\nLog:\n%s"% (rex.regex, ''.join(lines)) )
				return None
			else:
				first=False
			#append tmp to m, overwriting previous data, if anything is persent
			for key in tmp:
				if tmp[key]:
					m[key]=tmp[key]

		#collect the user-specified data
		matched ={}
		for key in m:
			if key not in ["etime","utime","stime","tcount","scount","vsize","rss","kill"]:
				matched[key]=m[key]
		
		#collect all relevant information into one dictionary
		data = {
			'model': modelname,
			'tool':(s[1], toolversion),
			'algorithm':s[2],
			'hardware':hardware,
			'options':optlist,
			'benchmark':(
				dt, m.get('etime'), m.get('utime'), m.get('stime'), m.get('tcount'),
				m.get('scount'), m.get('vsize'), m.get('rss'), not m.get('kill')
			),
			'extravals':matched
		}
		
		self.print_message(V_NOISY, "Notice: Derived data: %s"% (m))

		if data:
			self.print_message(V_NOISY, "Notice: Read successful!")
		
		#return this log's information as a dictionary.
		return data
	#end of parse
	
	def parse_call(self, call, version):
		"""Parses a call to an algorithm-tool
		A call, like "dve-reach -v --cache test.txt", is parsed by this method to provide all the useful information we can get from it.
			Arguments: 
				call		A string that shows how the run was executed
			Returns:
				A tuple, containing:
					a tuple 			of a Regex object and a list of Regex objects, which specifies how to parse this run (single one is for tool, rest is per option)
					a list				containing three elements; the call itself, the tool name and the algorithm name
					a list				of tuples: (option, value), as getopt.gnu_getopt() except options without value will appear with value True (as opposed to gnu_getopt, which would provide an empty string
					a string			containing the file name of the model
				or None, when the call cannot be parsed because the combination of tool and algorithm does not appear in the database.
		"""
		s = self.match_regex(r'^memtime (.*?)((?:2|-).*?)(?:$| .*$)', call)
		#s should result in: [call, toolname, algorithmname]
		if not s:
			#this is a fix introduced for an alternative naming scheme, where "memtime" is not included in the Call line
			s = self.match_regex(r'^.*?(.*?)((?:2|-).*?)(?:$| .*$)', call)
			if not s:
				#that's bad
				self.print_message(V_QUIET, "Error: invalid call in log: %s" %(call))
				return None
		
		#query the database for the regex that goes with the AlgorithmTool and then query those of the options
		regexes=[]
		try:
			t = Tool.objects.get(name=s[1])
			a = Algorithm.objects.get(name=s[2])
			at = AlgorithmTool.objects.get(tool=t, algorithm=a, version=version)
			regexes.append(at.regex)
			shortopts = ''
			#long options
			opts = []
			#fetch all valid options for this tool+algorithm combo
			for o in ValidOption.objects.filter(algorithm_tool=at):
				opts.append(o.option)
				if o.regex.regex:
					regexes.append(o.regex)
			#find the appropriate short options
			for option in opts:
				try:
					#throws an exception if there isn't any shortoption for this option
					rs = RegisteredShortcut.objects.get(algorithm_tool=at, option=option)
					if option.takes_argument:
						shortopts+=rs.shortcut+':'
					else:
						shortopts+=rs.shortcut
				except ObjectDoesNotExist:
					#just continue
					pass
		#handle database related errors
		except ObjectDoesNotExist:
			self.print_message(V_QUIET, "Error: This algorithm/tool/version combination is not known: %s%s (version %s)" %(s[1], s[2], version))
			return None
		except MultipleObjectsReturned:
			self.print_message(V_SILENT, "Error: multiple parsers for %s %s (version %s). This indicates database integrity issues!" %(s[1], 1, s[2]))
			return None
		#translate all options Option->ascii, ignoring unicode-only characters, and reformat them to match what gnu_getopt expects
		tmp = opts
		opts = []
		for i in tmp:
			if i.name.startswith("--"):
				if i.takes_argument:
					opts.append(i.name.encode('ascii', 'ignore')[2:] + '=')
				else:
					opts.append(i.name.encode('ascii', 'ignore')[2:])
			elif i.name.startswith(" "):
				#short option only: this is a bit of an ugly hack to get around our database limitation, which concerns itself primarely with long options
				pass
			else:
				if i.takes_argument:
					opts.append(i.name.encode('ascii', 'ignore') + '=')
				else:
					opts.append(i.name.encode('ascii', 'ignore'))

		#read the options for the tool and convert them into a nice list
		#arguments are discarded for now (also, some of those might be bash-parsed and not passed to the algorithm_tool)
		import getopt
		try:
			self.print_message(V_NOISY, "Notice: input for gnu_getopt: \n%s\n%s"%(shortopts,opts))
			if call.startswith("memtime"):
				optlist, args = getopt.gnu_getopt(call.split(" ")[2:], shortopts, opts)
			else:
				optlist, args = getopt.gnu_getopt(call.split(" ")[1:], shortopts, opts)
		except getopt.GetoptError as e:
			self.print_message(V_VERBOSE, "Warning: grabbing options failed: %s"%(e))
			return None
		#this fixes a bug related to a '\n' character being behind the model name, which occurred when model is the last string on the "Call: ..." line
		args[-1]=args[-1][:-1]

		counter = 0
		#getopt.gnu_getopt returns tuples, where the value is empty if the option is provided
		#we need a value, however; we'll use True
		for t in optlist:
			o, v = t
			if not v:	#no parameter
				optlist[counter]=(o,True)

			if not o.startswith('--'): #shortcut!
				p = o[1:] #chop the '-'
				rs = RegisteredShortcut.objects.get(algorithm_tool=at, shortcut=p)
				if v:
					optlist[counter]=(rs.option.name, v)
				else:
					optlist[counter]=(rs.option.name, True)
			
			counter+=1
		
		self.print_message(V_NOISY, "read options and arguments, resulting in:\noptions:%s\nargs:%s"%(optlist,args))
		(head, tail) = os.path.split(args[0])
		#tail contains the filename of the log
		#that is formatted as <modelname>.e<number> in our tests.
		#we can use the logextension regex to chop that .e<number> part off.
		#should this not work (as with a real-life log), we'll just use the full argument that is in the log
		match = logextension.match(tail)
		if match:
			tail = match.group(1)

		#return as the docstring describes
		return (regexes, s, optlist, tail)
	#end of parse_call
	
	def check_data_validity(self, data):
		"""Checks the data validity.
		The data argument is one that is intended to be inserted in the database.
		This method should prevent incorrect or incomplete data from entering the database.
		The data argument may be updated to correct data, such as 'None' being provided to an integer field (this will become 0)
		If the verbosity is Verbose or higher, all applicable warnings will be produced before returning.
			Arguments:
				data		a dictionary, containing all the data about one run, as returned by parse_log()
			Returns:
				True when the data is sufficient
				False when something is incorrect (ie. missing data, negative numbers where they are not allowed, etc)
		"""
		#assume things are correct, then walk through the data based on the classes in models.py
		valid = True

		#Model
		name = data['model']
		if not name:
			self.print_message(V_VERBOSE, "Warning while checking: Data invalid. Model.name=%s"%(name))
			valid=False

		#Algorithm
		name = data['algorithm']
		try:
			a = Algorithm.objects.get(name=name)
		except (MultipleObjectsReturned, ObjectDoesNotExist) as e:
			self.print_message(V_VERBOSE, "Warning while checking: %s"%(e))
			valid=False

		#Tool
		name, version = data['tool']
		try:
			t = Tool.objects.get(name=name)
		except (MultipleObjectsReturned, ObjectDoesNotExist) as e:
			self.print_message(V_VERBOSE, "Warning while checking: %s"%(e))
			valid = False

		#AlgorithmTool
		try:
			at = AlgorithmTool.objects.get(tool=t, algorithm=a, version=version)
		except (MultipleObjectsReturned, ObjectDoesNotExist) as e:
			self.print_message(V_VERBOSE, "Warning while checking: %s"%(e))
			valid = False

		#Hardware
		hwdata = data['hardware']
		for tuple in hwdata:
			computername, memory, cpu, disk_space, os = tuple
			#memory may not be zero, disk_space may be.
			if not computername or memory <=0 or not cpu or disk_space <0 or not os:
				self.print_message(V_VERBOSE, "Warning while checking: Data invalid. HW.name=%s HW.memory=%s HW.cpu=%s HW.disk_space=%s HW.os=%s" %(name, memory, cpu, disk_space, os))
				valid=False
		
		#Option
		optiondata = data['options']
		for tuple in optiondata:
			name, value = tuple
			if not name or not value:
				self.print_message(V_VERBOSE, "Warning while checking: invalid option: name=<%s> value=<%s>"%(name,value))
				valid=False
			try:
				o = Option.objects.get(name=name)
			except (MultipleObjectsReturned, ObjectDoesNotExist) as e:
				self.print_message(V_VERBOSE, "Warning while checking: Django error: %s"%(e))
				self.print_message(V_NOISY, "Notice: name: %s, value:%s"%(name,value))
				valid = False

		#Benchmark
		date, utime, stime, etime, tcount, scount, mVSIZE, mRSS, finished = data['benchmark']
		self.print_message(V_NOISY,"Statecount for this run is: %s, did it finish? %s"% (scount,finished))
		if not date or utime <0 or stime <0 or etime <0 or tcount <0 or scount <0 or mVSIZE <0 or mRSS <0:
			if not tcount or (not scount and not finished):
				#tcount is allowed to be empty, scount is not given if excecution is ended prematurely
				if not tcount:
					tcount = 0
					data['benchmark'] = (date, utime, stime, etime, tcount, scount, mVSIZE, mRSS, finished)
				if not scount and not finished:
					scount = 0
					data['benchmark'] = (date, utime, stime, etime, tcount, scount, mVSIZE, mRSS, finished)
			else:
				self.print_message(V_VERBOSE, "Warning while checking: invalid value in benchmark %s"% ((date, utime, stime, etime, tcount, scount, mVSIZE, mRSS)))
				valid=False
		for key in data['extravals']:
			if data['extravals'][key] is None:
				self.print_message(V_VERBOSE, "Warning while checking: invalid extra value for benchmark, name: %s"% (key))
				valid=False
		return (valid, data)
	#end of check_data_validity
	
	def write_to_db(self, data):
		"""Tests, and if correct, writes the data to the database
			Arguments:
				data			the data that is to be inserted to the database, as a dictionary, describing a single run
			Returns:
				nothing.
		"""
		#check the data
		valid, data = self.check_data_validity(data)
		if not valid:
			#provide an error
			if self.verbose:
				raise FileReaderError("Error: some invalid data provided.", debug_data=data)
			else:
				raise FileReaderError("Error: some invalid data provided.")
		else:
			self.print_message(V_NOISY, "Notice: Validity checked and passed, writing to DB...")
		
		#note that if the logs were generated using our tools, most of the information below is already in there
		#data that is already used is queried with a get, data that may be new is added using a get_or_create query
		
		#Model
		name = data['model']
		#a model is identified by name and version.
		m, created = Model.objects.get_or_create(name=name)
		if created:
			self.print_message(V_NOISY, "Notice: created a new Model entry:%s"%(name))
		else:
			self.print_message(V_NOISY, "Notice: Model already exists:%s"%(name))

		#Algorithm
		name = data['algorithm']
		a = Algorithm.objects.get(name=name)

		#Tool
		name, version = data['tool']
		t = Tool.objects.get(name=name)

		#AlgorithmTool
		at = AlgorithmTool.objects.get(tool=t, algorithm=a, version=version)

		#Hardware
		hwdata = data['hardware']
		hardwarelist = []
		for tuple in hwdata:
			name, memory, cpu, disk_space, os = tuple
			if disk_space > 0:
				h, created = Hardware.objects.get_or_create(computername=name, memory=memory, cpu=cpu, kernelversion=os, defaults={'disk_space': disk_space})
				#if the DB did contain h but missed disk_space information:
				if not created and h.disk_space==0:
					h.disk_space = disk_space
					h.save()
			else:
				h, created = Hardware.objects.get_or_create(computername=name, memory=memory, cpu=cpu, kernelversion=os, defaults={'disk_space': 0})
			if created:
				self.print_message(V_NOISY, "Notice: created a new Hardware entry:%s"%(name))
			else:
				self.print_message(V_NOISY, "Notice: Hardware already exists:%s"%(name))
			hardwarelist.append(h)
		
		#Benchmark
		date, utime, stime, etime, tcount, scount, mVSIZE, mRSS, finished = data['benchmark']
		#convert these to Decimal explicitly
		utime = Decimal(utime)
		stime = Decimal(stime)
		etime = Decimal(etime)
		#now create and save the db object, uniquely identified by model, algorithm_tool and datetime of the run
		b, created = Benchmark.objects.get_or_create(model=m, algorithm_tool = at,
			date_time=date, 
			defaults={'user_time':utime, 'system_time':stime, 'elapsed_time':etime,
				'total_time':(utime+stime),
				'transition_count':tcount, 'states_count':scount, 'memory_VSIZE':mVSIZE,
				'memory_RSS':mRSS, 'finished':finished, 'logfile':None}
		)
		#connect the manytomany relations. this has to happen ONLY if newly created, or when we want to override existing data
		if created or self.override:
			if self.override:
				#delete and then create
				old_id = b.pk
				b.delete()
				b, created = Benchmark.objects.get_or_create(model=m, algorithm_tool = at,
					date_time=date, 
					defaults={'user_time':utime, 'system_time':stime, 'elapsed_time':etime,
						'total_time':(utime+stime),
						'transition_count':tcount, 'states_count':scount, 'memory_VSIZE':mVSIZE,
						'memory_RSS':mRSS, 'finished':finished, 'logfile':None}
				)
				self.print_message(V_VERBOSE, "Overridden a benchmark with ID: %s"%(old_id))
			
			self.print_message(V_NOISY,"Notice: created Benchmark entry: %s on %s, which ran on: %s"%(t.name, m.name, date))
			for hardware in hardwarelist:
				bh, c = BenchmarkHardware.objects.get_or_create(benchmark=b, hardware=hardware)

			#OptionValue
			optiondata = data['options']
			for tuple in optiondata:
				name, value = tuple
				o = Option.objects.get(name=name)
				ov, c = OptionValue.objects.get_or_create(option=o, value=value)
				if c:
					self.print_message(V_NOISY, "Notice: created a new OptionValue entry.")
				else:
					self.print_message(V_NOISY, "Notice: OptionValue already exists:%s, %s"%(name,value))
				bov, c = BenchmarkOptionValue.objects.get_or_create(optionvalue=ov,benchmark=b)
			
			#ExtraValues
			extravals=data['extravals']
			if not extravals:
				#nothing to see here, move along
				return (created, b)
			#create 'em
			for key in extravals:
				val=extravals[key]
				ev = ExtraValue(name=key, value=val, benchmark=b)
				ev.save()
			return (created, b)
		else:
			self.print_message(V_NOISY,"Notice: Benchmark already exists: %s on %s, which ran on: %s"%(t.name, m.name, date))
			#existing benchmark; don't modify
			return (created, b)
	#end of write_to_db

	def main(self, file_arg=None, verbosity=0):
		"""Main function for this app
		This just controls everything.
		If called by other apps rather than from the commandline, file_arg should contain a list of strings that contain a path to specify a file.
			See the python documentation for open() for more information.
		verbosity should only be set if debugging functionality is required (then, use verbosity=2)
			Arguments:
				verbosity		the level of verbosity
				file_arg		a list of files, indicated by their path as a string (usually absolute)
			Returns:
				the amount of logs that somehow failed
		"""
		if file_arg:
			#file_arg is specified, this is an external call and we should look for paths in file_arg
			self.verbose = verbosity
			file_list = file_arg
		else:
			#call from commandline, use parse_app_options()
			(options, args) = self.parse_app_options()
			self.verbose = options.verbose
			self.override = options.override
			self.use_dulwich = options.use_dulwich
			file_list = args

		#check if file(s) were provided
		if not file_list:
			if self.verbose:
				raise FileReaderError("Error: No file(s) provided.", debug_data=args)
			else:
				raise FileReaderError("Error: No file(s) provided.")
		
		if not self.verbose:
			self.verbose=V_QUIET
		
		self.print_message(V_VERBOSE, "Verbosity level: %s"%(self.verbose))
		
		runcounter = 0
		errorcounter = 0
		
		for f in file_list:
			runs_in_file=[]
			self.print_message(V_NOISY, "Notice: Reading from file: %s"%(f))
			
			#read the file, chopping it into seperate logs
			file = open(f, 'r')
			new_run=True
			j=0
			lines=[]
			for line in file:
				lines.append(line)
				if line.startswith("REPORT ENDS HERE"):
					#chop here
					j+=1
					new_run=True
				elif new_run:
					#new run, so we need to do some extra stuff
					runs_in_file.append([])
					runs_in_file[j].append(line)
					new_run=False
				else:
					#just another line of run j.
					runs_in_file[j].append(line)
			file.close()
			#iterate over these runs we've read
			for run in runs_in_file:
				#parse the whole thing
				data = self.parse(run)
				if data:
					#write to the database
					error=True
					created=False
					bench = None
					try:
						(created, bench)=self.write_to_db(data)
						if created:
							id=bench.pk
							log_file_path = self.write_to_log(run, "%d"%(id))
							bench.logfile="%s"%(log_file_path)
							bench.save()
						error = False
					#handle known error FileReaderError
					except FileReaderError as fre:
						#some known error occured, check how bad it is
						if fre.db_altered:
							#major panic!
							self.print_message(V_SILENT, "ERROR: an error occured while writing to the database! %s"%(fre.error))
							return -1
						else:
							#it's just an error in the write-process, or a failed check
							self.print_message(V_QUIET, "Error: FileReaderError: %s" %( fre.error))
							errorcounter+=1
						self.print_message(V_NOISY, "Details:%s"%( fre.debug_data))
					finally:
						if error:
							self.print_message(V_QUIET, "Note: Error writing to database from file %s"%(f))
						else:
							if created:
								if self.verbose==V_VERBOSE:
									self.print_message(V_VERBOSE, "Note: Added data to database, id: %s from file %s, with data\n %s"%(bench.pk, f, bench.get_print_data()))
								else:
									self.print_message(V_QUIET, "Note: Added data to database, id: %s from file %s"%(bench.pk, f))
							else:
								if self.verbose==V_VERBOSE:
									self.print_message(V_VERBOSE, "Note: Tried to data to database, but essential data already exists, id: %s from file %s, with data\n %s"%(bench.pk, f, bench.get_print_data()))
								else:
									self.print_message(V_QUIET, "Note: Tried to add data to database, already exists, id: %s from file %s"%(bench.pk, f))
				else:
					#there was no data returned while parsing
					self.print_message(V_VERBOSE, "Warning: no data, skipping run %s"%(runcounter))
					errorcounter+=1
				#next run
				runcounter+=1
			#next file
		#we're done! return how many errors we got
		return errorcounter
	#end of main

	def write_to_log(self, lines, filename):
		"""Saves the log contained in lines as a file specified by filename """
		# # # # # # # # # # # # seperate the header
		header_started = False
		i = 0
		done = False
		#iterate 'till we've seen the whole log or when the header ends
		while i < len(lines) and not done:
			if header_started:
				#we're reading the header, check for its end
				if not lines[i].startswith("END OF HEADER"):
					pass # a line of the header is seen
				else:
					done = True #stop
			#we're not at the header yet, keep reading 'till we find the start
			elif lines[i].startswith("BEGIN OF HEADER"):
				header_started = True
			#point to the next line
			i += 1
		
		#split the header off
		lines = lines[i:]
		header= lines[:i]

		f = os.path.join(LOGS_PATH, filename)
		fh = os.path.join(LOGS_PATH, filename + ".header")

		if self.use_dulwich:
			from beat.tools.logsave import create_log, __init_code__, GitFileError
			try:
				repo = __init_code__()
				create_log(repo, lines, f)
				create_log(repo, header, fh)
			except GitFileError as gfe:
				self.print_message(V_QUIET, "Failed to write log to git repository: %s", gfe.error)
		else:
			with open(f, 'wb') as file:
				for x in lines:
					file.write(x)
			with open(fh, 'wb') as file:
				for x in lines:
					file.write(x)
		return f


	def parse_app_options(self):
		"""Parse options for this script using python's optparse
		This will set verbose, print the --help message and read the arguments as per optparse.
		Three options are currently available:
		--quiet (verbosity errors only)
		--verbose (verbosity errors and warnings)
		--noisy (verbosity full)
		--override overrides data that already exists in the database
		"""
		parser = OptionParser()
		parser.add_option("--silent", 
			action="store_const", const=V_SILENT, dest = "verbose", help = "Print only dangerous errors (like database integrity warnings).")
		parser.add_option("-q", "--quiet",
			action="store_const", const=V_QUIET, dest="verbose", help = "Print default amount of messages; one per item under normal circumstances.")
		parser.add_option("-v", "--verbose",
			action="store_const", const=V_VERBOSE, dest="verbose", help = "Print additional (helpful) information, such as a summary of added data.")
		parser.add_option("--noisy",
			action="store_const", const=V_NOISY, dest="verbose", help = "Print as much as possible. Useful for debugging this script, not intended for other use.")
		parser.add_option("--override",
			action="store_const", const=True, dest="override", help = "Override existing data")
		parser.add_option("--dulwich",
			action="store_const", const=True, dest="use_dulwich", help = "Use this switch if logs are to be saved to a local git repository")
		return parser.parse_args()
	#end of parse_app_options
#end of FileReader

class FileReaderError(Exception):
	def __init__(self, error, db_altered=False, debug_data=None):
		self.error = error
		self.db_altered = db_altered
		self.debug_data = debug_data
	def __str__(self):
		if db_altered:
			if debug_data:
				return "Warning, the database was altered before this error was encountered.\n" + error + "\n" + debug_data
			else:
				return "Warning, the database was altered before this error was encountered.\n" + error
		else:
			if debug_data:
				return error +"\n"+debug_data
			else:
				return error
#end of FileReaderError


#run the main method
if __name__ == '__main__':
	f = FileReader()
	#f.main()
	exitcode = f.main()
	print "Saw %d error(s)." %exitcode
	if exitcode:
		sys.exit(1)
	else:
		sys.exit(0)
