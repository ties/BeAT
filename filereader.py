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
from optparse import OptionParser
#imports of code we wrote
from benchmarks.models import *
from parsers import *

RUN_DETAILS_HEADER = 11

class FileReader:
	verbose = 0 #default: no messages except errors
	#def __init__(self):
	#	contructor
	def match_regex(self, regex, input, flags=None):
		"""
		This function compiles (with flags, if given) and matches the regex on the input.
		If the regex does not use groups (ie. the groupdict() method returns None), this method will return True.
		In other words, the function returns whether the regex matches, and if it does, returns the dictionary.
		This works because a non-empty dictionary evaluates to true.
		The disable_verbose option allows the caller to explicitly disable verbose output.
		
		regex should be a regular expression string( r'' )
		input should be any string
		flags will be passed directly to the regex compiler
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
		elif self.verbose:
			print "Warning: Regex ", regex, " on input ", input, "has an empty dictionary."
			if flags:
				print "\tFlags argument to compiler: ", flags
		return None
	#end of match_regex
	
	def get_lines(self, file):
		"This function simply reads all lines from the file in question."
		lines = []
		line = None
		loop_end = False
		while not loop_end:
			if line:
				lines.append(line)
			try:
				line = file.next()
			except StopIteration:
				if self.verbose>1:
					print "Notice: end of file encountered"
				loop_end = True
		return lines
	#end of get_lines

	def parse(self, lines):
		if self.verbose>1:
			print "Notice: Reading run details..."
		#read the run information
		information, start = self.parse_run_details(lines)
		if self.verbose>1:
			print "Notice: Complete!"
			print "Notice: Finding parser..."
		#find the parse_tuple
		parse_info = information['parse_tuple']
		if self.verbose>1:
			print "Notice: Found parser!"
		#grab te regex that we'll parse
		regex = parse_info[3]	#expression to parse
		
		if self.verbose>1:
			print "Notice: Option(s) are:",information['options']
			print "Notice: Regex is:",regex
			print "Notice: Reading data..."
		#parse the log content
		data = self.parse_single_output(''.join(lines[RUN_DETAILS_HEADER:]), information, regex)
		if self.verbose>1:
			print "Notice: Read successful!"
		return data
	#end of parse
	
	def parse_run_details(self, lines):
		#datetime still missing
		regex = r'Nodename: (?P<name>.*)\n.*\nOS: (?P<OS>.*)\nKernel-name: (?P<Kernel_n>.*)\nKernel-release: (?P<Kernel_r>.*)\nKernel-version: (?P<Kernel_v>.*)\n.*\nProcessor: (?P<processor>.*)\nMemory-total: (?P<memory_kb>[0-9]+)\nDateTime: (?P<datetime>.*)\nCall: (?P<call>.*)\n'
		m = self.match_regex(regex, ''.join(lines[:RUN_DETAILS_HEADER]), re.MULTILINE + re.DOTALL)
		call = m['call'].split(' ')
		if call[0] == 'memtime':
			s = self.get_parser(call[1])
		else:
			s = self.get_parser(call[0])
		
		#fetch datetime info and create an object out of it
		dt = m['datetime'].split(' ')
		dt = datetime.datetime(int(dt[0]), int(dt[1]), int(dt[2]), int(dt[3]), int(dt[4]), int(dt[5]), int(dt[6]))
		
		result = ({
			'parse_tuple' : s,
			'model_name' : "test",
			'model_version' : 1,
			'model_location' : 'test.txt',
			'tool_name': s[0],
			'tool_version': 1,
			'hardware': [(m['name'], m['memory_kb'], m['processor'], 0, m['OS']+" "+m['Kernel_n']+" "+m['Kernel_r']+" "+m['Kernel_v'])],
			'options': [('algorithm', s[1])],
			'date': dt,
		}, 9)
		#copy over the other options:
		for x in s[2]:
			result['options'].append((x, s[2][x]))
		return result
		#this will return a tuple containing the run details as a dictionary and the line on which the tool log begins as an int(in that order).
	#end of parse_options
	
	#content should be the entire log as a string
	#run_details should be a dictionary containing the keys: model_name, model_version, model_location, tool_name, tool_version, hardware, options, date
	#regex should be the regular expression to extract data from content. The regex should contain the groups etime, utime, stime, tcount, scount, vsize, rss. 
	#	these are: elapsed, user, system times, state and transition count, memory vsize and memory rss
	#	only transition count may be left out.
	def parse_single_output(self, content, run_details, regex):
		m = self.match_regex(regex, content, re.MULTILINE + re.DOTALL)
		if self.verbose>1:
			print "Notice: regex match gives: ", m
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
		elif self.verbose:
			print "Warning: Parse error. The input failed to match on the regex."
		if self.verbose>1:
			print "Notice: resulting dictionary: ", match
		return match

	def get_parser(self, content):
		if self.verbose>1:
			print "Notice: " + content + " is the parser, according to the file."
		for tuple in self.pattern_list:
			if tuple[0] == content:
				return tuple[1]
		print "Error: parsing of the data in the specified file is not yet supported."
		exit()
	#end of get_parser
	
	def check_data_validity(self, data):
		valid = True
		#Model
		name, version, location = data['model']
		if not name or not version or not location:
			if self.verbose:
				print "Warning: Data may be wrong: Model.name=",name,"Model.version=",version,"Model.location=",location
			valid=False
		#Tool
		name, version = data['tool']
		if not name or not version:
			if self.verbose:
				print "Warning: Data may be invalid: Tool.name=",name,"Tool.version=",version
			valid=False
			#name or version invalid -> raise an error
		#Hardware
		hwdata = data['hardware']
		for tuple in hwdata:
			name, memory, cpu, disk_space, os = tuple
			if not name or memory <0 or not cpu or disk_space <0 or not os:
				if self.verbose:
					print "Warning: Data may be invalid: HW.name=",name,"HW.memory=",memory,"HW.cpu",cpu,"HW.disk_space",disk_space,"HW.os",os
				valid=False
				#name, memory, cpu or os invalid -> raise error (or continue?)
			#disk_space invalid -> don't set
		#Option
		optiondata = data['options']
		for tuple in optiondata:
			name, value = tuple
			if not name or not value:
				if self.verbose:
					print "Warning: invalid option: name",name,"value",value
				valid=False
		#Benchmark
		date, utime, stime, etime, tcount, scount, mVSIZE, mRSS = data['benchmark']
		if date == -1 or utime <0 or stime <0 or etime <0 or tcount <0 or scount <0 or mVSIZE <0 or mRSS <0:
			if tcount == -1:
				#tcount can be undefined.
				tcount = None
				data['benchmark'] = (date, utime, stime, etime, tcount, scount, mVSIZE, mRSS)
			else:
				if self.verbose:
					print "Warning: invalid value in benchmark"
				#raise an error?
				valid=False
		return (valid, data)
	#end of check_data_validity
	
	def write_to_db(self, data):
		#check the data
		valid, data = self.check_data_validity(data)
		if not valid:
			print "Error: invalid data."
			if self.verbose>=1:
				print "Notice: the data: ", data
			exit()
		elif self.verbose>1:
			print "Notice: Validity checked and passed, writing to DB..."
		#model entry
		name, version, location = data['model']
		#a model is identified by name and version.
		m, created = Model.objects.get_or_create(name=name, version=version, defaults={'location': location})
		if created and verbose>1:
			print "Notice: created a new Model entry"
		
		#tool entry
		name, version = data['tool']
		t, created = Tool.objects.get_or_create(name=name, version=version)
		if created and verbose>1:
			print "Notice: created a new Tool entry"
		
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
				if created and verbose>1:
					print "Notice: created a new Hardware entry"
			else:
				h, created = Hardware.objects.get_or_create(name=name, memory=memory, cpu=cpu, os=os, defaults={'disk_space': 0})
				if created and verbose>1:
					print "Notice: created a new Hardware entry"
			hardwarelist.append(h)
		
		#option entries
		optiondata = data['options']
		optionlist = []
		for tuple in optiondata:
			name, value = tuple
			if not name or not value:
				if self.verbose:
					print "Warning: invalid option: name",name,"value",value
			o, created = Option.objects.get_or_create(name=name, value=value)
			if created and verbose>1:
				print "Notice: created a new Option entry"
			optionlist.append(o)
		
		#this one's always new
		#add BenchmarkHardware and BenchmarkOption reference here
		date, utime, stime, etime, tcount, scount, mVSIZE, mRSS = data['benchmark']

		#now create and save the db object
		b = Benchmark(model_ID=m, tool_ID=t, date_time=date, user_time=utime, system_time=stime, elapsed_time=etime, transition_count=tcount, states_count=scount, memory_VSIZE=mVSIZE, memory_RSS=mRSS, finished=True)
		b.save()
		#connect the manytomany relations. this has to happen AFTER calling save on the benchmark.
		for option in optionlist:
			bo = BenchmarkOption(benchmark=b, option=option)
			bo.save()
		for hardware in hardwarelist:
			bh = BenchmarkHardware(benchmark=b, hardware=hardware)
			bh.save()
		b.save()
	#end of write_to_db

	def main(self):
		"""Main function for this app
		This just controls everything.
		"""
		#parse the filereader options
		(options, args) = self.parse_app_options()
		self.verbose = options.verbose
		file_list = args
		if not file_list:
			print "Error: No file provided."
			exit()
		if self.verbose:
			print "Verbose mode active at level:", self.verbose, "\nLevel 1 text is preceded by 'Warning:', Level 2 by 'Notice:'"

		#fetch the patterns from the external file
		execute(self)
		if self.verbose>1:
			print "Notice: pattern list is: ", self.pattern_list

		#start of file-reading
		#when we want multiple files, a loop should be here
		path = file_list[0]
		if self.verbose>1:
			print "Notice: Reading from file: " + path
		try:
			file = open(path, 'r')
		except IOError as detail:
			#if something breaks, output the error and ask for retry
			print 'Error: ', detail, '\n'
			exit()
		#file fetched, read it now:
		lines = self.get_lines(file)
		file.close()
		if self.verbose>1:
			print "Notice: Read complete"
			print "Notice: Start parsing"
		#figure out the runs that are in here
		runs = self.find_runs(lines)
		#parse each:
		for run in runs:
			data = self.parse(run)
			self.write_to_db(data)
		#end of file-reading
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
		parser.add_option("-q", "--quiet",
			action="store_const", const=0, dest="verbose", help = "Do not print anything.")
		parser.add_option("-v", "--verbose",
			action="store_const", const=1, dest="verbose", help = "Print helpful things.")
		parser.add_option("--noisy",
			action="store_const", const=2, dest="verbose", help = "Print everything.")
		return parser.parse_args()
	#end of parse_app_options
	
	pattern_list = []
	
	def patterns(self, *args):
		for tuple in args:
			identification, tool, algorithm, option_dict, regex = tuple
			self.pattern_list.append((identification, (tool, algorithm, option_dict, regex)))
		return self.pattern_list
	#end of patterns
#end of FileReader

#run the main method
if __name__ == '__main__':
	sys.exit(FileReader.main(FileReader()))
