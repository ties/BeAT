from django import forms
from django.forms import widgets
from beat.benchmarks.models import Benchmark, Model, Algorithm, Tool, OptionValue, AlgorithmTool
from beat.jobs.models import *

class JobGenForm(forms.Form):
	algos			= AlgorithmTool.objects.all()
	algos			= algos.extra(order_by = ['version','tool','algorithm'])
	name			= forms.CharField(max_length=255, required=False)
	
	models = forms.ModelMultipleChoiceField(Model.objects.all(), required=True)
	tool = forms.ModelChoiceField(Tool.objects.all(), empty_label=None, required=False)
	algorithm = forms.ModelChoiceField(Algorithm.objects.all(), empty_label=None, required=False)

class SuiteGenForm(forms.Form):
	models = forms.ModelMultipleChoiceField(Model.objects.all(), required=True)
