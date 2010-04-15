from django import forms
from django.forms import widgets
from django.db.models import Count

from beat.benchmarks.models import Benchmark, Model, Algorithm, Tool, OptionValue

class CompareForm(forms.Form):
	benchmarks = forms.ModelMultipleChoiceField(Benchmark.objects.all(), required=False, widget=widgets.CheckboxSelectMultiple)
	
class CompareModelsForm(forms.Form):
	DATA_TYPES = (
		('transitions', 'Transition count'),
		('states', 'States count'),
		('vsize', 'Memory VSIZE'),
		('rss', 'Memory RSS'),
	)
	type = forms.ChoiceField(choices=DATA_TYPES, label='Data type', help_text='What type of data should be displayed in the graph?')
	tool = forms.ModelChoiceField(Tool.objects.all(), empty_label=None)
	algorithm = forms.ModelChoiceField(Algorithm.objects.all(), empty_label=None)
	option = forms.ModelChoiceField(OptionValue.objects.all(), required=False)
	#models = forms.ModelMultipleChoiceField(Model.objects.all())

	
class UploadLogForm(forms.Form):
    title = forms.CharField(max_length=50)
    file  = forms.FileField()
