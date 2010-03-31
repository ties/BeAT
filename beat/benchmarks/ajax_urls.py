from django.conf.urls.defaults import *
from django.conf import settings
import os
urlpatterns = patterns('',
	(r'^filter/$', 'benchmarks.ajax_execute.ajaxfilter'),
	(r'^options/$', 'benchmarks.ajax_execute.ajaxoptions'),
)