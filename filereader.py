"""
This file reader is just an initial version.
Hopefully, the intermediate format will be implemented, which makes the process of parsing a lot easier.
For now, only nips2lts-grey and nips2lts-grey that writes to a .dir output file are supported.
Hardware, Options, timestamp and other stuff that is to be taken from the (not yet approved) commandline script is still missing.
"""
#imports of python-libs
import re
import datetime
import sys
import os
from optparse import OptionParser
#imports of code we wrote
from benchmarks.models import *
from parsers import *

RUN_DETAILS_HEADER = 11
V_NOISY = 2
V_VERBOSE = 1
V_QUIET = 0
V_SILENT = -1

class FileReader:
	verbose = V_QUIET #default mode: no messages except errors
	
	def print_message(self, level, text):
		"""Function to print, based on verbosity level
		Arguments:
			level		the level from which this message should be printed
			text		the message
		
		Both arguments are required.
		Returns:
			This function returns nothing.
		"""
		if self.verbose >= level:
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
			On a match, a dictionary, or true if this dictionary is empty.
			Otherwise, returns None.
		"""
		#compile
		if flags:
			compiled = re.compile(regex, flags)
		else:
			compiled = re.compile(regex)
		match = compiled.match(input)
		if match:
			list = match.groupdict()
			if not list:
				#no groups
				list = True
			return list
		else:
			self.print_message(V_VERBOSE, "Warning: Regex  %s on input %s has an empty dictionary."%(regex, input))
			if flags:
				self.print_message(V_NOISY,"\tFlags argument to compiler: %s"%(flags))
		return None
	#end of match_regex
	
	def get_lines(self, file):
		"""This function simply reads all lines from the specified file."""
		lines = []
		line = None
		loop_end = False
		while not loop_end:
			if line:
				lines.append(line)
			try:
				line = file.next()
			except StopIteration:
				self.print_message(V_NOISY, "Notice: end of file encountered")
				loop_end = True
		return lines
	#end of get_lines

	def parse(self, lines):
		"""Parse runs from the specified lines.
		Arguments:
			lines		a list of strings, including newlines
		
		Returns:
			None when some (non-fatal) error occurs, or:
			A dictionary, as specified by parse_single_output.
		"""
		self.print_message(V_NOISY, "Notice: Reading run details...")
		#read the run information
		tmp = self.parse_run_details(lines)
		if tmp:
			information = tmp
		else:
			#something went wrong, skip ahead to the next run
			return None
		self.print_message(V_NOISY, "Notice: Complete!\nNotice: Finding parser...")
		#find the parse_tuple
		parse_info = information['parse_tuple']
		self.print_message(V_NOISY, "Notice: Found parser!")
		#grab te regex that we'll parse
		regex = parse_info[2]	#expression to parse
		
		self.print_message(V_NOISY, "Notice: Option(s) are: %s\nNotice: Regex is: %s\nNotice: Reading data..." %(information['options'], regex))
		
		#parse the log content
		data = self.parse_single_output(''.join(lines[RUN_DETAILS_HEADER:]), information, regex)
		self.print_message(V_NOISY, "Notice: Read successful!")
		
		return data
	#end of parse
	
	def parse_run_details(self, lines):
		"""Parses the header of a run from the lines specified
		Arguments:
			lines		a list containing at least RUN_DETAILS_HEADER elements, which specify a header.
			
		Returns:
			None when some (non-fatal) error occurs, or:
			A dictionary, as follows:
				'parse_tuple'		the tuple that contains information for parsing, like elements of pattern_list
				'model_name'		the name of the model
				'model_version' 	the version of the model
				'model_location'	the location of the model
				'tool_name'			the name of the tool
				'tool_version' 		the version of the tool
				'hardware'			a list containing hardware platforms, specified as a tuple:
										(name, memory kb, processor, disk space, OS)
				'options'			a list of options, specified by a tuple:
										(name, value)
				'date'				the date this benchmark was run. see datetime.datetime in the python doc
		"""
		regex = r'Nodename: (?P<name>.*)\n.*\nOS: (?P<OS>.*)\nKernel-name: (?P<Kernel_n>.*)\nKernel-release: (?P<Kernel_r>.*)\nKernel-version: (?P<Kernel_v>.*)\n.*\nProcessor: (?P<processor>.*)\nMemory-total: (?P<memory_kb>[0-9]+)\nDateTime: (?P<datetime>.*)\nCall: (?P<call>.*)\n'
		m = self.match_regex(regex, ''.join(lines[:RUN_DETAILS_HEADER]), re.MULTILINE + re.DOTALL)
		call = m['call'].split(' ')
		if call[0] == 'memtime':
			s = self.get_parser(call[1])
			call = call[2:]
		else:
			s = self.get_parser(call[0])
			call = call[1:]
		if not s:
			#get_parser returned None
			return None
		#s will look like this from here: (tool, algorithm, regex, opt, longopt)
		
		#fetch datetime info and create an object out of it
		dt = m['datetime'].split(' ')
		dt = datetime.datetime(int(dt[0]), int(dt[1]), int(dt[2]), int(dt[3]), int(dt[4]), int(dt[5]), int(dt[6]))
		
		#read the options/args for the tool and convert them into a nice list
		import getopt
		if s[4]:
			optlist, args = getopt.gnu_getopt(call, s[3], s[4])
		else:
			optlist, args = getopt.gnu_getopt(call, s[3])
		counter = 0
		for t in optlist:
			o, v = t
			if not v:	#no parameter
				optlist[counter]=(o,True)
			counter+=1
		self.print_message(V_NOISY, "read options and arguments, resulting in:\noptions:%s\nargs:%s"%(optlist,args))
		optlist.append(('algorithm', s[1]))
		(head, tail) = os.path.split(args[0])
		#tail contains the filename of the model
		
		result = {
			'parse_tuple' : s,
			'model_name' : tail,
			'model_version' : 1,
			'model_location' : 'test.txt',
			'tool_name': s[0],
			'tool_version': 1,
			'hardware': [(m['name'], m['memory_kb'], m['processor'], 0, m['OS']+" "+m['Kernel_n']+" "+m['Kernel_r']+" "+m['Kernel_v'])],
			'options': optlist,
			'date': dt,
		}
		return result
		#this will return a tuple containing the run details as a dictionary and the line on which the tool log begins as an int(in that order).
	#end of parse_options
	
	#content should be the entire log as a string
	#run_details should be a dictionary containing the keys: model_name, model_version, model_location, tool_name, tool_version, hardware, options, date
	#regex should be the regular expression to extract data from content. The regex should contain the groups etime, utime, stime, tcount, scount, vsize, rss. 
	#	these are: elapsed, user, system times, state and transition count, memory vsize and memory rss
	#	only transition count may be left out.
	def parse_single_output(self, content, run_details, regex):
		"""Parses informations from the tool log.
		Arguments:
			content			the log contents as a string.
			run_details		the details for the run that generated this log, as returned by parse_run_details()
			regex			the regular expression that can be used to parse this log
		Returns:
			A dictionary containing everything that needs to go into the database:
				'model'		a tuple:
								(name, version, location)
				'tool'		a tuple:
								(name, version)
				'hardware'	a list containing tuples as specified in run_details['hardware']
				'options'	a list containing tuples as specified in run_details['options']
				'benchmark'	a tuple:
								(datetime, etime, utime, stime, tcount, scount, vsize, rss)
		"""
		m = self.match_regex(regex, content, re.MULTILINE + re.DOTALL)
		self.print_message(V_NOISY, "Notice: regex match gives: %s"% (m))
		if m:
			match = {
				'model':(run_details.get('model_name'), run_details.get('model_version'), run_details.get('model_location')),
				'tool':(run_details.get('tool_name'), run_details.get('tool_version')),
				'hardware':run_details.get('hardware'),
				'options':run_details.get('options'),
				'benchmark':(run_details.get('date'),m['etime'],m['utime'],m['stime'],m.get('tcount'),m['scount'],m['vsize'],m['rss']),
			}
			#the following ensures 'hardware' and 'options' always contain something iteratable
			if not match['hardware']:
				match['hardware'] = []
			if not match['options']:
				match['options'] = []
		else:
			self.print_message(V_QUIET, "Warning: Parse error. The input failed to match on the regex.")
		self.print_message(V_NOISY, "Notice: resulting dictionary: %s"% (match))
		return match

	def get_parser(self, content):
		self.print_message(V_NOISY, "Notice: %s is the parser, according to the file."%(content))
		for tuple in self.pattern_list:
			if tuple[0] == content:
				return tuple[1]
		self.print_message(V_SILENT, "Error: Unknown run type. Skipping.")
		return None
	#end of get_parser
	
	def check_data_validity(self, data):
		valid = True
		#Model
		name, version, location = data['model']
		if not name or not version or not location:
			self.print_message(V_VERBOSE, "Warning: Data invalid. Model.name=%s Model.version=%s Model.location=%s"%(name, version,location))
			valid=False
		#Tool
		name, version = data['tool']
		if not name or not version:
			self.print_message(V_VERBOSE, "Warning: Data invalid. Tool.name=%s Tool.version=%s"%(name, version))
			valid=False
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
				self.print_message(V_VERBOSE, "Warning: invalid option: name=%s value=%s"%(name,value))
				valid=False
		#Benchmark
		date, utime, stime, etime, tcount, scount, mVSIZE, mRSS = data['benchmark']
		if not date or utime <0 or stime <0 or etime <0 or tcount <0 or scount <0 or mVSIZE <0 or mRSS <0:
			if not tcount or tcount == -1:
				#tcount can be undefined, but may be zero.
				tcount = 0
				data['benchmark'] = (date, utime, stime, etime, tcount, scount, mVSIZE, mRSS)
			else:
				self.print_message(V_VERBOSE, "Warning: invalid value in benchmark %s"% ((date, utime, stime, etime, tcount, scount, mVSIZE, mRSS)))
				valid=False
		return (valid, data)
	#end of check_data_validity
	
	def write_to_db(self, data):
		#check the data
		valid, data = self.check_data_validity(data)
		if not valid:
			if self.verbose:
				raise FileReaderError("Error: some invalid data provided.", debug_data=data)
			else:
				raise FileReaderError("Error: some invalid data provided.")
		else:
			self.print_message(V_NOISY, "Notice: Validity checked and passed, writing to DB...")
		#model entry
		name, version, location = data['model']
		#a model is identified by name and version.
		m, created = Model.objects.get_or_create(name=name, version=version, defaults={'location': location})
		if created:
			self.print_message(V_NOISY, "Notice: created a new Model entry:%s,%s"%(name,version))
		
		#tool entry
		name, version = data['tool']
		t, created = Tool.objects.get_or_create(name=name, version=version)
		if created:
			self.print_message(V_NOISY, "Notice: created a new Tool entry:%s,%s"%(name,version))
		
		#hardware entries
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
				self.print_message(V_VERBOSE, "Notice: created a new Hardware entry:%s"%(name))
			hardwarelist.append(h)
		
		#option entries
		optiondata = data['options']
		optionlist = []
		for tuple in optiondata:
			name, value = tuple
			o, created = Option.objects.get_or_create(name=name, value=value)
			if created and self.verbose>1:
				self.print_message(V_VERBOSE, "Notice: created a new Option entry:%s,%s"%(name,value))
			optionlist.append(o)
		
		#this one's always new
		#add BenchmarkHardware and BenchmarkOption reference here
		date, utime, stime, etime, tcount, scount, mVSIZE, mRSS = data['benchmark']

		#now create and save the db object
		b = Benchmark(model=m, tool=t, date_time=date, user_time=utime, system_time=stime, elapsed_time=etime, transition_count=tcount, states_count=scount, memory_VSIZE=mVSIZE, memory_RSS=mRSS)
		b.save()
		#connect the manytomany relations. this has to happen AFTER calling save on the benchmark.
		for option in optionlist:
			bo = BenchmarkOption(benchmark=b, option=option)
			bo.save()
		for hardware in hardwarelist:
			bh = BenchmarkHardware(benchmark=b, hardware=hardware)
			bh.save()
		b.save()
		#code below is still broken!
		#b, created = Benchmark.objects.get_or_create(model=m, tool=t, date_time=date, 
		#	defaults={'user_time':utime, 'system_time':stime, 'elapsed_time':etime,
		#		'transition_count':tcount, 'states_count':scount, 'memory_VSIZE':mVSIZE,
		#		'memory_RSS':mRSS, 'finished':True})

		#connect the manytomany relations. this has to happen AFTER calling save on the benchmark. and only if newly created
		#if created:
		#	self.print_message(V_NOISY,"Notice: created Benchmark entry: %s"%(b))
		#	for option in optionlist:
		#		bo = BenchmarkOption(benchmark=b, option=option)
		#		bo.save()
		#	for hardware in hardwarelist:
		#		bh = BenchmarkHardware(benchmark=b, hardware=hardware)
		#		bh.save()
		#	b.save()
		#done!
	#end of write_to_db

	def main(self, file_arg=None, verbosity=0):
		"""Main function for this app
		This just controls everything.
		If called by other apps rather than from the commandline, file_arg should contain a list of strings that contain a path to specify a file.
				See the python documentation for open() for more information.
			verbosity should only be set if debugging functionality is required (then, use verbosity=2)
		"""
		#if file_arg is specified, this is an external call and we should look for paths there
		if file_arg:
			self.verbose = verbosity
			file_list = file_arg
		#else, just use the parse_app_options function
		else:
			(options, args) = self.parse_app_options()
			self.verbose = options.verbose
			file_list = args
		if not file_list:
			if self.verbose:
				raise FileReaderError("Error: No file provided.", debug_data=args)
			else:
				raise FileReaderError("Error: No file provided.")
		self.print_message(V_VERBOSE, "Verbosity level: %s"%(self.verbose))

		#fetch the patterns from the external file
		execute(self)
		self.print_message(V_NOISY, "Notice: the user-provided pattern list is: %s"% (self.pattern_list))

		#start of file-reading
		#when we want multiple files, a loop should be here
		path = file_list[0]
		self.print_message(V_NOISY, "Notice: Reading from file: %s"%(path))
		lines=[]
		with open(path, 'r') as file:
			for line in file:
				lines.append(line)
		self.print_message(V_NOISY, "Notice: Read complete\nNotice: Start parsing")
		#figure out the runs that are in here
		runs = self.find_runs(lines)
		runcounter=0
		errorcounter=0
		#parse each:
		for run in runs:
			data = self.parse(run)
			if data:
				try:
					self.write_to_db(data)
				except FileReaderError as f:
					if f.db_altered:
						self.print_message(V_SILENT, "Warning: an error occured while writing to the database! %s"%(f.error))
						return -1
					else:
						self.print_message(V_QUIET, "Warning: FileReaderError: %s" %( f.error))
						errorcounter+=1
					self.print_message(V_NOISY, "Details:%s"%( f.debug_data))
				except Exception, e:
					#an error occured, skip this part
					self.print_message(V_QUIET, "Warning: parsing of run %s failed"%(runcounter))
					print e
					errorcounter+=1
			else:
				self.print_message(V_VERBOSE, "Warning: no data, skipping run %s"%(runcounter))
				errorcounter+=1
			runcounter+=1
		#end of file-reading
		return errorcounter
	#end of main
	
	def find_runs(self, lines):
		"""Splits the argument on runs
		This function will return a list of lists, each containing a complete run.
		The last item is an empty string if the file is correctly formatted
		"""
		runs = []
		j=0
		new_run = True
		for line in lines:
			if line.startswith("REPORT ENDS HERE"):
				j+=1
				new_run=True
			elif new_run:
				runs.append([])
				runs[j].append(line)
				new_run=False
			else:
				runs[j].append(line)
		return runs
	#end of find_runs
	
	def parse_app_options(self):
		"""Parse options using python's optparse
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
	
	pattern_list = []
	
	def patterns(self, *args):
		for tuple in args:
			identification, tool, algorithm, regex, opt, longopt = tuple
			self.pattern_list.append((identification, (tool, algorithm, regex, opt, longopt)))
		return self.pattern_list
	#end of patterns
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
	exitcode = FileReader.main(FileReader())
	print exitcode
	sys.exit(exitcode)