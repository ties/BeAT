from django.conf.urls.defaults import *
from django.conf import settings
import os

# Uncomment the next two lines to enable the admin:
from django.contrib import admin
admin.autodiscover()

urlpatterns = patterns('',
	# Example:
	# (r'^beat/', include('beat.foo.urls')),
	(r'^benchmarks/ajax/', include('beat.benchmarks.ajax_urls')),
	(r'^$', 'benchmarks.views.index'),
	(r'^benchmarks/export/$', 'benchmarks.views.export_benchmarks'),
	(r'^benchmarks/(?P<id>\d+)/$', 'benchmarks.views.log_response'),

	# Graph for benchmark-scatterplot, this needs to be implemented in views.benchmarks
	(r'^benchmarks/$', 'benchmarks.views.benchmarks'),
	
	# View saved comparisons
	(r'^user/compare/$', 'benchmarks.views.user_comparisons'),
	
	# URLs for comparisons are decoupled - they can be found in the comparisons module.
	(r'^compare/', include('beat.comparisons.urls')),
	
	#Job Generation
	#authorization should be here too
	(r'^jobgen/$', 'jobs.views.jobgen'),
	(r'^jobgen/go/$', 'jobs.views.jobgen_create'),
	(r'^suitegen/go/$', 'jobs.views.suitegen_create'),
	(r'^jobgen/(?P<id>[0-9]+)/$', 'jobs.views.jobgen_load'),
	
	#View saved jobs
	(r'^user_jobs', 'jobs.views.user_jobs'),
	
	# Uncomment the next line to enable the admin:
	(r'^admin/', include(admin.site.urls)),
	(r'^admin/doc/', include('django.contrib.admindocs.urls')),
	
	# Auth pages
	(r'^logout/$', 'django.contrib.auth.views.logout_then_login'),
	(r'^login/$', 'django.contrib.auth.views.login', {'template_name': 'login.html'}),
	
	# Overige pagina's
	(r'^colophon/$', 'benchmarks.views.colophon'),
	(r'^tool_upload/$', 'benchmarks.views.tool_upload'),
	# Page to test a regular expression through AJAX
	(r'^regextester/$','benchmarks.views.test_regex'),
)

# static media: DEVELOPMENT ONLY!
if settings.DEBUG:
	urlpatterns += patterns('django.views.static',
	(r'^site_media/(?P<path>.*)$', 
		'serve', {
		'document_root': os.path.join(settings.SITE_ROOT, 'site_media'),
		'show_indexes': True }),)
