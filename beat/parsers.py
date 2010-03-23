from filereader import *

def execute(obj):
	obj.patterns(
		#here, create your own tuples.
		#they're formatted as follows:
		#(identification, tool_name, algorithm_name, regular_expression, short_parameters, long_parameters),
		#here's an example:
		(
			#identifier, name, 
			"nips2lts-grey", "nips", "grey", 
			r'nips2lts-grey: .*\nnips2lts-grey: state space has \d+ levels '
				+'(?P<scount>\d+) states (?P<tcount>\d+).*\nExit \[[0-9]+\]\n'
				+'(?P<utime>[0-9\.]+) user, (?P<stime>[0-9\.]+) system, '
				+'(?P<etime>[0-9\.]+) elapsed --( Max | )VSize = '
				+'(?P<vsize>\d+)KB,( Max | )RSS = (?P<rss>\d+)KB',
			'dcr:vqh',
			[
				'strategy=', 'state=', 'deadlock', 'trace=', #options
				'cache', 'regroup=',#greybox
				'vset=',#vector set
				'cache-ratio=', 'max-increase=', 'min-free-nodes=', 'fdd-bits=', #BuDDy
				'block-size=', 'cluster-size=', 'plain', #container i/o
				'grey', 'matrix', 'write-state', #dev
				'debug', 'version', 'help', 'usage' #general
			]
		),
		(
			"lpo2lts-grey", "lpo", "grey", 
			r'lpo2lts-grey: .*\nlpo2lts-grey: state space has \d+ levels'
			+' (?P<scount>\d+) states (?P<tcount>\d+) .*\nExit \[[0-9]+\]'
			+'\n(?P<utime>[0-9\.]+) user, (?P<stime>[0-9\.]+) system, '
			+'(?P<etime>[0-9\.]+) elapsed --( Max | )VSize ='
			+' (?P<vsize>\d+)KB,( Max | )RSS = (?P<rss>\d+)KB',
			'dcr:vqh',
			[
				'strategy=', 'state=', 'deadlock', 'trace=', #options
				'state-names', 'mcrl=', #mcrl
				'cache', 'regroup=',#greybox
				'vset=',#vector set
				'cache-ratio=', 'max-increase=', 'min-free-nodes=', 'fdd-bits=', #BuDDy
				'block-size=', 'cluster-size=', 'plain', #container i/o
				'grey', 'matrix', 'write-state', #dev
				'debug', 'version', 'help', 'usage' #general
			]
		),
		(
			"lpo-reach", "lpo", "reach",
			r'lpo-reach: .*\nlpo-reach: reachability took.*\nstate space'
			+' has (?P<scount>\d+) states.*\nExit \[[0-9]+\]\n(?P<utime>[0-9\.]+)'
			+' user, (?P<stime>[0-9\.]+) system, (?P<etime>[0-9\.]+) elapsed --'
			+'( Max | )VSize = (?P<vsize>\d+)KB,( Max | )RSS = (?P<rss>\d+)KB',
			'dcr:vqh',
			[
				'order=', 'deadlock', 'trace=' #opts
				'state-names', 'mcrl=', #mcrl
				'cache', 'regroup=',#greybox
				'vset=',#vector set
				'cache-ratio=', 'max-increase=', 'min-free-nodes=', 'fdd-bits=', #BuDDy
				'debug', 'version', 'help', 'usage' #general
			]
		),
		(	#not sure about this one in terms of options
			"ltsmin", "ltsmin", "ltsmin",
			r'.*\nreduced LTS has (?P<scount>\d+) states and'
			+'  (?P<tcount>\d+).*\nExit \[[0-9]+\]\n(?P<utime>[0-9\.]+)'
			+' user, (?P<stime>[0-9\.]+) system, (?P<etime>[0-9\.]+) elapsed '
			+'--( Max | )VSize = (?P<vsize>\d+)KB,( Max | )RSS = (?P<rss>\d+)KB',
			'',
			[
			]
		),
		(
			"nips-reach", "nips", "reach",
			r'nips-reach: .*\nnips-reach: reachability took.*\nstate space has'
			+' (?P<scount>\d+) states.*\nExit \[[0-9]+\]\n(?P<utime>[0-9\.]+) '
			+'user, (?P<stime>[0-9\.]+) system, (?P<etime>[0-9\.]+) elapsed --'
			+'( Max | )VSize = (?P<vsize>\d+)KB,( Max | )RSS = (?P<rss>\d+)KB',
			'dcr:vqh',
			[
				'order=', 'deadlock', 'trace=' #opts
				'cache', 'regroup=',#greybox
				'vset=',#vector set
				'cache-ratio=', 'max-increase=', 'min-free-nodes=', 'fdd-bits=', #BuDDy
				'debug', 'version', 'help', 'usage' #general
			]
		),
		(
			"etf2lts-grey", "etf", "grey", 
			r'etf2lts-grey: .*\netf2lts-grey: state space has \d+ levels '
			+'(?P<scount>\d+) states (?P<tcount>\d+) .*\nExit \[[0-9]+\]\n'
			+'(?P<utime>[0-9\.]+) user, (?P<stime>[0-9\.]+) system, '
			+'(?P<etime>[0-9\.]+) elapsed --( Max | )VSize = (?P<vsize>\d+)KB,'
			+'( Max | )RSS = (?P<rss>\d+)KB',
			'dcr:vqh',
			[
				'strategy=', 'state=', 'deadlock', 'trace=', #options
				'cache', 'regroup=',#greybox
				'vset=',#vector set
				'cache-ratio=', 'max-increase=', 'min-free-nodes=', 'fdd-bits=', #BuDDy
				'debug', 'version', 'help', 'usage' #general
			]
		),
		(
			"etf-reach", "etf", "reach", 
			r'etf-reach: .*\netf-reach: reachability took.*\nstate space has'
			+' (?P<scount>\d+) states.*\nExit \[[0-9]+\]\n(?P<utime>[0-9\.]+)'
			+' user, (?P<stime>[0-9\.]+) system, (?P<etime>[0-9\.]+) elapsed --'
			+'( Max | )VSize = (?P<vsize>\d+)KB,( Max | )RSS = (?P<rss>\d+)KB',
			'dcr:vqh',
			[
				'order=', 'deadlock', 'trace=' #opts
				'cache', 'regroup=',#greybox
				'vset=',#vector set
				'cache-ratio=', 'max-increase=', 'min-free-nodes=', 'fdd-bits=', #BuDDy
				'debug', 'version', 'help', 'usage' #general
			]
		),
	)