"""
This script processes logs, using regular expressions that are in the database.
By convention, methods in this script will return None when (non-fatal or solvable) errors occur.
"""
#python libraries
import re		#regular expressions
import datetime	#for datetime objects
import sys		#for system calls
import os		#for os.path.split()
from optparse import OptionParser
#django exceptions
from django.core.exceptions import ObjectDoesNotExist, MultipleObjectsReturned
#models
from benchmarks.models import *

#the length of the header placed in the logs
RUN_DETAILS_HEADER = 11
#verbosity levels
V_NOISY = 2		#noisy:	as much as possible
V_VERBOSE = 1	#verbose:	everything except informative messages (which are preceded by "notice:")
V_QUIET = 0		#quiet:	errors only
V_SILENT = -1	#silent: 	only errors that are dangerous for the database integrity

class FileReader:
	#this variable will contain the log of the run of this filereader
	log = []
	#the verbosity level of this filereader. default is quiet.
	verbose = V_QUIET
	
	def print_message(self, level, text):
		"""Function to log, based on verbosity level
		Arguments:
			level		the level from which this message should be printed
			text		the message
		
		Both arguments are required.
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
		If the regex does not use groups (ie. the groupdict() method returns None), this method will return True on a match.
		In other words, the function returns whether the regex matches, and returns the dictionary, if any.
		Arguments:
			regex		a regular expression string( r'' )
			input		any string to be matched on
			flags		a value to be passed to re.compile(), defaults to None.
		
		regex and input are required arguments.
		Returns:
			On a match, a dictionary containing the named groups
				or a list if the regex does not use named groups
				or true if this dictionary is empty
			Otherwise, returns None.
		"""
		#compile the expression
		if flags:
			compiled = re.compile(regex, flags)
		else:
			compiled = re.compile(regex)
		#do a match
		match = compiled.match(input)
		if match:
			#there was a match, fetch the group dictionary
			list = match.groupdict()
			if not list:
				#the groups in the expression were not named, or there were no groups
				list = []
				i=0
				#read all the named groups
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
				#no groups: return True
				list = True
			return list
		else:
			#there was no match, something probably went wrong
			self.print_message(V_VERBOSE, "Warning: Regex  %s on input %s has an empty dictionary."%(regex, input))
			if flags:
				self.print_message(V_NOISY,"Notice: Flags argument to compiler: %s"%(flags))
			return None
	#end of match_regex
	
	def parse(self, lines):
		"""Parse a run from the specified lines.
		This method analyzes the log file of one run, including a header. The length of the header is specified by the RUN_DETAILS_HEADER constant.
			Arguments:
				lines		a list of strings, including newlines
			Returns:
				None when some (non-fatal) error occurs, or:
				A dictionary, as specified by parse_single_output.
		"""
		self.print_message(V_NOISY, "Notice: Reading run details and finding parser...")
		#read the header
		information = self.parse_run_details(lines)
		if not information:
			#something went wrong, skip ahead to the next run
			return None
		self.print_message(V_NOISY, "Notice: Complete!")
		
		#parse the log content, chopping off the header, and take along the header information
		data = self.parse_single_output(''.join(lines[RUN_DETAILS_HEADER:]), information)
		self.print_message(V_NOISY, "Notice: Read successful!")
		
		#return this log's information as a dictionary.
		return data
	#end of parse
	
	def parse_run_details(self, lines):
		"""Parses the header of a run from the lines specified
		The lines argument should contain strings, which must be at least RUN_DETAILS_HEADER long to ensure correctness.
		The newlines should remain in each of these strings.
			Arguments:
				lines		a list containing at least RUN_DETAILS_HEADER elements, which specify a header.
				
			Returns:
				None when some (non-fatal) error occurs, or:
				A dictionary, as follows:
					'parse_regex'		the regex to parse the log
					'model_name'		the name of the model
					'model_version' 	the version of the model
					'model_location'	the location of the model
					'tool_name'			the name of the tool
					'tool_version' 		the version of the tool
					'algorithm'			the name of the algorithm
					'hardware'			a list containing hardware platforms, specified as a tuple:
											(name, memory kb, processor, disk space, OS)
					'options'			a list of options, specified by a tuple:
											(name, value)
					'date'				the date this benchmark was run. see datetime.datetime in the python doc
		"""
		#match on this regular expression to fetch all the information
		regex = r'Nodename: (?P<name>.*)(\r\n|\n).*(\r\n|\n)OS: (?P<OS>.*)(\r\n|\n)Kernel-name: (?P<Kernel_n>.*)(\r\n|\n)Kernel-release: (?P<Kernel_r>.*)(\r\n|\n)Kernel-version: (?P<Kernel_v>.*)(\r\n|\n).*(\r\n|\n)Processor: (?P<processor>.*)(\r\n|\n)Memory-total: (?P<memory_kb>[0-9]+)(\r\n|\n)DateTime: (?P<datetime>.*)(\r\n|\n)Call: (?P<call>.*)(\r\n|\n)'
		m = self.match_regex(regex, ''.join(lines[:RUN_DETAILS_HEADER]), re.MULTILINE + re.DOTALL)
		#check for correctness
		if not m:
			#match_regex() returned None, so this header is incorrect.
			self.print_message(V_QUIET, "Error: header regex failed.")
			return None
		
		#deduce options, algorithm, tool from the call line
		tmp = self.parse_call(m['call'])
		if tmp:
			#unpack the tuple
			(parser, s, optlist, modelname) = tmp
		else:
			#tmp is none, so something went wrong in parse_call()
			return None
		#s[0] contains the whole call, s[1] contains the tool name and s[2] contains the algorithm name
		
		#fetch datetime info and create an object out of it
		dt = m['datetime'].split(' ')
		#don't put microseconds in the DB, the admin doesn't allow the user to enter them anyway
		dt = datetime.datetime(int(dt[0]), int(dt[1]), int(dt[2]), int(dt[3]), int(dt[4]), int(dt[5]))

		#the result of this function is a dictionary:
		result = {
			'parse_regex' : parser.regex,	#regular expression to be used to parse the log in question
			'model_name' : modelname,		#model name
			'model_version' : 1,				#version
			'model_location' : 'test.txt',		#and location
			'tool_name': s[1],				#tool name
			'tool_version': 1,					#version
			'algorithm': s[2],				#algorithm name
			'hardware': [(m['name'], m['memory_kb'], m['processor'], 0, m['OS']+" "+m['Kernel_n']+" "+m['Kernel_r']+" "+m['Kernel_v'])],
			'options': optlist,				#list of options as returned by parse_call()
			'date': dt,						#the datetime object specifying when the run took place
		}
		return result
	#end of parse_run_details
	
	#content should be the entire log as a string
	#run_details should be a dictionary containing the keys: model_name, model_version, model_location, tool_name, tool_version, hardware, options, date
	#regex should be the regular expression to extract data from content. The regex should contain the groups etime, utime, stime, tcount, scount, vsize, rss. 
	#	these are: elapsed, user, system times, state and transition count, memory vsize and memory rss
	#	only transition count may be left out.
	def parse_single_output(self, content, run_details):
		"""Parses information from the tool log.
		This method takes a log excluding header and a dictionary containing the information from the header.
		The log information and header information are merged into one result dictionary, which contain variables which correspond to entries in the database.
		This method will return None if something goes wrong.
			Arguments:
				content			the log contents as a string.
				run_details		the details for the run that generated this log, as returned by parse_run_details()
			Returns:
				A dictionary containing everything that needs to go into the database:
					'model'		a tuple:
									(name, version, location)
					'tool'		a tuple:
									(name, version)
					'algorithm' a string containing the algorithm name
					'hardware'	a list containing tuples as specified in run_details['hardware']
					'options'	a list containing tuples as specified in run_details['options']
					'benchmark'	a tuple:
									(datetime, etime, utime, stime, tcount, scount, vsize, rss, finished)
				or None if the regular expression (run_details['parse_regex']) does not match on the content.
		"""
		m = self.match_regex(run_details['parse_regex'], content, re.MULTILINE + re.DOTALL)
		self.print_message(V_NOISY, "Notice: regex match gives: %s"% (m))
		if m:
			#collect all relevant information into one dictionary
			match = {
				'model':(run_details.get('model_name'), run_details.get('model_version'), run_details.get('model_location')),
				'tool':(run_details.get('tool_name'), run_details.get('tool_version')),
				'algorithm':run_details.get('algorithm'),
				'hardware':run_details.get('hardware'),
				'options':run_details.get('options'),
				#this one should be re-written if we change the regexes to be identified by group numbers rather than group names
				'benchmark':(
						run_details.get('date'),m.get('etime'),m.get('utime'),m.get('stime'),
						m.get('tcount'),m.get('scount'),m.get('vsize'),m.get('rss'), not m.get('kill'))
			}
			#the following ensures 'hardware' and 'options' always contain something iteratable
			if not match['hardware']:
				match['hardware'] = []
			if not match['options']:
				match['options'] = []
			else:
				#here, ExtraValues can be parsed in a later version of this script
				pass
			self.print_message(V_NOISY, "Notice: resulting dictionary: %s"% (match))
			return match
		else:
			#the regex did not match, print an error and return None
			self.print_message(V_QUIET, "Error: Parse error. The input failed to match on the regex.")
			self.print_message(V_NOISY, "Notice: Details of error: %s\non\n%s"% (run_details['parse_regex'], content) )
			return None
	#end of parse_single_output
	
	def parse_call(self, call):
		"""Parses a call to an algorithm-tool
		A call, like "dve-reach -v --cache test.txt", is parsed by this method to provide all the useful information we can get from it.
			Arguments: 
				call		A string that shows how the run was executed
			Returns:
				A tuple, containing:
					a Regex object		which specifies how to parse this run
					a list				containing three elements; the call itself, the tool name and the algorithm name
					a list				of tuples: (option, value), as getopt.gnu_getopt() except options without value will appear with value True (as opposed to gnu_getopt, which would provide an empty string
					a string			containing the file name of the model
				or None, when the call cannot be parsed because the combination of tool and algorithm does not appear in the database.
		"""
		s = self.match_regex(r'^memtime (.*?)((?:2|-).*?)(?:$| .*$)', call)
		#s should be like: [call, toolname, algorithmname]
		if not s:
			#that's bad
			self.print_message(V_QUIET, "Error: invalid call in log: %s" %(call))
			return None

		#we don't know how to get the tool version yet, so we assume version = 1 for now
		try:
			t = Tool.objects.get(name=s[1], version=1)
			a = Algorithm.objects.get(name=s[2])
			at = AlgorithmTool.objects.get(tool=t, algorithm=a)
			shortopts = ''
			#long options
			opts = []
			#fetch all valid options for this tool+algorithm combo
			for o in ValidOption.objects.filter(algorithm_tool=at):
				opts.append(o.option.name)
			#find the appropriate short options
			for option in opts:
				o = Option.objects.get(name=option)
				try:
					rs = RegisteredShortcut.objects.get(algorithm_tool=at, option=o)
					shortopts+=rs.shortcut
				except:
					pass
		#handle database related errors
		except ObjectDoesNotExist:
			self.print_message(V_QUIET, "Error: unknown log: %s%s (version %s)" %(s[1], s[2], 1))
			return None
		except MultipleObjectsReturned:
			self.print_message(V_QUIET, "Error: multiple parsers for %s %s (version %s)" %(s[1], 1, s[2]))
			return None
		#translate all options unicode->ascii, ignoring unicode-only characters
		tmp = opts
		opts = []
		for i in tmp:
			i.encode('ascii', 'ignore')
		opts = tmp

		#read the options for the tool and convert them into a nice list
		#arguments are discarded for now (also, some of those might be bash-parsed and not passed to the algorithm_tool)
		import getopt
		optlist, args = getopt.gnu_getopt(call.split(" ")[2:], shortopts, opts)
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
				if not v:	#no parameter
					optlist[counter]=(rs.option.name, True)
			counter+=1
		self.print_message(V_NOISY, "read options and arguments, resulting in:\noptions:%s\nargs:%s"%(optlist,args))
		(head, tail) = os.path.split(args[0])
		#tail contains the filename of the model
		
		#return as the docstring describes
		return (at.regex, s, optlist, tail)
	#end of parse_call
	
	def check_data_validity(self, data):
		"""Checks the data validity.
		The data argument is one that is intended to be inserted in the database.
		This method should prevent incorrect or incomplete data from entering the database.
		The data argument may be updated to correct data, such as 'None' being provided to an integer field (this will become 0)
		If the verbosity is Verbose or higher, all applicable warnings will be produced before returning.
			Arguments:
				data		a dictionary, containing all the data about one run, as returned by parse_single_output()
			Returns:
				True when the data is sufficient
				False when something is incorrect (ie. missing data, negative numbers where they are not allowed, etc)
		"""
		#assume things are correct, then walk through the data based on the classes in models.py
		valid = True

		#Model
		name, version, location = data['model']
		if not name or not version or not location:
			self.print_message(V_VERBOSE, "Warning: Data invalid. Model.name=%s Model.version=%s Model.location=%s"%(name, version,location))
			valid=False

		#Algorithm
		name = data['algorithm']
		try:
			a = Algorithm.objects.get(name=name)
		except (MultipleObjectsReturned, ObjectDoesNotExist) as e:
			self.print_message(V_VERBOSE, "Warning: %s"%(e))
			valid=False

		#Tool
		name, version = data['tool']
		try:
			t = Tool.objects.get(name=name, version=version)
		except (MultipleObjectsReturned, ObjectDoesNotExist) as e:
			self.print_message(V_VERBOSE, "Warning: %s"%(e))
			valid = False

		#Hardware
		hwdata = data['hardware']
		for tuple in hwdata:
			name, memory, cpu, disk_space, os = tuple
			#memory may not be zero, disk_space may be.
			if not name or memory <=0 or not cpu or disk_space <0 or not os:
				self.print_message(V_VERBOSE, "Warning: Data invalid. HW.name=%s HW.memory=%s HW.cpu=%s HW.disk_space=%s HW.os=%s" %(name, memory, cpu, disk_space, os))
				valid=False
		
		#Option
		optiondata = data['options']
		for tuple in optiondata:
			name, value = tuple
			if not name or not value:
				self.print_message(V_VERBOSE, "Warning: invalid option: name=<%>s value=<%s>"%(name,value))
				valid=False
			try:
				o = Option.objects.get(name=name)
			except (MultipleObjectsReturned, ObjectDoesNotExist) as e:
				self.print_message(V_VERBOSE, "Warning: Django error: %s"%(e))
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
				self.print_message(V_VERBOSE, "Warning: invalid value in benchmark %s"% ((date, utime, stime, etime, tcount, scount, mVSIZE, mRSS)))
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
		
		#Model
		name, version, location = data['model']
		#a model is identified by name and version.
		m, created = Model.objects.get_or_create(name=name, version=version, defaults={'location': location})
		if created:
			self.print_message(V_NOISY, "Notice: created a new Model entry:%s, %s"%(name,version))
		else:
			self.print_message(V_NOISY, "Notice: Model already exists:%s, %s"%(name,version))

		#Algorithm
		name = data['algorithm']
		#an algorithm only has a name
		a = Algorithm.objects.get(name=name)

		#Tool
		name, version = data['tool']
		#a tool has a name and version
		t = Tool.objects.get(name=name, version=version)

		#Hardware
		hwdata = data['hardware']
		hardwarelist = []
		for tuple in hwdata:
			name, memory, cpu, disk_space, os = tuple
			if disk_space > 0:
				h, created = Hardware.objects.get_or_create(name=name, memory=memory, cpu=cpu, os=os, defaults={'disk_space': disk_space})
				#if the DB did contain h but missed disk_space information:
				if not created and h.disk_space==0:
					h.disk_space = disk_space
					h.save()
			else:
				h, created = Hardware.objects.get_or_create(name=name, memory=memory, cpu=cpu, os=os, defaults={'disk_space': 0})
			if created:
				self.print_message(V_NOISY, "Notice: created a new Hardware entry:%s"%(name))
			else:
				self.print_message(V_NOISY, "Notice: Hardware already exists:%s"%(name))
			hardwarelist.append(h)
		
		#Benchmark
		date, utime, stime, etime, tcount, scount, mVSIZE, mRSS, finished = data['benchmark']
		#convert these to float explicitly
		utime = float(utime)
		stime = float(stime)
		etime = float(etime)
		#now create and save the db object
		b, created = Benchmark.objects.get_or_create(model=m, tool=t, algorithm=a, date_time=date, 
			defaults={'user_time':utime, 'system_time':stime, 'elapsed_time':etime,
				'total_time':(utime+stime),
				'transition_count':tcount, 'states_count':scount, 'memory_VSIZE':mVSIZE,
				'memory_RSS':mRSS, 'finished':finished}
		)
		#connect the manytomany relations. this has to happen ONLY if newly created
		if created:
			self.print_message(V_NOISY,"Notice: created Benchmark entry: %s on %s, which ran on: %s"%(t.name, m.name, date))
			for hardware in hardwarelist:
				bh, c = BenchmarkHardware.objects.get_or_create(benchmark=b, hardware=hardware)

			#OptionValue
			optiondata = data['options']
			for tuple in optiondata:
				name, value = tuple
				o = Option.objects.get(name=name)
				ov, created = OptionValue.objects.get_or_create(option=o, value=value)
				if created:
					self.print_message(V_VERBOSE, "Notice: created a new OptionValue entry.")
				else:
					self.print_message(V_VERBOSE, "Notice: OptionValue already exists:%s, %s"%(name,value))
				bov, c = BenchmarkOptionValue.objects.get_or_create(optionvalue=ov,benchmark=b)

		else:
			self.print_message(V_NOISY,"Notice: Benchmark already exists: %s on %s, which ran on: %s"%(t.name, m.name, date))
			print "return None"
			#existing benchmark; don't modify
			return None
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
			file_list = args
		#check if file(s) were provided
		if not file_list:
			if self.verbose:
				raise FileReaderError("Error: No file(s) provided.", debug_data=args)
			else:
				raise FileReaderError("Error: No file(s) provided.")
		self.print_message(V_VERBOSE, "Verbosity level: %s"%(self.verbose))
		
		all_data=[]
		#read all files into all_data, each file in a seperate list of strings
		for path in file_list:
			lines=[]
			self.print_message(V_NOISY, "Notice: Reading from file: %s"%(path))
			with open(path, 'r') as file:
				for line in file:
					lines.append(line)
			all_data.append(lines)
			self.process(all_data)
			all_data=[]
		
		"""
		self.print_message(V_NOISY, "Notice: Read complete\nNotice: Start parsing")
		
		runcounter=0
		errorcounter=0
		#for each group of lines, ie. each parsed file:
		for lines in all_data:
			runs = self.find_runs(lines)
			#split logs in a file
			for run in runs:
				data = self.parse(run)
				#check if something was returned
				if data:
					#write to the database
					try:
						self.write_to_db(data)
					except FileReaderError as f:
						#some known error occured, check how bad it is
						if f.db_altered:
							#major panic!
							self.print_message(V_SILENT, "ERROR: an error occured while writing to the database! %s"%(f.error))
							return -1
						else:
							#it's just an error in the write-process, or a faileld check
							self.print_message(V_QUIET, "Error: FileReaderError: %s" %( f.error))
							errorcounter+=1
						self.print_message(V_NOISY, "Details:%s"%( f.debug_data))
					except Exception, e:
						#an unknown error occured, skip this part
						self.print_message(V_QUIET, "Error: parsing of run %s failed by unexpected error: %s"%(runcounter, e))
						errorcounter+=1
				else:
					self.print_message(V_VERBOSE, "Warning: no data, skipping run %s"%(runcounter))
					errorcounter+=1
				runcounter+=1
		#end of file-reading
		"""
		errorcounter=0
		return errorcounter
	#end of main
	
	def process(self, all_data):
		self.print_message(V_NOISY, "Notice: Read complete\nNotice: Start parsing")
		
		runcounter=0
		errorcounter=0
		#for each group of lines, ie. each parsed file:
		for lines in all_data:
			runs = self.find_runs(lines)
			#split logs in a file
			for run in runs:
				data = self.parse(run)
				#check if something was returned
				if data:
					#write to the database
					try:
						self.write_to_db(data)
					except FileReaderError as f:
						#some known error occured, check how bad it is
						if f.db_altered:
							#major panic!
							self.print_message(V_SILENT, "ERROR: an error occured while writing to the database! %s"%(f.error))
							return -1
						else:
							#it's just an error in the write-process, or a faileld check
							self.print_message(V_QUIET, "Error: FileReaderError: %s" %( f.error))
							errorcounter+=1
						self.print_message(V_NOISY, "Details:%s"%( f.debug_data))
					except Exception, e:
						#an unknown error occured, skip this part
						self.print_message(V_QUIET, "Error: parsing of run %s failed by unexpected error: %s"%(runcounter, e))
						errorcounter+=1
				else:
					self.print_message(V_VERBOSE, "Warning: no data, skipping run %s"%(runcounter))
					errorcounter+=1
				runcounter+=1

	def find_runs(self, lines):
		"""Splits the argument into a list of runs
		This function will return a list of lists, each containing a complete run.
		The last item is an empty string if the file is correctly formatted
		"""
		runs = []
		j=0
		new_run = True
		for line in lines:
			if line.startswith("REPORT ENDS HERE"):
				#chop here
				j+=1
				new_run=True
			elif new_run:
				#new run, so we need to do some extra stuff
				runs.append([])
				runs[j].append(line)
				new_run=False
			else:
				#just another line of run j.
				runs[j].append(line)
		return runs
	#end of find_runs
	
	def parse_app_options(self):
		"""Parse options for this script using python's optparse
		This will set verbose, print the --help message and read the arguments as per optparse.
		Three options are currently available:
		--quiet (verbosity errors only)
		--verbose (verbosity errors and warnings)
		--noisy (verbosity full)
		"""
		parser = OptionParser()
		parser.add_option("--silent", 
			action="store_const", const=V_SILENT, dest = "verbose", help = "Print only dangerous errors (like database integrity warnings).")
		parser.add_option("-q", "--quiet",
			action="store_const", const=V_QUIET, dest="verbose", help = "Only print errors and bad warnings.")
		parser.add_option("-v", "--verbose",
			action="store_const", const=V_VERBOSE, dest="verbose", help = "Print helpful things.")
		parser.add_option("--noisy",
			action="store_const", const=V_NOISY, dest="verbose", help = "Print everything.")
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
	exitcode = f.main()
	#print "%s\nLog: "%( exitcode)
	for l in f.log:
		print l
	sys.exit(exitcode)
