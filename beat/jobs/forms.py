from django import forms
from django.forms import widgets
from beat.benchmarks.models import Benchmark, Model, Algorithm, Tool, OptionValue, AlgorithmTool
from beat.jobs.models import *
from django.shortcuts import get_object_or_404

class JobGenForm(forms.Form):
	name		= forms.CharField(max_length=255, required=False)
	tool		= forms.ModelChoiceField(Tool.objects.all(), empty_label=None, required=True)
	algorithm	= forms.ModelChoiceField(Algorithm.objects.all(), empty_label=None, required=True)
	models		= forms.ModelChoiceField(Model.objects.all().extra(order_by = ['name']), required=True)
	options		= forms.CharField(max_length=255, required=False)
	
	def change_defaults(self, jfilter):
		self.name		= forms.CharField(max_length=255, required=False, initial=jfilter.name)
		self.tool		= forms.ModelChoiceField(Tool.objects.all(), empty_label=None, required=True, initial=jfilter.tool)
		self.algoritm	= forms.ModelChoiceField(Algorithm.objects.all(), empty_label=None, required=True, initial=jfilter.algorithm)
		self.models		= forms.ModelChoiceField(Model.objects.all().extra(order_by = ['name']), required=True, initial=jfilter.model)
		self.options	= forms.CharField(max_length=255, required=False, initial=jfilter.options)
	
class SuiteGenForm(forms.Form):
	models = forms.ModelMultipleChoiceField(Model.objects.all(), required=True)
