from django.http import HttpResponse
from django.contrib.auth.decorators import login_required
from django.template import RequestContext, loader
from django.shortcuts import render_to_response
from beat.benchmarks.models import Benchmark, Option
from django.core import serializers
from beat.benchmarks.filter import *
from datetime import datetime
import json
"""
	Function to filter the benchmark table, returns a HttpResponse with the filtered values and the possible algorithms, models, options, and tools
"""
def ajaxbenchmarks(request):
	print "POST:"
	print request.POST
	#for k in request.POST.lists():
	#	print k
	qs = filter(Benchmark.objects.all(),convertfilters(request.POST.lists()))
	#qs = Benchmark.objects.all()
	print "Queryset:"
	print qs
	result = {}
	benchmarks = []
	algorithms = []
	options = []
	tools = []
	models = []
	
	#to prevent duplicates:
	algorithmids = []
	optionids = []
	toolids = []
	modelids = []
	
	for benchmark in qs:
		benchmarks.append({
			'id': benchmark.id,
			'model': benchmark.model.name+":"+benchmark.model.version,
			'states': benchmark.states_count,
			'runtime': benchmark.total_time,
			'memory': benchmark.memory_RSS,
			'finished': benchmark.finished
			})
		
		if benchmark.algorithm.id not in algorithmids:
			algorithms.append({
				'id': benchmark.algorithm.id,
				'name': benchmark.algorithm.name
				})
			algorithmids.append(benchmark.algorithm.id)
		
		if benchmark.model.id not in modelids:
			models.append({
				'id': benchmark.model.id,
				'name': benchmark.model.name
				})
			modelids.append(benchmark.model.id)
		
		if benchmark.tool.id not in toolids:
			tools.append({
				'id': benchmark.tool.id,
				'name': benchmark.tool.name
				})
			toolids.append(benchmark.tool.id)
		
		for ov in benchmark.optionvalue.all():
			if ov.option.id not in optionids:
				options.append({
					'id': ov.option.id,
					'name': ov.option.name,
					'takes_argument': ov.option.takes_argument
					})
				optionids.append(ov.option.id)
	
	result['benchmarks'] = benchmarks
	result['algorithms'] = algorithms
	result['options'] = options
	result['tools'] = tools
	result['models'] = models
	
	dump = json.dumps(result)
	
	print '--------------RESULT-----------------------'
	print result
	print '--------------DUMP-------------------'
	print dump
	
	return HttpResponse(dump,mimetype="application/json")