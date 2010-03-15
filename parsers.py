from filereader import FileReader

def execute(obj):
	obj.patterns(
		#here, create your own tuples.
		#they're formatted as follows:
		#(identification, tool_name, algorithm_name, options, regular_expression),
		#where regular_expression is the expression to parse the log,
			#identification is how the tool is identified by the run details log.
			#options is a dictionary, which looks like:
			#{name0 : value0, name1:value1, name2:value2,}
			#and can contain any number of values, of any valid python type. the names must be valid python strings.
		
		
		("nips2lts-grey", "nips", "grey", {}, r'nips2lts-grey: .*\nnips2lts-grey: state space has \d+ levels (?P<scount>\d+) states (?P<tcount>\d+) .*\nExit \[[0-9]+\]\n(?P<utime>[0-9\.]+) user, (?P<stime>[0-9\.]+) system, (?P<etime>[0-9\.]+) elapsed --( Max | )VSize = (?P<vsize>\d+)KB,( Max | )RSS = (?P<rss>\d+)KB'),
	)