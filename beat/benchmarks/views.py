from django.http import HttpResponse, HttpResponseRedirect, HttpResponseForbidden
from django.contrib.auth.decorators import login_required
from django.template import RequestContext, loader
from django.shortcuts import render_to_response, redirect, get_object_or_404, get_list_or_404
import datetime
from beat.benchmarks.models import *
from beat.comparisons.models import Comparison, ModelComparison
from beat.tools import graph, export_csv
from forms import *

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
		if (form.is_valid()):
		
			b = form.cleaned_data['benchmarks']
			title = form.cleaned_data['name']
			# Export CSV button has been clicked:
			ids = [bench.id for bench in b]
			bs = Benchmark.objects.filter(id__in=ids)
			if (title == ''):
				title = 'benchmarks'
			
			# Return CSV file to browser as download
			return export_csv.export(bs, title)
				
	return render_to_response('benchmarks.html', {'form': form}, context_instance=RequestContext(request))
"""
Shows a list of all Comparisons and ModelComparisons
"""		
@login_required()
def user_comparisons(request):
	b_comparisons = list(Comparison.objects.filter(user=request.user.id))
	m_comparisons = list(ModelComparison.objects.filter(user=request.user.id))
	return render_to_response('user_compare.html', { 'b_comparisons' : b_comparisons, 'm_comparisons' : m_comparisons }, context_instance=RequestContext(request))

def colophon(request):
	return render_to_response('colophon.html', context_instance=RequestContext(request))