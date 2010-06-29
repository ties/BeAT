from django import forms
from django.forms import widgets
from beat.benchmarks.models import Benchmark, Model, Algorithm, Tool, OptionValue, AlgorithmTool
from beat.jobs.models import *
from django.shortcuts import get_object_or_404

def ltsminversions():
	versions = list(set(AlgorithmTool.objects.all().extra(order_by = ['date']).values_list('version', flat=True).distinct()))
	result = []
	for version in versions:
		result.append( (version,version) )
	return result

class JobGenForm(forms.Form):
	name		= forms.CharField(max_length=255, required=False)
	nodes		= forms.CharField(max_length=255, required=True, initial="1:E5520,walltime=4:00:00")
	tool		= forms.ModelChoiceField(Tool.objects.all(), empty_label=None, required=True)
	algorithm	= forms.ModelChoiceField(Algorithm.objects.all(), empty_label=None, required=True)
	options		= forms.CharField(max_length=255, required=False)
	model		= forms.ModelChoiceField(Model.objects.all().extra(order_by = ['name']), required=True)
	gitversion	= forms.ChoiceField( choices=ltsminversions() )
	#prefix		= forms.CharField(max_length=255, required=False)
	#postfix		= forms.CharField(max_length=255, required=False)
	
class SuiteGenForm(forms.Form):
	versions	= forms.MultipleChoiceField( choices=ltsminversions(), required=True )
	models		= forms.ModelMultipleChoiceField(Model.objects.all(), required=True)
