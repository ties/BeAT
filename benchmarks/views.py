from django.http import HttpResponse
from django.contrib.auth.decorators import login_required
from django.template import RequestContext, loader
from django.shortcuts import render_to_response
from beat.benchmarks.models import Benchmark

#@login_required(redirect_field_name='next')
def index(request):
	
	t = loader.get_template('base.html')
	c = RequestContext(request, {
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

def compare(request):
	if request.method == 'POST': # If the form has been submitted...
			r = request.POST
			t = loader.get_template('compare.html')
			c = RequestContext(request, {
				'compare' : r
			})
			return HttpResponse(t.render(c)) # Redirect after POST
	else:
		form = ContactForm() # An unbound form
	return render_to_response('contact.html', {
		'form': form,
	})
#@login_required()
#def mudkip(request):

#def index(request):
#	return HttpResponse('Hello world.')