from django.http import HttpResponse
from django.contrib.auth.decorators import login_required
from django.template import RequestContext, loader
from django.shortcuts import render_to_response
from beat.benchmarks.models import *
from django.core import serializers
from beat.benchmarks.filter import *
from datetime import datetime
import json
"""
	Function to filter the benchmark table, returns a HttpResponse with the filtered values and the possible algorithms, models, options, and tools

def ajaxbenchmarks(request):
	print "POST:"
	print request.POST.lists()
	
	filters = convertfilters(request.POST.lists())
	#print filters
	qs = Benchmark.objects.all()
	#print qs
	
	result = getAjaxResponse(qs,filters)
	dump = json.dumps(result)
	
	print '--------------DUMP-------------------'
	print dump
	
	return HttpResponse(dump,mimetype="application/json")
"""
def getAjaxResponse(qs,filters):
	algorithmids = []
	optionids = []
	toolids = []
	modelids = []
	
	algorithmdone = False
	optionsdone = False
	tooldone = False
	modeldone = False
	
	for k,f in filters.iteritems():
		print "Now starting filter row %i" % f.row
		print qs
		if f.type==MODEL:
			print "Filter of type model"
			modelids = getModels(qs)
			modeldone = True
			print modelids
		elif f.type==ALGORITHM:
			print "Filter of type algorithm"
			algorithmids = getAlgorithms(qs)
			algorithmdone = True
			print algorithmids
		elif f.type==TOOL:
			print "Filter of type tool"
			toolids = getTools(qs)
			tooldone = True
			print toolids
		elif f.type==OPTIONS:
			print "Filter of type options"
			optionids = getOptions(qs)
			optionsdone = True
			print optionids
		
		qs = f.apply(qs)
	
	print "Final queryset:"
	print qs
	result = {}
	benchmarks = []
	
	for benchmark in qs:
		benchmarks.append({
			'id': benchmark.id,
			'model': benchmark.model.name+":"+benchmark.model.version,
			'states': benchmark.states_count,
			'runtime': benchmark.total_time,
			'memory': benchmark.memory_RSS,
			'finished': benchmark.finished
		})
		if modeldone==False:
			modelids.append(benchmark.model.id)
		
		if algorithmdone==False:
			algorithmids.append(benchmark.algorithm.id)
		
		if tooldone==False:
			toolids.append(benchmark.tool.id)
		
		if optionsdone==False:
			for ov in benchmark.optionvalue.all():
				optionids.append(ov.option.id)
	
	result['benchmarks'] = benchmarks
	algorithms = []
	options = []
	tools = []
	models = []
	
	for a in Algorithm.objects.filter(id__in=algorithmids).order_by('name').values('id','name'):
		algorithms.append(a)
	for m in Model.objects.filter(id__in=modelids).order_by('name').values('id','name'):
		models.append(m)
	for o in Option.objects.filter(id__in=optionids).order_by('name').values('id','name','takes_argument'):
		options.append(o)
	for t in Tool.objects.filter(id__in=toolids).order_by('name').values('id','name'):
		tools.append(t)
	
	result['algorithms'] = algorithms
	result['options'] = options
	result['tools'] = tools
	result['models'] = models
	
	return result

def getModels(qs):
	ids = []
	for benchmark in qs:
		ids.append(benchmark.model.id)
	
	return list(set(ids))

def getAlgorithms(qs):
	ids = []
	for benchmark in qs:
		ids.append(benchmark.algorithm.id)
	
	return list(set(ids))

def getTools(qs):
	ids = []
	for benchmark in qs:
		ids.append(benchmark.tool.id)
	
	return list(set(ids))

def getOptions(qs):
	ids = []
	for benchmark in qs:
		for ov in benchmark.optionvalue.all():
			ids.append(ov.option.id)
	
	return list(set(ids))

def ajaxbenchmarks(request):
	print request.POST
	
	filters = {}
	if 'filters' in request.POST.keys():
		filters = convertfiltersJSON(json.loads(request.POST['filters']))
	print filters
	res = getAjaxResponse(Benchmark.objects.all(),filters)
	print res
	dump = json.dumps(res)
	
	return HttpResponse(dump,mimetype="application/json")