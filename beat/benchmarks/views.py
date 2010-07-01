from django.http import HttpResponse, HttpResponseRedirect, HttpResponseForbidden
from django.contrib.auth.decorators import login_required
from django.template import RequestContext, loader
from django.shortcuts import render_to_response, redirect, get_object_or_404, get_list_or_404
import datetime
from beat.benchmarks.models import *
from beat.comparisons.models import Comparison, ModelComparison
from beat.tools import graph, export_csv, regex_tester
from forms import *
import json

#@login_required(redirect_field_name='next')
def index(request):
	benches = Benchmark.objects.order_by("date_time")[0:10]
	return render_to_response('base.html', {'benches':benches}, context_instance=RequestContext(request))


"""
Show the list of benchmarks
"""
@login_required()
def benchmarks(request):
	return render_to_response('benchmarks.html', {}, context_instance=RequestContext(request))

"""
ExportForm handler.
Take all selected benchmarks and redirect to compare page or show empty form
"""	
@login_required()
def export_benchmarks(request):
	if request.method == 'POST': # If the form has been submitted...
		form =  ExportForm(request.POST) # A form bound to the POST data
		if form.is_valid():
			ids = json.loads(request.POST['ids'])
			b = form.cleaned_data['benchmarks']
			title = form.cleaned_data['name']
			# Export CSV button has been clicked:
			bs = Benchmark.objects.filter(id__in=ids)
			if (title == ''):
				title = 'benchmarks'
		
			# Return CSV file to browser as download
			return export_csv.export(bs, title, ['logfile'])
				
	return render_to_response('benchmarks.html', {'form': form}, context_instance=RequestContext(request))
"""
Shows a list of all Comparisons and ModelComparisons
"""		
@login_required()
def user_comparisons(request):
	b_comparisons = list(Comparison.objects.filter(user=request.user.id))
	m_comparisons = list(ModelComparison.objects.filter(user=request.user.id))
	return render_to_response('user_compare.html', { 'b_comparisons' : b_comparisons, 'm_comparisons' : m_comparisons }, context_instance=RequestContext(request))

"""
Shows the colophone page for this project.
"""
def colophon(request):
	return render_to_response('colophon.html', context_instance=RequestContext(request))

"""
Shows a log file for the given database id. if no such file is found it will return a file not found in the response form.
"""	
@login_required
def log_response(request, id):	
	b = Benchmark.objects.get(pk=id)
	path = b.logfile
	ov = b.optionvalue.all()
	hw = b.hardware.all()
	ev = ExtraValue.objects.filter(benchmark=b)
	loglist = []
	if not os.path.exists(path):
		#read log from git repository containing logs
		try:
			from beat.tools.logsave import __init_code__, get_log
			repo = losgsave.__init_code__()
			log = get_log(repo, path)
		except:
			log = 'Error: log file not found'
	else:
		try:
			#read log from file
			with open(path, 'rb') as file:
				for line in file:
					loglist.append(line)
		except IOError:
			log = 'IOError: log file not found'
	return render_to_response('log_response.html', {'ev':ev,'log':loglist,'b': b, 'ov':ov, 'hardware':hw,}, context_instance=RequestContext(request))

"""
This method allows for the uploading of tool to the database. 
It will take the reqest read out the form and attempt to put it in the database.
"""
@login_required
def tool_upload(request):
	import time
	import sys
	import beat.gitinterface as g
	
	#switch to and pull the repository
	#this can later be extended to use a user-provided repository
	repository = g.GitInterface(os.path.join(GIT_PATH, 'ltsmin'))

	at = None
	error = False
	if request.method == 'POST':
		repository.pull_from_git("http://fmt.cs.utwente.nl/tools/scm/ltsmin.git")
		form = ToolUploadForm(request.POST)
		if form.is_valid():
			version_name = form.cleaned_data['version_name']
			tool_name = form.cleaned_data['tool_name']
			algorithm_name = form.cleaned_data['algorithm_name']
			expression = form.cleaned_data['expression']
			options = form.cleaned_data['options']
			matching_item = repository.get_matching_item(version_name[-6:])
			#note that get_matching_item() returns the oldest revision if a match is not found, so this check is needed:
			if str(matching_item).startswith(version_name[-6:]):
				dummydate = datetime.datetime(*repository.get_date(repository.get_matching_item(version_name[-6:]))[:6])			
				emptyregex,created=Regex.objects.get_or_create(regex="")
				a, created = Algorithm.objects.get_or_create(name=algorithm_name)
				t, created = Tool.objects.get_or_create(name=tool_name)
				rx, created = Regex.objects.get_or_create(regex=expression)
				at, created = AlgorithmTool.objects.get_or_create(algorithm=a, tool=t, regex=rx, date=dummydate, version=version_name[:6])
				y = options.split('\n') #split the options field into lines
				for z in y:
					if z.endswith('\r'):
						z=z[:-1]
					if not z: #empty line, skip
						continue
					#figure out what the shortcut is, if any, and whether this option takes an argument
					shortcut = ""
					if z[-2] == ':':
						takes_arg=(z[-3]=='=')
						shortcut=z[-1]
					else:
						takes_arg=(z[-2]=='=')
					
					#determine the option
					if shortcut and (len(z)==2):
						option = " "+shortcut
					elif takes_arg and shortcut:
						option = z[:-3]
					elif shortcut:
						option = z[:-2]
					elif takes_arg:
						option = z[:-1]
					else:
						option = z
						
					op, created = Option.objects.get_or_create(name=option, takes_argument=takes_arg)
					vo, created = ValidOption.objects.get_or_create(algorithm_tool=at, option=op, defaults={'regex':emptyregex})
					rs, created = RegisteredShortcut.objects.get_or_create(algorithm_tool=at, option=op, shortcut=shortcut)
				form = ToolUploadForm()
			else:
				form = ToolUploadForm(initial={'tool_name' : tool_name, 'algorithm_name' : algorithm_name, 'version_name' : version_name, 'expression' : expression, 'options' : options})
				error="Could not find the provided version in the git."
	else:
		return render_to_response('upload_tool.html', {'form': ToolUploadForm()}, context_instance=RequestContext(request))
	if error:
		return render_to_response('upload_tool.html', {'form': form, 'error' : error}, context_instance=RequestContext(request))
	else:
		return render_to_response('upload_tool_complete.html', {'id':at.id}, context_instance=RequestContext(request))

def test_regex(request):
	dump = json.dumps({'result': regex_tester.test_regex(request.POST.get('regex'), request.POST.get('testlog'))})
	return HttpResponse(dump,mimetype="application/json")
