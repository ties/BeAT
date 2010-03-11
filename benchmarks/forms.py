from django import forms
from django.forms import widgets

from beat.benchmarks.models import Benchmark

class CompareForm(forms.Form):
	benchmarks = forms.ModelMultipleChoiceField(Benchmark.objects.all(), required=False, widget=widgets.CheckboxSelectMultiple)