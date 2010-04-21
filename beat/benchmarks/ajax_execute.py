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
"""
def ajaxbenchmarks(request):
	print "check"
	#filter:
	print request.POST.lists()
	qs = filter(Benchmark.objects.all(),convertfilters(request.POST.lists()))
	print "check"
	#order:
	order = 'id'; #needs code to get the actual order
	qs.order_by(order)
	print "check"
	result = {}
	benchmarks = []
	
	algorithmids = []
	optionids = []
	toolids = []
	modelids = []
	print "check"
	for benchmark in qs:
		benchmarks.append({
			'id': benchmark.id,
			'model': benchmark.model.name+":"+benchmark.model.version,
			'states': benchmark.states_count,
			'runtime': benchmark.total_time,
			'memory': benchmark.memory_RSS,
			'finished': benchmark.finished
		})
		#add ids
		algorithmids.append(benchmark.algorithm.id)
		toolids.append(benchmark.tool.id)
		modelids.append(benchmark.model.id)
		for ov in benchmark.optionvalue.all():
			optionids.append(ov.option.id)
	print "check"
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
	print "check"
	result['algorithms'] = algorithms
	result['options'] = options
	result['tools'] = tools
	result['models'] = models
	print "check"
	dump = json.dumps(result)
	print '--------------DUMP-------------------'
	print dump
	
	return HttpResponse(dump,mimetype="application/json")