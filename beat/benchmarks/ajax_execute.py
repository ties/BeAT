from django.http import HttpResponse
from django.contrib.auth.decorators import login_required
from django.template import RequestContext, loader
from django.shortcuts import render_to_response
from beat.benchmarks.models import Benchmark
from django.core import serializers
from beat.benchmarks.filter import *
from datetime import datetime

"""
	Function to filter the benchmark table, returns a HttpResponse with the filtered values
"""
def ajaxfilter(request):
	if (request.method=='GET'):
		qs = filter(Benchmark.objects.all(),convertfilters(request.GET))
		data = serializers.serialize("json", qs,use_natural_keys=True)
		return HttpResponse(data, mimetype="application/json")