from django.http import HttpResponse
from django.contrib.auth.decorators import login_required
from django.template import RequestContext, loader
from django.shortcuts import render_to_response
from beat.benchmarks.models import *
from django.core import serializers
from beat.benchmarks.filter import *
from beat.benchmarks.ajax_benchmarks import *
from datetime import datetime
import json

def ajaxbenchmarks(request):
	res = getBenchmarks(request)
	dthandler = lambda obj: obj.date().isoformat() if isinstance(obj, datetime) else None
	dump = json.dumps(res,default=dthandler)
	return HttpResponse(dump,mimetype="application/json")