from django import forms
from django.forms import widgets
from django.db.models import Count

from beat.benchmarks.models import Benchmark, Model

class CompareForm(forms.Form):
	benchmarks = forms.ModelMultipleChoiceField(Benchmark.objects.all(), required=False, widget=widgets.CheckboxSelectMultiple)
	
class CompareModelsForm(forms.Form):
	DATA_TYPES = (
		('transitions', 'Transition count'),
		('states', 'States count'),
		('vsize', 'Memory VSIZE'),
		('rss', 'Memory RSS'),
	)
	type = forms.ChoiceField(choices=DATA_TYPES, label='Data type')
	models = forms.ModelMultipleChoiceField(Model.objects.all())
	
class UploadLogForm(forms.Form):
    title = forms.CharField(max_length=50)
    file  = forms.FileField()
