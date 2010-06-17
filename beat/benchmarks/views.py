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
	return render_to_response('base.html', context_instance=RequestContext(request))


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
	if not path: # check to see if path is not a path
		try: # try to get the data form beat if it is not a system path
			from beat.tools.logsave import __init_code__, get_log
			repo = losgsave.__init_code__()
			log = get_log(repo, path)
		except: #else return file not found
			log = 'Error: log file not found'
	else: # rad out the file and put it in the form
		with open(path, 'rb') as file:
			for line in file:
				loglist.append(line)
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
	dummydate = datetime.datetime.now()
	with_git = False
	repository = g.GitInterface(os.path.join(GIT_PATH, 'ltsmin')) # get the repository of ltsmin on the system.
		
	no_error = True
	if request.method == 'POST':
		form = ToolUploadForm(request.POST) # if post has bene called 
		if form.is_valid(): #check if it was a valid form that we can read
			version_name = form.cleaned_data['version_name']
			tool_name = form.cleaned_data['tool_name']
			algorithm_name = form.cleaned_data['algorithm_name']
			git_revision = form.cleaned_data['git_revision']
			expression = form.cleaned_data['expression']
			options = form.cleaned_data['options']
			matching_item = repository.get_matching_item(git_revision)
			# get all data form the form and store it
			if str(repository.get_sha(matching_item)).startswith(git_revision): # check if the igven git revision really is the version we want. because of how get_matching_item works.
				a, created = Algorithm.objects.get_or_create(name=algorithm_name)
				t, created = Tool.objects.get_or_create(name=tool_name)
				rx, created = Regex.objects.get_or_create(regex=options)
				dummydate = datetime(*repository.get_date(repository.get_matching_item(revision))[:6])
				at, created = AlgorithmTool.objects.get_or_create(algorithm=a, tool=t, regex=rx, date=dummydate, version=version_name)
				#put all the data in the database.
				y = options.split(';') #split the options on a semi colon
				for z in y: #then for each spitted option
					x = z.split(":") # spit again on colon so we got the option and its shot cut after each other.
					op, created = Option.objects.get_or_create(name=x[0], takes_argument=(x[0].endswith("=")))
					vo, created = ValidOption.objects.get_or_create(algorithm_tool=at, option=op, defaults={'regex':emptyregex})
					try: # try if it has a shot cut if not it skips that part.
						rs, created = RegisteredShortcut.objects.get_or_create(algorithm_tool=at, option=op, shortcut=x[1])
					except IndexError:
						pass
				form = ToolUploadForm() # return empty form if all is well
			else: # return the filled in form wiht the comment on the git revision and that it dous not exist.
				form = ToolUploadForm(initial={'tool_name' : tool_name, 'algorithm_name' : algorithm_name, 'git_revision' : 'git revision does not exist', 'expression' : expression, 'options' : options})
	else:
		form = ToolUploadForm() # return empty form if post was not used
	return render_to_response('upload_tool.html', {'form': form,}, context_instance=RequestContext(request)) # return the page with the form.

def test_regex(request):
	dump = json.dumps({'result': regex_tester.test_regex(request.POST.get('regex'), request.POST.get('testlog'))})
	return HttpResponse(dump,mimetype="application/json")
