from django.http import HttpResponse
from django.contrib.auth.decorators import login_required
from django.template import RequestContext, loader
from django.shortcuts import render_to_response
from beat.benchmarks.models import Benchmark
from django import forms
from django.forms import widgets

class CompareForm(forms.Form):
	benchmarks = forms.ModelMultipleChoiceField(Benchmark.objects.all(), required=False, widget=widgets.CheckboxSelectMultiple)

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
		form = CompareForm(request.POST) # A form bound to the POST data
		if form.is_valid(): # All validation rules pass
			# Process the data in form.cleaned_data
			b = form.cleaned_data['benchmarks']
			t = loader.get_template('compare.html')
			c = RequestContext(request, {
				# benchmarks is an array of selected Benchmark objects,
				# so properties of a single benchmark object can still be accessed.
				'benchmarks' : b
			})
			return HttpResponse(t.render(c)) # Redirect after POST
	#else:
	#	form = CompareForm() # An unbound form
	return render_to_response('compare.html', {
		'form': form,
	})

#@login_required()
#def mudkip(request):

#def index(request):
#	return HttpResponse('Hello world.')