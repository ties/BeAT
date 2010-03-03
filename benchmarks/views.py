from django.http import HttpResponse
from django.contrib.auth.decorators import login_required
from django.template import RequestContext, loader
from django.shortcuts import render_to_response
from beat.benchmarks.models import Benchmark

#@login_required(redirect_field_name='next')
def index(request):
	
	t = loader.get_template('base.html')
	c = RequestContext(request, {
		'is_admin' : request.user.is_staff,
		'is_logged_in' : request.user.is_authenticated()
	})
	return HttpResponse(t.render(c));
	
def tables(request):
	t = loader.get_template('index_tables.html')
	c = RequestContext(request, {})
	return HttpResponse(t.render(c));

def benchmarks(request):
	benches = Benchmark.objects.all()
	t = loader.get_template('benchmarks.html')
	c = RequestContext(request, {
		'benchmarks' : benches
	})
	return HttpResponse(t.render(c))

#@login_required()
#def mudkip(request):

#def index(request):
#	return HttpResponse('Hello world.')