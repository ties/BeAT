from django import forms
from django.forms import widgets
from django.db.models import Count
from beat.benchmarks.models import Benchmark

class ExportForm(forms.Form):
	benchmarks = forms.ModelMultipleChoiceField(Benchmark.objects.all(), required=False, widget=widgets.CheckboxSelectMultiple)
	name = forms.CharField(max_length=255, required=False)

class ToolUploadForm(forms.Form):
	version_name = forms.CharField(max_length=255, required=True, help_text='the name of the version like ltsmin-1.5-20-g6d5d0c')
	tool_name = forms.CharField(max_length=255, required=True, help_text='the name of the tool')
	algorithm_name = forms.CharField(max_length=255, required=True, help_text='the name of the algorithm')
	git_revision = forms.CharField(max_length=255, required=True, help_text='the git revision that fits with this')
	expression = forms.CharField(required=True, help_text='the regular expression to parese this log')
	test_log = forms.CharField(widget=forms.Textarea, required=False, help_text='enter a test log abov to see if your regular expression is correct')
	log_check = forms.CharField(widget=forms.Textarea, required=False)
	options = forms.CharField(widget=forms.Textarea, help_text='add option here like deadlock')

#class LogResponseForm(forms.Form):
#	response = forms.CharField(widget=forms.Textarea)