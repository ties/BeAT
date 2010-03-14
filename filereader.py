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

class FileReader:
	verbose = 0 #default: no messages except errors
	#def __init__(self):
	#	contructor
	def match_regex(self, regex, input, flags=None, disable_verbose=False):
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
		contents = ''.join(lines[1:])#all lines 'cept the first
		if self.verbose>1:
			print "Notice: Finding parser..."
		parse_info = self.get_parser(lines[0]) #the first line is used here
		if self.verbose>1:
			print "Notice: Found parser!"
		options = parse_info[2]	#fetch the options specified by the first line
		regex = parse_info[3]	#expression to parse
		
		if self.verbose>1:
			print "Notice: Option(s) are:",options
			print "Notice: Regex is:",regex
			print "Notice: Reading data..."
		data = self.parse_single_output(contents, options, regex)
		if self.verbose>1:
			print "Notice: Read successful!"
		self.write_to_db(data)
	#end of parse
	
	def write_to_db(self, data):
		#model entry
		name, version, location = data['model']
		if not name or version == -1 or not location:
			if self.verbose:
				print "Warning: Model.name=",name,"Model.version=",version,"Model.location=",location
			#name or version invalid -> raise an error
			#for location, just leave it none
		m = Model(name=name ,version=version, location=location)

		#tool entry
		name, version = data['tool']
		if not name or version == -1:
			if self.verbose:
				print "Warning: Tool.name=",name,"Tool.version=",version
			#name or version invalid -> raise an error
		t = Tool(name=name, version=version)

		#hardware entries
		hwdata = data['hardware']
		hardwarelist = []
		for tuple in hwdata:
			name, memory, cpu, disk_space, os = tuple
			if not name or memory == -1 or not cpu or disk_space ==-1 or not os:
				if self.verbose:
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
				if self.verbose:
					print "Warning: invalid option: name",name,"value",value
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
				if self.verbose:
					print "Warning: invalid value in benchmark"
				#raise an error?
		
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
	#end of write_to_db
	
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

	# This dictionary contains all known parsers
	# format:
	#{
	#	ID : (tool, algorithm, {'option0':True, 'option1':'hello world'}, parse_function, parse_regex),
	#}
	parsers = {
		'nips2lts-grey' : ("nips", "grey", {}, r'nips2lts-grey: .*\nnips2lts-grey: state space has \d+ levels (?P<scount>\d+) states (?P<tcount>\d+) .*\nExit \[[0-9]+\]\n(?P<utime>[0-9\.]+) user, (?P<stime>[0-9\.]+) system, (?P<etime>[0-9\.]+) elapsed --( Max | )VSize = (?P<vsize>\d+)KB,( Max | )RSS = (?P<rss>\d+)KB'),
#		'nips2lts-grey-fileout-dir' : ("nips", "grey", {"fileout_dir": True,}, parse_nips_grey, r'nips2lts-grey: NIPS language module initialized\n.*\nnips2lts-grey: state space has \d+ levels (?P<scount>\d+) states (?P<tcount>\d+) .*\nExit \[[0-9]+\]\n(?P<utime>[0-9\.]+) user, (?P<stime>[0-9\.]+) system, (?P<etime>[0-9\.]+) elapsed --( Max | )VSize = (?P<vsize>\d+)KB,( Max | )RSS = (?P<rss>\d+)KB'),
#		'dve2lts-grey' : ("dve", "grey"), {}, parse_single_output,  r'dve2lts-grey: .*\nnips2lts-grey: state space has \d+ levels (?P<scount>\d+) states (?P<tcount>\d+) .*\nExit \[[0-9]+\]\n(?P<utime>[0-9\.]+) user, (?P<stime>[0-9\.]+) system, (?P<etime>[0-9\.]+) elapsed --( Max | )VSize = (?P<vsize>\d+)KB,( Max | )RSS = (?P<rss>\d+)KB'),
	}
	
	def get_parser(self, content):
		type = content.split('\n', 1)[0] # = first line
		if self.verbose>1:
			print "Notice: " + type + " is the parser, according to the file."
		try:
			return self.parsers[type]
		except KeyError:
			print "Error: parsing of the data in the specified file is not yet supported."
			exit()
	#end of get_parser
	
	def main(self):
		(options, args) = self.parse_options()
		self.verbose = options.verbose
		file_list = args
		if self.verbose:
			print "Verbose mode active at level:", self.verbose, "\nLevel 1 text is preceded by 'Warning:', Level 2 by 'Notice:'"
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
		#we have a file to work with
		#read the lines here
		lines = self.get_lines(file)
		file.close()
		if self.verbose>1:
			print "Notice: Read complete"
			print "Notice: Start parsing"
		self.parse(lines)
		
	#end of main
	
	def parse_options(self):
		parser = OptionParser()
		parser.add_option("-q", "--quiet",
			action="store_const", const=0, dest="verbose", help = "Do not print anything.")
		parser.add_option("-v", "--verbose",
			action="store_const", const=1, dest="verbose", help = "Print helpful things.")
		parser.add_option("--noisy",
			action="store_const", const=2, dest="verbose", help = "Print everything.")
		return parser.parse_args()
	#end of parse_options

#run the main method
if __name__ == '__main__':
	sys.exit(FileReader.main(FileReader()))