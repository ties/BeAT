from django.conf.urls.defaults import *
from django.conf import settings
import os
urlpatterns = patterns('',
	(r'^benchmarks/$', 'benchmarks.ajax_execute.ajaxbenchmarks'),
	(r'^modelcompare/$', 'benchmarks.modelcompare.ajaxmodels'),
)