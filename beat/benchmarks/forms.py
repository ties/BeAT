from django import forms
from django.forms import widgets
from django.db.models import Count
from beat.benchmarks.models import Benchmark

class ExportForm(forms.Form):
	benchmarks = forms.ModelMultipleChoiceField(Benchmark.objects.all(), required=False, widget=widgets.CheckboxSelectMultiple)
	name = forms.CharField(max_length=255, required=False)

